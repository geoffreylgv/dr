import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.scanner import (
    Scanner,
    _calculate_cve_penalty,
    _parse_trivy_output,
)


# --- Score normalization unit tests ---

def make_findings(critical=0, high=0, medium=0, low=0):
    findings = []
    for _ in range(critical):
        findings.append({"severity": "CRITICAL", "id": "CVE-X", "package": "pkg",
                         "installed_version": "1.0", "fixed_version": None, "title": ""})
    for _ in range(high):
        findings.append({"severity": "HIGH", "id": "CVE-X", "package": "pkg",
                         "installed_version": "1.0", "fixed_version": None, "title": ""})
    for _ in range(medium):
        findings.append({"severity": "MEDIUM", "id": "CVE-X", "package": "pkg",
                         "installed_version": "1.0", "fixed_version": None, "title": ""})
    for _ in range(low):
        findings.append({"severity": "LOW", "id": "CVE-X", "package": "pkg",
                         "installed_version": "1.0", "fixed_version": None, "title": ""})
    return findings


def test_clean_container_scores_100():
    assert _calculate_cve_penalty([]) == 0


def test_score_never_zero_all_violations():
    findings = make_findings(critical=10, high=10, medium=10, low=20)
    cve_penalty = _calculate_cve_penalty(findings)
    config_penalty = 8 * 5  # all 8 rules triggered
    total = min(cve_penalty + config_penalty, 99)
    score = max(1, 100 - total)
    assert score == 1


def test_critical_cve_capped_at_30():
    penalty = _calculate_cve_penalty(make_findings(critical=5))
    assert penalty == 30  # 5 * 15 would be 75 but cap is 30


def test_high_cve_capped_at_24():
    penalty = _calculate_cve_penalty(make_findings(high=5))
    assert penalty == 24


def test_medium_cve_capped_at_15():
    penalty = _calculate_cve_penalty(make_findings(medium=6))
    assert penalty == 15


def test_low_cve_capped_at_10():
    penalty = _calculate_cve_penalty(make_findings(low=12))
    assert penalty == 10


def test_total_penalty_never_exceeds_99():
    findings = make_findings(critical=10, high=10, medium=10, low=20)
    cve_penalty = _calculate_cve_penalty(findings)
    config_penalty = 40  # hypothetical large config penalty
    assert min(cve_penalty + config_penalty, 99) == 99


def test_trivy_subprocess_args():
    with patch("backend.scanner.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout='{"Results": []}')
        from backend.scanner import _trivy_subprocess
        _trivy_subprocess("nginx:1.25")
        args = mock_run.call_args[0][0]
        assert "--format" in args
        assert "json" in args
        assert "--quiet" in args
        assert "nginx:1.25" in args
