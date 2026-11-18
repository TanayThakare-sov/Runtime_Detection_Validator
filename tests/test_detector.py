from validator.detector import EventLog
from validator.rules import outbound_connection, shadow_read, shell_spawned


def test_wait_for_finds_event_written_after_mark(tmp_path):
    log_file = tmp_path / "events.log"
    log_file.write_text("OPEN|1|cat|/etc/shadow\n")  # old event, must be ignored
    log = EventLog(log_file)
    mark = log.mark()
    assert log.wait_for(shadow_read, since=mark, timeout=0.5) is None

    with open(log_file, "a") as f:
        f.write("OPEN|2|cat|/etc/shadow\n")
    assert log.wait_for(shadow_read, since=mark, timeout=1).pid == 2


def test_shell_rule_matches_token_only():
    log_events = ["EXEC|1|runc|/bin/sh|sh -c echo tok123"]
    from validator.events import parse_line
    e = parse_line(log_events[0])
    assert shell_spawned("tok123")(e)
    assert not shell_spawned("other")(e)


def test_connection_rule():
    from validator.events import parse_line
    e = parse_line("CONN|3|python|203.0.113.10|4444")
    assert outbound_connection("203.0.113.10", 4444)(e)
    assert not outbound_connection("203.0.113.10", 80)(e)


def test_missing_log_returns_none(tmp_path):
    log = EventLog(tmp_path / "nope.log")
    assert log.wait_for(shadow_read, since=0, timeout=0.3) is None
