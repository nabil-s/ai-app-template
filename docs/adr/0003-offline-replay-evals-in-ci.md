# 0003. Replay evals on every PR, live evals on demand

- **Status:** accepted
- **Date:** 2026-11-18

## Context
Evals must run in CI to catch regressions, but live model calls in CI are non-deterministic, need a
secret, and cost money on every push.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Live evals on every PR | Measures real quality | Cost, flakiness, secret exposure on fork PRs |
| No evals in CI | Free | Regressions ship silently |
| **Replay on every PR + live on `workflow_dispatch`** | Free, deterministic gate; real numbers when wanted | Replay doesn't measure model quality |

## Decision
CI replays recorded outputs (`evals/fixtures/recordings.json`) on every push/PR and fails below the
threshold. Live evals run only on manual dispatch with the `ANTHROPIC_API_KEY` repository secret.

## Consequences
Replay protects parsing, scoring and post-processing. README quality numbers must come from live
runs only, stating model, date and n. Re-record fixtures whenever the prompt or model changes.
