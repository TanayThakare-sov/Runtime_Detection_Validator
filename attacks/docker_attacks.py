"""Attack simulations. Each one runs a harmless command inside the target container."""
import subprocess


def _exec(container: str, *cmd: str, timeout: int = 20) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "exec", container, *cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def spawn_shell(container: str, token: str):
    """Simulates: attacker gets a shell inside a container (execve)."""
    return _exec(container, "sh", "-c", f"echo {token}")


def read_shadow(container: str):
    """Simulates: credential access by reading /etc/shadow (openat)."""
    return _exec(container, "cat", "/etc/shadow")


def outbound_connection(container: str, ip: str, port: int):
    """Simulates: unexpected outbound connection / C2 beacon (connect).

    Uses a TEST-NET address (RFC 5737) that never routes, so nothing real is contacted.
    """
    code = (
        "import socket;"
        "s=socket.socket();s.settimeout(2);"
        f"s.connect_ex(('{ip}',{port}))"
    )
    return _exec(container, "python", "-c", code)
