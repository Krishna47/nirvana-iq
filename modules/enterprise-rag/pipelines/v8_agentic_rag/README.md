# v8 — Agentic RAG

LangGraph loop: **retrieve → sufficiency check → re-retrieve → generate**.

Uses the shared **v3** hybrid collection and **v7** metadata filters on each
retrieve round (no new index).

## What failed before

One-shot retrieval (even hybrid / multi-query) can miss a second cause on
multi-hop questions — e.g. California laptop sales decline needs **promo end**
and **inventory below reorder**.

## What changed

- LangGraph `StateGraph` with retrieve / check / generate nodes
- Check returns JSON `{sufficient, reason, followup_query}`
- At most **2** retrieve rounds; merge/dedupe chunks (top 6) before generate
- Lab shows **Agent steps** for interview demos

## Status

Runnable.

## Tradeoff

Extra LLM check (+ optional second retrieve) raises latency/cost; better
multi-hop coverage. Distinct from v10 (answer self-critique).

## Interview talking points

1. Agents fix **coverage gaps**, not just ranking.
2. Bound the loop (max 1 retry) for operable demos.
3. Keep enterprise filters on every retrieve round.
