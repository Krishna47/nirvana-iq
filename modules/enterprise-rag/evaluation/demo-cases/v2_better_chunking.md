# Demo cases — v2 Better Chunking

Section-aware chunks with overlap. Same dense retrieve + generate as v1.

## Setup

```bash
python modules/enterprise-rag/cli.py index --version v2_better_chunking --recreate
```

Open Evolution Lab → select **V2**.

---

# A. Chunk boundary wins (vs v1)

### A1 — Intact promotion section

```text
When did the California laptop promotion end?
```

**✅ Expected:** Clear end date from a complete section (heading-prefixed chunk)

**🔍 Check in UI:**

* Retrieved chunks start at `##` / `###` headings
* Less mid-sentence truncation than v1

---

### A2 — Boundary fact (electronics return window)

```text
What is the electronics return window?
```

**✅ Expected:** `15 days` (or corpus-equivalent return window)

**🔍 Check in UI:** Fact and surrounding policy language in one section chunk

**Note:** Ranking can still miss the right doc — v4 rerank helps further.

---

# B. Still intentionally broken (later versions)

### B1 — Expired vs current California promo

```text
When did the California laptop promotion end?
```

**❌ Still possible:** Expired `status=expired` policy ranks in top-k

**✅ Fixed in:** V7 (metadata filters)

### B2 — Exact SKU / code match

Dense-only retrieval can still miss literal IDs.

**✅ Fixed in:** V3 (hybrid search)

---

# Interview talking points

1. v1 vs v2 is an **indexing** delta — same `TOP_K=4`, same generator.
2. Heading prefixes keep section context in the embedding and in the LLM context.
3. Overlap trades index size for fewer facts lost at chunk edges.
4. Point at the scorecard: citation hit / latency after `cli.py eval --version v2_better_chunking`.
