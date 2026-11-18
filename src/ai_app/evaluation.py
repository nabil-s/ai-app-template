"""Eval core: load a JSONL dataset, run the task, score it. CLI lives in evals/run_evals.py."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai_app.llm import LLMClient
from ai_app.task import classify


@dataclass(frozen=True)
class CaseResult:
    id: str
    expected: str
    actual: str

    @property
    def passed(self) -> bool:
        return self.expected == self.actual


def load_dataset(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run(dataset: list[dict], client: LLMClient) -> list[CaseResult]:
    return [CaseResult(c["id"], c["expected"], classify(c["input"], client)) for c in dataset]


def accuracy(results: list[CaseResult]) -> float:
    return sum(r.passed for r in results) / len(results) if results else 0.0
