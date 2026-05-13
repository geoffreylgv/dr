import asyncio
import json
import subprocess
from typing import Any

from .docker_client import DockerClient
from .rules import check_rules

_SCAN_SEMAPHORE = asyncio.Semaphore(2)

_CVE_PENALTIES = {
    "CRITICAL": (15, 30),
    "HIGH": (8, 24),
    "MEDIUM": (3, 15),
    "LOW": (1, 10),
}


class Scanner:
    def __init__(self, docker_client: DockerClient):
        self._docker = docker_client
        self._cache: dict[str, dict[str, Any]] = {}  # keyed by image digest

    async def scan_container(self, container_id: str) -> dict[str, Any]:
        inspect = await self._docker.inspect_container(container_id)

        # image_name sourced exclusively from docker inspect — never from user input
        image_tag = inspect["Config"]["Image"]
        digest = await self._docker.get_image_digest(image_tag)

        if digest in self._cache:
            cve_result = self._cache[digest]
        else:
            cve_result = await self._run_trivy(image_tag)
            self._cache[digest] = cve_result

        config_findings = check_rules(inspect)
        cve_findings = _parse_trivy_output(cve_result)

        cve_penalty = _calculate_cve_penalty(cve_findings)
        config_penalty = len(config_findings) * 5
        total_penalty = min(cve_penalty + config_penalty, 99)
        score = max(1, 100 - total_penalty)

        return {
            "container_id": container_id,
            "image": image_tag,
            "score": score,
            "cve_findings": cve_findings,
            "config_findings": config_findings,
            "breakdown": {
                "cve_penalty": cve_penalty,
                "config_penalty": config_penalty,
            },
        }

    async def _run_trivy(self, image_name: str) -> dict[str, Any]:
        async with _SCAN_SEMAPHORE:
            result = await asyncio.to_thread(
                _trivy_subprocess, image_name
            )
        return result

    async def update_trivy_db(self):
        """Background task: update Trivy DB without blocking startup."""
        try:
            await asyncio.to_thread(
                subprocess.run,
                ["trivy", "image", "--download-db-only", "--quiet"],
                check=True,
                capture_output=True,
            )
        except Exception:
            pass  # bundled DB remains in use; update failure is non-fatal


def _trivy_subprocess(image_name: str) -> dict[str, Any]:
    result = subprocess.run(
        ["trivy", "image", "--format", "json", "--quiet", image_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"Results": [], "error": result.stderr}
    return json.loads(result.stdout)


def _parse_trivy_output(raw: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    for result in raw.get("Results", []):
        for vuln in result.get("Vulnerabilities") or []:
            findings.append({
                "id": vuln.get("VulnerabilityID"),
                "severity": vuln.get("Severity", "UNKNOWN"),
                "package": vuln.get("PkgName"),
                "installed_version": vuln.get("InstalledVersion"),
                "fixed_version": vuln.get("FixedVersion"),
                "title": vuln.get("Title", ""),
            })
    return findings


def _calculate_cve_penalty(findings: list[dict[str, Any]]) -> int:
    counts: dict[str, int] = {}
    for f in findings:
        sev = f["severity"].upper()
        counts[sev] = counts.get(sev, 0) + 1

    total = 0
    for sev, (per_finding, cap) in _CVE_PENALTIES.items():
        count = counts.get(sev, 0)
        total += min(count * per_finding, cap)
    return total
