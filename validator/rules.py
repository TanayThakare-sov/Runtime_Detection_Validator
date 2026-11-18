"""Detection rules: what counts as 'the sensor caught this attack'."""
from validator.events import Event


def shell_spawned(token: str):
    """EXEC event whose argv contains our unique token."""
    return lambda e: e.kind == "EXEC" and token in e.extra


def shadow_read(e: Event) -> bool:
    """OPEN of /etc/shadow by `cat`."""
    return e.kind == "OPEN" and e.detail == "/etc/shadow" and e.comm == "cat"


def outbound_connection(ip: str, port: int):
    """CONN event to the given ip and port."""
    return lambda e: e.kind == "CONN" and e.detail == ip and e.extra == str(port)
