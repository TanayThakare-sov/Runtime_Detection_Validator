from validator.events import parse_line


def test_parse_exec():
    e = parse_line("EXEC|123|runc|/bin/sh|sh -c echo abc\n")
    assert e.kind == "EXEC" and e.pid == 123
    assert e.detail == "/bin/sh" and "abc" in e.extra


def test_parse_open():
    e = parse_line("OPEN|7|cat|/etc/shadow")
    assert e.kind == "OPEN" and e.comm == "cat" and e.detail == "/etc/shadow"


def test_parse_conn():
    e = parse_line("CONN|9|python|203.0.113.10|4444")
    assert e.detail == "203.0.113.10" and e.extra == "4444"


def test_garbage_is_ignored():
    assert parse_line("Attaching 3 probes...") is None
    assert parse_line("EXEC|notanumber|x|y|z") is None
    assert parse_line("") is None
