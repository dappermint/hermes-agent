"""Text-emitted tool calls are recovered when the server drops the tool_calls field."""

import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agent.acp_openai_bridge import extract_tool_calls_from_text


def _msg(content, tool_calls=None):
    return types.SimpleNamespace(content=content, tool_calls=tool_calls, finish_reason="stop")


def test_recovers_xml_block():
    m = _msg('here you go\n<tool_call>{"name": "read_file", "arguments": {"path": "/tmp/x"}}</tool_call>')
    calls, cleaned = extract_tool_calls_from_text(m.content)
    assert len(calls) == 1
    assert calls[0].function.name == "read_file"
    assert "<tool_call>" not in cleaned
    assert cleaned == "here you go"


def test_plain_text_is_untouched():
    calls, cleaned = extract_tool_calls_from_text("just a normal answer")
    assert calls == []
    assert cleaned == "just a normal answer"


if __name__ == "__main__":
    test_recovers_xml_block()
    test_plain_text_is_untouched()
    print("ok")
