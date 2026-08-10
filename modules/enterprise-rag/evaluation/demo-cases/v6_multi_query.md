# Demo cases — v6 Multi-query

LlamaIndex expands to multiple search queries → hybrid retrieve each on **v3** → client RRF → top-4 → generate.

## Setup

```bash
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
pip install -r modules/enterprise-rag/api/requirements.txt
```

Open Evolution Lab → select **V6**.

---

# A. Multi-angle coverage

### A1 — California sales decline (promo + inventory)

```text
Why did California laptop sales decline in April 2026?
```

**✅ Expected:** Promotion expired and/or inventory below reorder; sources among `NRG-RPT-SALES-010`, `NRG-RPT-INV-011`, `NRG-POL-SALES-001`, `NRG-POL-INV-003`.

**🔍 Check in UI:**

* **Expanded queries** panel lists ~3 phrasings (promo / inventory / region angles)
* Citations span more than one related document when possible

---

# B. Still intentionally broken (later versions)

### B1 — Expired vs current California promo

Multi-query does not filter `status=expired`.

**✅ Fixed in:** V7 (metadata filters)

---

# Interview talking points

1. v6 improves **recall coverage** via multiple phrasings; v5 is a single rewrite.
2. Client RRF merges ranked lists when raw scores are not comparable across queries.
3. Shares `nrg_gold_v3_hybrid_search` — no second index.
4. Point at the scorecard after `cli.py eval --version v6_multi_query`.
