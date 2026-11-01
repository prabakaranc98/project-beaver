"""Deliberately red, to prove a failing PR cannot merge (#28). Reverted in the next commit."""


def test_the_gate_holds():
    assert False, "planted failure"
