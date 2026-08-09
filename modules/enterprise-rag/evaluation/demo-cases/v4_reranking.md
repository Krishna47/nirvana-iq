# Demo cases — v4 Reranking

Hybrid N=20 from v3 → LLM listwise rerank → top-K=4 → generate.

## Setup

Requires the **v3** collection (no v4 index):

```bash
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
```

Open Evolution Lab → select **V4**.

---

# A. Ranking wins (vs hybrid top-4 alone)

### A1 — Return after 20 days (opened, non-defective)

```text
Can an opened non-defective laptop be returned after 20 days?
```

**✅ Expected:** No — electronics return window is 15 days (`NRG-POL-CX-004`)

**🔍 Check in UI:** Correct return-policy chunk ranks in top-k after rerank; answer is a clear refusal.

---

# B. Still intentionally broken (later versions)

### B1 — Expired vs current California promo

Rerank does not filter `status=expired`.

**✅ Fixed in:** V7 (metadata filters)

### B2 — Vague / paraphrase queries

Rerank helps precision among retrieved candidates; query rewrite / multi-query (v5/v6) help when the right doc never enters N=20.

---

# Interview talking points

1. v4 is a **query-time** delta — same hybrid recall as v3, reorders before generate.
2. Extra chat call trades latency/cost for better top-K precision on near-duplicates.
3. Shares `nrg_gold_v3_hybrid_search` — no second index to maintain.
4. Point at the scorecard after `cli.py eval --version v4_reranking`.
