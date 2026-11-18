# Evals

| File | Purpose |
|---|---|
| `dataset.jsonl` | Cases: `{"id", "input", "expected"}`. Version it; never edit cases to make a score go up. |
| `fixtures/recordings.json` | Recorded model outputs for replay mode. |
| `run_evals.py` | Runner. Exits non-zero below `--threshold`. |
| `results/latest.json` | Last run's summary (committed so the README number is traceable). |

```bash
uv run python evals/run_evals.py                          # replay: free, what CI runs on every PR
LLM_PROVIDER=ollama uv run python evals/run_evals.py --mode live --record      # free, local model
LLM_PROVIDER=anthropic uv run python evals/run_evals.py --mode live            # paid
```

Replay mode tests the scoring pipeline and catches regressions in parsing/post-processing.
It does **not** measure model quality. Only live-mode numbers go in the README. See `docs/adr/0003`.
