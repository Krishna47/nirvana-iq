# Demo cases — v5 Query Rewrite

LlamaIndex rewrites the question, then hybrid retrieves from the **v3** collection (top-4). No new index.

## Setup

```bash
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
pip install -r modules/enterprise-rag/api/requirements.txt
```

Open Evolution Lab → select **V5**.

---

# A. Vague / paraphrase wins

### A1 — Informal promo discount

```text
How much off laptops in CA for the big Q1 promo?
```

**✅ Expected:** ~12% discount from California laptop promotion (`NRG-POL-SALES-001`)

**🔍 Check in UI:**

* **Rewritten query** panel shows a clearer search string (California / laptop / promotion / discount) vs the raw slang question
* Citations include `NRG-POL-SALES-001`

---

# B. Still intentionally broken (later versions)

### B1 — Expired vs current California promo

Rewrite does not filter `status=expired`.

**✅ Fixed in:** V7 (metadata filters)

### B2 — Multi-angle coverage

A single rewrite may still miss alternate phrasings; multi-query fusion is **V6**.

---

# Interview talking points

1. v5 is the first ladder step that uses **LlamaIndex** — for rewrite only; Qdrant stays hybrid.
2. Rewritten **text** feeds both dense and BM25 (unlike HyDE’s dense-only hypothetical embedding).
3. Shares `nrg_gold_v3_hybrid_search` — no second index.
4. Point at the scorecard after `cli.py eval --version v5_query_rewrite`.
