# Demo cases — v3 Hybrid Search

Dense OpenAI + BM25 sparse fused with Qdrant RRF. Section chunks inherited from v2.

## Setup

```bash
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
```

Open Evolution Lab → select **V3**.

---

# A. Exact-match wins (vs dense-only)

### A1 — Below-reorder SKU

```text
Which SKU is called out as below reorder in the April 2026 inventory risk report?
```

**✅ Expected:** `NRG-LAP-1001` (cite `NRG-RPT-INV-011`)

**🔍 Check in UI:** Retrieved chunks contain the literal SKU; BM25 helps surface the inventory report.

---

### A2 — Flagship catalog SKU

```text
What is the flagship SKU in the laptop product catalog?
```

**✅ Expected:** `NRG-LAP-1002` (cite `NRG-CAT-PROD-012`)

**🔍 Check in UI:** Catalog chunk ranks in top-k despite many other docs mentioning laptop SKUs.

---

# B. Still intentionally broken (later versions)

### B1 — Expired vs current California promo

Dense+BM25 can still rank expired policy text highly.

**✅ Fixed in:** V7 (metadata filters)

### B2 — Boundary ranking / precision

Hybrid improves recall of exact tokens; hard ranking among near-duplicates is still a v4 rerank story.

---

# Interview talking points

1. v3 is a **retrieval** delta — same section chunks as v2, same generator, dual Qdrant channels + RRF.
2. Dense alone struggles with identifiers; BM25 ranks literal `NRG-LAP-*` tokens.
3. Tradeoff: FastEmbed at index/query time and a larger collection schema.
4. Point at the scorecard after `cli.py eval --version v3_hybrid_search`.
