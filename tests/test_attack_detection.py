"""Integration tests: attack inside a container, assert the eBPF sensor saw it.

Needs: Linux, Docker, and the sensor running (make sensor).
"""
import uuid

import pytest

from attacks import docker_attacks as attacks
from validator import rules

pytestmark = pytest.mark.integration

C2_IP, C2_PORT = "203.0.113.10", 4444  # TEST-NET-3, never routable


def test_sensor_is_running(event_log):
    ready = event_log.wait_for(lambda e: e.kind == "READY", since=0, timeout=2)
    assert ready is not None, "Sensor did not write its READY line"


def test_shell_spawn_detected(event_log, target_container):
    token = uuid.uuid4().hex[:8]
    mark = event_log.mark()
    attacks.spawn_shell(target_container, token)
    assert event_log.wait_for(rules.shell_spawned(token), since=mark), "execve not detected"


def test_shadow_read_detected(event_log, target_container):
    mark = event_log.mark()
    attacks.read_shadow(target_container)
    assert event_log.wait_for(rules.shadow_read, since=mark), "/etc/shadow read not detected"


def test_outbound_connection_detected(event_log, target_container):
    mark = event_log.mark()
    attacks.outbound_connection(target_container, C2_IP, C2_PORT)
    assert event_log.wait_for(
        rules.outbound_connection(C2_IP, C2_PORT), since=mark
    ), "connect() not detected"
