# 0001. Record architecture decisions

- **Status:** accepted
- **Date:** 2026-11-18

## Context
Each app in this portfolio exists to show design judgment. Judgment is only visible if the
alternatives and trade-offs are written down at the time the decision is made.

## Decision
Every significant decision (model choice, retrieval strategy, storage, eval method, anything that
trades cost against quality or latency) gets a short ADR in `docs/adr/`, numbered sequentially,
using `0000-template.md`. The README links each ADR in its "Design decisions" table.

## Consequences
A few minutes of writing per decision. Superseded ADRs are kept and marked, not deleted.
