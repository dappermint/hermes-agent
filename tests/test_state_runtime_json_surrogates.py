from hermes_state_runtime import _json


def test_lone_surrogate_replaced_and_pair_rejoined():
    out = _json({"a": "hi \ud83c", "b": "\ud83c\udf89"})
    out.encode("utf-8")
    assert "\ufffd" in out
    assert "\U0001f389" in out
