import os
import shutil
import subprocess
from pathlib import Path

import pytest

from validator.detector import EventLog

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "rdv-target:latest"
NAME = "rdv-target"


@pytest.fixture(scope="session")
def event_log():
    path = Path(os.environ.get("EVENT_LOG", ROOT / "logs" / "events.log"))
    if not path.exists():
        pytest.skip("No event log. Start the sensor first: make sensor")
    return EventLog(path)


@pytest.fixture(scope="session")
def target_container():
    if shutil.which("docker") is None:
        pytest.skip("Docker not installed")
    subprocess.run(
        ["docker", "build", "-t", IMAGE, "-f", str(ROOT / "Dockerfile.target"), str(ROOT)],
        check=True,
        capture_output=True,
    )
    subprocess.run(["docker", "rm", "-f", NAME], capture_output=True)
    subprocess.run(["docker", "run", "-d", "--name", NAME, IMAGE], check=True, capture_output=True)
    yield NAME
    subprocess.run(["docker", "rm", "-f", NAME], capture_output=True)
