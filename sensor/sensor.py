"""Runs the bpftrace sensor and appends every event line to logs/events.log.

Must be run as root:  sudo python3 sensor/sensor.py
Stop with Ctrl+C.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "sensor" / "tracer.bt"
LOG = Path(os.environ.get("EVENT_LOG", ROOT / "logs" / "events.log"))


def main() -> int:
    if os.geteuid() != 0:
        print("Run as root: sudo python3 sensor/sensor.py", file=sys.stderr)
        return 1
    if shutil.which("bpftrace") is None:
        print("bpftrace not found. Install it: sudo apt install bpftrace", file=sys.stderr)
        return 1

    LOG.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        ["bpftrace", str(SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    print(f"Sensor running, writing events to {LOG}")
    try:
        with open(LOG, "a", buffering=1) as out:
            for line in proc.stdout:
                out.write(line)
                out.flush()
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
