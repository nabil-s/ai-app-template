"""Run evals.

  replay (default, CI on every PR): recorded outputs, free, deterministic.
  live: calls the configured LLM_PROVIDER; add --record to refresh the recordings.

Exits non-zero if accuracy is below --threshold, so CI fails on regressions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ai_app.evaluation import accuracy, load_dataset, run
from ai_app.llm import ReplayClient, get_client

HERE = Path(__file__).parent
DATASET = HERE / "dataset.jsonl"
RECORDINGS = HERE / "fixtures" / "recordings.json"
RESULTS = HERE / "results" / "latest.json"


class _Recorder:
    def __init__(self, inner):
        self.inner, self.seen = inner, {}

    def complete(self, prompt, system=None):
        response = self.inner.complete(prompt, system)
        self.seen[prompt] = response.text
        return response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["replay", "live"], default="replay")
    parser.add_argument("--record", action="store_true", help="live mode: save outputs as fixtures")
    parser.add_argument("--threshold", type=float, default=0.8)
    args = parser.parse_args()

    dataset = load_dataset(DATASET)
    if args.mode == "replay":
        client = ReplayClient(json.loads(RECORDINGS.read_text(encoding="utf-8")))
    else:
        client = _Recorder(get_client())

    results = run(dataset, client)
    score = accuracy(results)

    if args.mode == "live" and args.record:
        RECORDINGS.write_text(json.dumps(client.seen, indent=2) + "\n", encoding="utf-8")

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(
        json.dumps({"mode": args.mode, "accuracy": score, "n": len(results)}, indent=2) + "\n",
        encoding="utf-8",
    )

    print("| case | expected | actual | pass |\n|---|---|---|---|")
    for r in results:
        print(f"| {r.id} | {r.expected} | {r.actual} | {'yes' if r.passed else 'NO'} |")
    summary = f"n={len(results)}, mode={args.mode}, threshold={args.threshold:.0%}"
    print(f"\naccuracy={score:.2%} ({summary})")
    return 0 if score >= args.threshold else 1


if __name__ == "__main__":
    sys.exit(main())
