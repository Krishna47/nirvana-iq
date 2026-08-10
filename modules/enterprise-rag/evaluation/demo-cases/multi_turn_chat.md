# Demo — Multi-turn Lab chat

True multi-turn: follow-ups condense into a standalone retrieval query, then generate with conversation history.

## Setup

Index a runnable version (example v2):

```bash
python modules/enterprise-rag/cli.py index --version v2_better_chunking --recreate
```

Open Evolution Lab → select that version → keep the chat thread open. Switching versions preserves each version’s thread; Clear chat appears only after the first ask.

---

# A. Follow-up needs condensation

### A1 — Promo then return window

**Turn 1**

```text
When did the California laptop promotion end?
```

**✅ Expected:** End date from the CA laptop promo policy; citations include the sales policy id.

**Turn 2 (follow-up)**

```text
What about the electronics return window for that?
```

**✅ Expected:**

* Metrics → **Search query** is a standalone rewrite (mentions California / laptop / return window), not the raw pronoun question alone.
* Answer cites the customer return / electronics window (e.g. 15 days) from retrieved chunks.
* Without condensation, dense search on “What about the electronics return window for that?” would often miss the right policy.

---

# B. Interview talking points

1. History in the UI is not enough — retrieval must see a rewritten query.
2. `search_query` in Metrics proves condensation for the audience.
3. Compare view stays single-question so version A/B tests stay fair.
