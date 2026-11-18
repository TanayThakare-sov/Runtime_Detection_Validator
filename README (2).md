# Runtime Detection Validator

**An automated test framework that attacks a Docker container on purpose and verifies that an eBPF-based sensor detected each attack.**

I built this to learn how runtime security sensors are validated. A sensor that silently misses events is worse than no sensor, so every detection here is backed by an automated test with a clear pass or fail.

> **Demo:** run the quick start below. With the sensor stopped the integration tests fail; with it running, all four pass.

---

## Skills demonstrated

| Skill | Where it appears in this project |
|---|---|
| Python automation for security testing | Attack simulations, event parser, detection rules, pytest suite |
| eBPF / kernel-level observability | `sensor/tracer.bt` (bpftrace) hooks `execve`, `openat`, `connect` |
| Linux fundamentals | Syscalls, processes, file permissions, namespaces, root privileges |
| Networking | Outbound connection detection (destination IP and port) |
| Docker / containers | Victim container, `docker exec` based attack simulation |
| CI/CD | GitHub Actions: lint, unit tests, integration tests |
| Test design | Unit vs integration split, unique tokens, log offsets to avoid false passes |

---

## What it does

| Attack simulated inside the container | Syscall observed by eBPF | Test |
|---|---|---|
| Shell spawned (`sh -c ...`) | `execve` | `test_shell_spawn_detected` |
| Credential file read (`cat /etc/shadow`) | `openat` | `test_shadow_read_detected` |
| Unexpected outbound connection | `connect` | `test_outbound_connection_detected` |

Each test follows the same pattern:

1. **Mark** the current end of the sensor's event log
2. **Run** the attack inside the container
3. **Wait** for a matching event (with a timeout)
4. **Assert** it was detected, otherwise fail with a clear message

Marking the log first means a test only sees events from its own attack, so old events can never cause a false pass.

## Architecture

```
pytest ──► attacks/ (docker exec) ──► target container
   │                                        │ syscalls
   │                                        ▼
   │                          sensor/tracer.bt (bpftrace, eBPF)
   │                                        │ event lines
   │                                        ▼
   └──────► validator/ ◄──────────── logs/events.log
        (parse, match rules, assert)
```

## Project structure

```
├── sensor/        eBPF tracer (tracer.bt) and runner (sensor.py)
├── attacks/       attack simulations
├── validator/     event parser, log reader, detection rules
├── tests/         unit tests + integration tests
├── docs/          concepts and learning log
└── .github/       CI workflow
```

## Quick start

**Requirements:** Linux (native, VM, or WSL2 with a recent kernel), Docker, `bpftrace`, Python 3.10+

```bash
git clone https://github.com/YOUR-USERNAME/runtime-detection-validator.git
cd runtime-detection-validator
make setup && source .venv/bin/activate

make unit            # unit tests, no eBPF needed

# Terminal 1: start the sensor (needs root)
make sensor

# Terminal 2: run attacks and validate detection
make integration
```

To watch what the sensor captures live: `tail -f logs/events.log`

**Expected output when everything works**

```
tests/test_attack_detection.py::test_sensor_is_running PASSED
tests/test_attack_detection.py::test_shell_spawn_detected PASSED
tests/test_attack_detection.py::test_shadow_read_detected PASSED
tests/test_attack_detection.py::test_outbound_connection_detected PASSED
```

## Design decisions

- **bpftrace over raw BCC/libbpf:** fastest way to express a syscall hook while learning, and easy to read in a review.
- **Filtering `openat` inside the eBPF program:** logging every file open on the host would flood the log, so only sensitive paths are emitted.
- **Unique token per shell test:** the sensor is host-wide, so the test matches on a random token in the command line to be sure it is detecting its own attack.
- **TEST-NET address for the connection test:** `203.0.113.10` (RFC 5737) never routes, so the simulation is harmless.
- **Unit and integration tests are separated:** parsing and matching logic is tested anywhere; only the eBPF tests need Linux, Docker and root.

## Known limitations

I would rather state these than hide them:

- The sensor sees the whole host, not one container. Tests narrow matches using tokens, process names and destinations.
- Only IPv4 `connect` events are captured.
- Events are passed through a log file and polled, which is fine for a lab but is not how a production pipeline works.
- The integration job in CI is allowed to fail, because eBPF permissions on hosted runners can vary.

## Challenges and how I solved them

1. **The sensor sees the whole host, not one container.**
   A host-wide `execve` hook also fires for unrelated processes, which could make a test pass for the wrong reason.
   *Solution:* each test matches something unique to its own attack: a random token in the shell command, the process name and path for the `/etc/shadow` read, and the destination IP and port for the connection.

2. **Old events causing false passes.**
   If a test just searched the whole log, an event from a previous run could satisfy it even when the sensor was broken.
   *Solution:* `EventLog.mark()` records the log position before the attack, and the test only reads events written after it.

3. **`openat` flooded the log.**
   Hooking every file open on a Linux host produces thousands of events per second.
   *Solution:* the filter lives inside the eBPF program, so only opens of `/etc/shadow` and `/etc/passwd` are emitted.

4. **Attack simulations must be safe and repeatable.**
   *Solution:* the connection test targets `203.0.113.10` (RFC 5737 TEST-NET-3), which never routes, so nothing real is contacted. The target container is created and removed by a pytest fixture, so every run starts clean.

5. **Tests that need root and eBPF should not block everyone else.**
   *Solution:* tests are split with a `pytest` marker. Unit tests run anywhere (including CI); integration tests run only where the sensor is available and skip with a clear message otherwise.

## What I learned

- How eBPF lets a program observe kernel events such as `execve`, `openat` and `connect` without changing the kernel, and why that suits security tooling.
- That validating a detection means proving both that it fires on the attack and that it does not pass by accident.
- How containers share the host kernel, which is why a host-level sensor can see container activity.
- How to structure a project so the logic is unit-testable and only the environment-dependent part needs root and Docker.
- How to wire lint, unit tests and integration tests into GitHub Actions.

## Roadmap

- [ ] Detect more behaviors (`chmod`, writes to `/etc/cron.d`, `ptrace`)
- [ ] Attribute events to a specific container using cgroup IDs
- [ ] Run the sensor as a Kubernetes DaemonSet (kind)
- [ ] Provision a cloud host with Terraform (AWS EC2)
- [ ] Export results to Prometheus and a Grafana dashboard

## License

MIT
