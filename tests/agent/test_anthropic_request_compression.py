import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import httpx
from agent.anthropic_adapter import build_anthropic_client


def _run_test_client(client, payload):
    captured = {}

    def capture_transport(request: httpx.Request) -> httpx.Response:
        captured["headers"] = dict(request.headers)
        captured["body"] = request.read()
        return httpx.Response(status_code=401, json={"error": "mock"}, request=request)

    client._client._transport = httpx.MockTransport(capture_transport)
    try:
        client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": payload}],
        )
    except Exception:
        pass
    return captured


def test_anthropic_large_request_gzipped():
    client = build_anthropic_client("sk-ant-test")
    payload = "long text " * 200
    captured = _run_test_client(client, payload)
    assert captured["headers"].get("content-encoding") == "gzip"
    assert int(captured["headers"]["content-length"]) == len(captured["body"])
    assert payload in gzip.decompress(captured["body"]).decode()


def test_anthropic_small_request_uncompressed():
    client = build_anthropic_client("sk-ant-test")
    captured = _run_test_client(client, "hi")
    assert "content-encoding" not in captured["headers"]


def test_anthropic_third_party_endpoint_uncompressed():
    client = build_anthropic_client("sk-ant-test", base_url="https://openrouter.ai/api/v1")
    captured = _run_test_client(client, "long text " * 200)
    assert "content-encoding" not in captured["headers"]


def test_anthropic_gzip_opt_out(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_GZIP_REQUEST_BODIES", "0")
    client = build_anthropic_client("sk-ant-test")
    captured = _run_test_client(client, "long text " * 200)
    assert "content-encoding" not in captured["headers"]


if __name__ == "__main__":
    test_anthropic_large_request_gzipped()
    test_anthropic_small_request_uncompressed()
    test_anthropic_third_party_endpoint_uncompressed()
    class DummyMonkeypatch:
        def setenv(self, k, v):
            os.environ[k] = v
    test_anthropic_gzip_opt_out(DummyMonkeypatch())
    os.environ.pop("CLAUDE_CODE_GZIP_REQUEST_BODIES", None)
    print("all anthropic request compression tests passed.")
