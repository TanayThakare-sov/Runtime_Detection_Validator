"""Read the sensor's event log and wait for specific events."""
import time
from collections.abc import Callable
from pathlib import Path

from validator.events import Event, parse_line


class EventLog:
    def __init__(self, path):
        self.path = Path(path)

    def mark(self) -> int:
        """Current end of the log. Events after this point belong to the next attack."""
        return self.path.stat().st_size if self.path.exists() else 0

    def read_since(self, offset: int) -> list[Event]:
        if not self.path.exists():
            return []
        with open(self.path, "rb") as f:
            f.seek(offset)
            text = f.read().decode(errors="replace")
        events = (parse_line(line) for line in text.splitlines())
        return [e for e in events if e is not None]

    def wait_for(
        self,
        predicate: Callable[[Event], bool],
        since: int,
        timeout: float = 10.0,
        interval: float = 0.25,
    ):
        """Poll until an event matches predicate. Returns the Event or None on timeout."""
        deadline = time.monotonic() + timeout
        while True:
            for event in self.read_since(since):
                if predicate(event):
                    return event
            if time.monotonic() >= deadline:
                return None
            time.sleep(interval)
