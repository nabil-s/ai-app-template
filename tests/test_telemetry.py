from ai_app.llm import LLMResponse
from ai_app.telemetry import cost_usd, log_call, summarize


def test_cost_known_and_unknown_models():
    assert cost_usd("claude-haiku-5-5", 1_000_000, 1_000_000) == 0.60
    assert cost_usd("llama3.2:3b", 10_000, 10_000) == 0.0


def test_log_and_summarize(tmp_path):
    path = tmp_path / "calls.jsonl"
    for ms in (100.0, 200.0, 300.0):
        log_call(LLMResponse("x", "anthropic", "claude-haiku-5-5", 1000, 100, ms), path)
    summary = summarize(path)
    assert summary["requests"] == 3
    assert summary["p50_latency_ms"] == 200.0
    assert abs(summary["mean_cost_usd"] - 0.00015) < 1e-12
