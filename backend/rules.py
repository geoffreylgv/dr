from typing import Any


_DB_PORTS = {5432, 3306, 27017, 6379, 5984, 9200, 1521}


def check_rules(inspect: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    hc = inspect.get("HostConfig", {})
    cfg = inspect.get("Config", {})

    _check_exposed_db_port(hc, findings)
    _check_no_memory_limit(hc, findings)
    _check_privileged(hc, findings)
    _check_root_user(cfg, findings)
    _check_no_restart_policy(hc, findings)
    _check_no_healthcheck(cfg, findings)
    _check_latest_tag(cfg, findings)
    _check_docker_sock_mount(hc, findings)

    return findings


def _check_exposed_db_port(hc: dict, findings: list):
    for container_port, bindings in (hc.get("PortBindings") or {}).items():
        try:
            port_num = int(container_port.split("/")[0])
        except ValueError:
            continue
        if port_num not in _DB_PORTS:
            continue
        for binding in (bindings or []):
            host_ip = binding.get("HostIp", "")
            if host_ip in ("", "0.0.0.0"):
                findings.append({
                    "rule": "exposed_db_port",
                    "severity": "HIGH",
                    "message": f"Database port {port_num} exposed on 0.0.0.0",
                    "fix_yaml": f'ports:\n  - "127.0.0.1:{port_num}:{port_num}"',
                })


def _check_no_memory_limit(hc: dict, findings: list):
    if hc.get("Memory", 0) == 0:
        findings.append({
            "rule": "no_memory_limit",
            "severity": "MEDIUM",
            "message": "No memory limit set — container can consume all host RAM",
            "fix_yaml": "deploy:\n  resources:\n    limits:\n      memory: 512M",
        })


def _check_privileged(hc: dict, findings: list):
    if hc.get("Privileged"):
        findings.append({
            "rule": "privileged_mode",
            "severity": "CRITICAL",
            "message": "Container running in privileged mode — full host access",
            "fix_yaml": "# Remove privileged: true from your compose service",
        })


def _check_root_user(cfg: dict, findings: list):
    user = cfg.get("User", "")
    if user in ("", "0", "root"):
        findings.append({
            "rule": "running_as_root",
            "severity": "HIGH",
            "message": "Container running as root (or no user set)",
            "fix_yaml": 'user: "1000:1000"',
        })


def _check_no_restart_policy(hc: dict, findings: list):
    policy = (hc.get("RestartPolicy") or {}).get("Name", "no")
    if policy == "no":
        findings.append({
            "rule": "no_restart_policy",
            "severity": "LOW",
            "message": "No restart policy — container will not recover from crashes",
            "fix_yaml": "restart: unless-stopped",
        })


def _check_no_healthcheck(cfg: dict, findings: list):
    if cfg.get("Healthcheck") is None:
        findings.append({
            "rule": "no_healthcheck",
            "severity": "LOW",
            "message": "No healthcheck defined — Docker cannot detect unhealthy state",
            "fix_yaml": (
                "healthcheck:\n"
                "  test: [\"CMD\", \"curl\", \"-f\", \"http://localhost/health\"]\n"
                "  interval: 30s\n"
                "  timeout: 10s\n"
                "  retries: 3"
            ),
        })


def _check_latest_tag(cfg: dict, findings: list):
    image = cfg.get("Image", "")
    if image.endswith(":latest") or (":" not in image):
        findings.append({
            "rule": "unpinned_image",
            "severity": "MEDIUM",
            "message": f"Image '{image}' uses :latest or no tag — not reproducible",
            "fix_yaml": f"# Pin to a specific digest, e.g.:\nimage: {image.split(':')[0]}:1.25.3",
        })


def _check_docker_sock_mount(hc: dict, findings: list):
    binds = hc.get("Binds") or []
    for bind in binds:
        if "/var/run/docker.sock" in bind:
            findings.append({
                "rule": "docker_sock_mounted",
                "severity": "CRITICAL",
                "message": "Docker socket mounted — container has full Docker host access",
                "fix_yaml": (
                    "# No safe automatic fix. If this is intentional (e.g. Docker Doctor itself),\n"
                    "# add a read-only flag where possible:\n"
                    "volumes:\n  - /var/run/docker.sock:/var/run/docker.sock:ro"
                ),
            })
            break
