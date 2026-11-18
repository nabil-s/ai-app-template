import pytest

from ai_app.evaluation import accuracy, run
from ai_app.llm import ReplayClient, get_client
from ai_app.task import classify


@pytest.fixture(autouse=True)
def _isolated_telemetry(tmp_path, monkeypatch):
    monkeypatch.setenv("TELEMETRY_PATH", str(tmp_path / "calls.jsonl"))


def test_classify_normalises_model_output():
    client = ReplayClient({"great": "  Positive.\n", "meh": "I'd say neutral", "??": "banana"})
    assert classify("great", client) == "positive"
    assert classify("meh", client) == "neutral"
    assert classify("??", client) == "unknown"


def test_run_and_accuracy():
    dataset = [
        {"id": "a", "input": "good", "expected": "positive"},
        {"id": "b", "input": "bad", "expected": "negative"},
    ]
    results = run(dataset, ReplayClient({"good": "positive", "bad": "positive"}))
    assert accuracy(results) == 0.5


def test_replay_missing_prompt_is_loud():
    with pytest.raises(KeyError):
        ReplayClient({}).complete("unseen")


def test_unknown_provider_rejected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nope")
    with pytest.raises(ValueError):
        get_client()
