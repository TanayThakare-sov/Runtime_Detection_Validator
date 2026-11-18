"""Parse sensor output lines into Event objects."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    kind: str       # EXEC, OPEN, CONN, READY
    pid: int
    comm: str       # process name
    detail: str     # EXEC: filename | OPEN: path | CONN: ip
    extra: str = ""  # EXEC: argv | CONN: port


def parse_line(line: str) -> Event | None:
    """Return an Event, or None if the line is not a valid event."""
    line = line.rstrip("\n")
    parts = line.split("|", 4)
    if len(parts) < 4 or parts[0] not in {"EXEC", "OPEN", "CONN", "READY"}:
        return None
    kind, pid, comm, detail = parts[0], parts[1], parts[2], parts[3]
    extra = parts[4] if len(parts) == 5 else ""
    try:
        pid_int = int(pid)
    except ValueError:
        return None
    return Event(kind, pid_int, comm, detail, extra)
