"""Per-request cost and latency logging (JSONL) plus a summary for the README.

Run `uv run python -m ai_app.telemetry` to print the numbers for the
"Cost per request" section. Never fill that section by hand.
"""

from __future__ import annotations

import json
import os
import statistics
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# USD per 1M tokens (input, output). Anthropic first-party rates as of 2026-11-03 -
# re-check https://platform.claude.com/docs/en/about-claude/pricing before publishing numbers.
# Haiku 5.5 rate applies to prompts up to 100K tokens.
PRICING_PER_MTOK: dict[str, tuple[float, float]] = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Unknown models (local Ollama, replay) cost 0."""
    in_rate, out_rate = PRICING_PER_MTOK.get(model, (0.0, 0.0))
    return (input_tokens * in_rate + output_tokens * out_rate) / 1_000_000


def _log_path() -> Path:
    return Path(os.environ.get("TELEMETRY_PATH", ".telemetry/calls.jsonl"))


def log_call(response: Any, path: Path | None = None) -> None:
    path = path or _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = asdict(response) if is_dataclass(response) else dict(response)
    record["cost_usd"] = cost_usd(record["model"], record["input_tokens"], record["output_tokens"])
    record["ts"] = datetime.now(UTC).isoformat()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def summarize(path: Path | None = None) -> dict[str, float]:
    path = path or _log_path()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not rows:
        return {"requests": 0}
    latencies = sorted(r["latency_ms"] for r in rows)
    costs = [r["cost_usd"] for r in rows]
    return {
        "requests": len(rows),
        "mean_cost_usd": statistics.fmean(costs),
        "total_cost_usd": sum(costs),
        "p50_latency_ms": statistics.median(latencies),
        "p95_latency_ms": latencies[min(len(latencies) - 1, int(0.95 * len(latencies)))],
    }


if __name__ == "__main__":
    for key, value in summarize().items():
        print(f"{key}: {value:.6f}" if isinstance(value, float) else f"{key}: {value}")
