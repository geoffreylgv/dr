import pytest
from backend.rules import check_rules


def base_inspect(**overrides):
    data = {
        "HostConfig": {
            "PortBindings": {},
            "Memory": 536870912,  # 512MB — has a limit
            "Privileged": False,
            "RestartPolicy": {"Name": "unless-stopped"},
            "Binds": [],
        },
        "Config": {
            "User": "1000",
            "Healthcheck": {"Test": ["CMD", "curl", "-f", "http://localhost/health"]},
            "Image": "nginx:1.25",
        },
    }
    for key, val in overrides.items():
        section, field = key.split(".", 1)
        data[section][field] = val
    return data


def rule_ids(findings):
    return [f["rule"] for f in findings]


def test_clean_container_no_findings():
    assert check_rules(base_inspect()) == []


def test_exposed_db_port_detected():
    inspect = base_inspect(**{"HostConfig.PortBindings": {
        "5432/tcp": [{"HostIp": "0.0.0.0", "HostPort": "5432"}]
    }})
    ids = rule_ids(check_rules(inspect))
    assert "exposed_db_port" in ids


def test_exposed_db_port_localhost_is_fine():
    inspect = base_inspect(**{"HostConfig.PortBindings": {
        "5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": "5432"}]
    }})
    assert check_rules(inspect) == []


def test_no_memory_limit_detected():
    inspect = base_inspect(**{"HostConfig.Memory": 0})
    ids = rule_ids(check_rules(inspect))
    assert "no_memory_limit" in ids


def test_privileged_detected():
    inspect = base_inspect(**{"HostConfig.Privileged": True})
    ids = rule_ids(check_rules(inspect))
    assert "privileged_mode" in ids


def test_root_user_detected():
    inspect = base_inspect(**{"Config.User": "root"})
    ids = rule_ids(check_rules(inspect))
    assert "running_as_root" in ids


def test_empty_user_detected_as_root():
    inspect = base_inspect(**{"Config.User": ""})
    ids = rule_ids(check_rules(inspect))
    assert "running_as_root" in ids


def test_no_restart_policy_detected():
    inspect = base_inspect(**{"HostConfig.RestartPolicy": {"Name": "no"}})
    ids = rule_ids(check_rules(inspect))
    assert "no_restart_policy" in ids


def test_no_healthcheck_detected():
    inspect = base_inspect(**{"Config.Healthcheck": None})
    ids = rule_ids(check_rules(inspect))
    assert "no_healthcheck" in ids


def test_latest_tag_detected():
    inspect = base_inspect(**{"Config.Image": "nginx:latest"})
    ids = rule_ids(check_rules(inspect))
    assert "unpinned_image" in ids


def test_no_tag_detected():
    inspect = base_inspect(**{"Config.Image": "nginx"})
    ids = rule_ids(check_rules(inspect))
    assert "unpinned_image" in ids


def test_docker_sock_mount_detected():
    inspect = base_inspect(**{"HostConfig.Binds": ["/var/run/docker.sock:/var/run/docker.sock"]})
    ids = rule_ids(check_rules(inspect))
    assert "docker_sock_mounted" in ids


def test_all_findings_have_fix_yaml():
    # Trigger every rule
    inspect = {
        "HostConfig": {
            "PortBindings": {"5432/tcp": [{"HostIp": "0.0.0.0", "HostPort": "5432"}]},
            "Memory": 0,
            "Privileged": True,
            "RestartPolicy": {"Name": "no"},
            "Binds": ["/var/run/docker.sock:/var/run/docker.sock"],
        },
        "Config": {
            "User": "root",
            "Healthcheck": None,
            "Image": "nginx:latest",
        },
    }
    findings = check_rules(inspect)
    assert len(findings) == 8
    for f in findings:
        assert f.get("fix_yaml"), f"Rule {f['rule']} missing fix_yaml"
