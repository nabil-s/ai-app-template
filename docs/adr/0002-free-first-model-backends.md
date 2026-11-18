# 0002. Free-first model backends

- **Status:** accepted
- **Date:** 2026-11-18

## Context
Apps should be cheap to build, run and demo, but a paid frontier model must be one switch away so
quality and cost can be compared on the same eval set.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Paid API only | Best quality, simplest | Every run costs money; demos need a key |
| Local model only (Ollama) | Free, private, offline | Lower quality; needs local hardware; not in CI |
| **Local default + paid opt-in behind one interface** | Free by default; same evals compare both | Small abstraction to maintain |

## Decision
`LLM_PROVIDER=ollama` (default) or `anthropic`, behind `LLMClient.complete()`. The Anthropic backend
uses the official SDK, reads credentials only from the environment, defaults to `claude-haiku-5-5`
at low effort, and is an optional dependency (`uv sync --extra anthropic`).

## Consequences
Every app can report a cost/quality comparison between a free and a paid model. Revisit if an app
needs a feature only one backend has (tool use, structured outputs). Record that in the app's own ADR.
