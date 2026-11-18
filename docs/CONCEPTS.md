# Concepts to know (interview prep)

**eBPF**: lets you run small, verified programs inside the Linux kernel without changing kernel code. Used for observability and security because it sees every syscall with low overhead.

**bpftrace**: a high-level language for writing eBPF programs. `tracepoint:syscalls:sys_enter_execve` runs your block whenever any process calls execve.

**Syscalls used here**
- `execve`: start a program. A shell spawning in a container is suspicious.
- `openat`: open a file. Reading `/etc/shadow` means someone wants password hashes.
- `connect`: open an outbound network connection. Unexpected destinations can mean command-and-control.

**Containers vs VMs**: containers share the host kernel and are isolated with namespaces (what a process can see) and cgroups (what it can use). That is why a host-level eBPF sensor can see container activity.

**Why validate a sensor?** A sensor that silently misses events is worse than none. Tests turn "I think it detects X" into proof, and catch regressions.

**Why a log offset (`mark`)?** It makes each test look only at events produced after its own attack, so old events cannot cause false passes.

**Known limitations (be honest about these)**
- The sensor is host-wide, not per-container. Tests match by unique token, process name, or destination to avoid false matches.
- Only IPv4 `connect` is captured.
- Polling a log file is simple but not how a production pipeline works.

## Questions to practice
1. What does `execve` capture and why is it useful for security?
2. Walk me through one test end to end.
3. What if the test passes but the sensor actually missed the event?
4. How does a container differ from a VM?
5. Why did you filter `openat` in the eBPF script?
6. How would you make this detect only one container's activity?
7. How would you run this on Kubernetes? (DaemonSet)
8. What was the hardest bug you hit?
