# V1 Basic RAG — Demo Failure Cases

Use this guide with the **Lab UI** to clearly demonstrate where the V1 baseline performs well and where it breaks down.

---

## ✅ How to Use This Guide

1. Select **V1** in the Lab UI
2. Copy a question from any section below
3. Run the query
4. Compare the output with the **Expected Result** and **Typical V1 Failure**
5. Open the **Chunks** tab when instructed to inspect retrieval details

> **Note:** Exact wording may vary depending on the model. Focus on identifying failure patterns such as:
>
> * Incorrect dates
> * Expired content ranked first
> * Missing or irrelevant documents
> * Incomplete explanations
> * Fabricated answers

---

## ⚙️ V1 Pipeline Overview

* Fixed chunk size: **800 characters**
* **No overlap** between chunks
* Uses **dense-vector search (Qdrant only)**
* Retrieves **Top 4 chunks**
* **No metadata filtering**
* **No reranking**
* **No query rewriting or multi-query retrieval**
* Single retrieval → single generation

---

# A. Freshness & Metadata Failures

### 🚨 Why V1 Fails

V1 ignores metadata such as `status`, `dates`, and `region`. As a result, outdated or expired policies may rank higher than current ones.

---

### A1 — Promotion End Date (⭐ Star Demo)

```text
When did the California laptop promotion end?
```

**✅ Expected:** `2026-03-31` (current policy v2.0, status: approved)

**🔍 Check in UI:** Look at **Chunks** → identify expired file paths or status

**❌ Typical Failure:**

* Returns `2025-03-31`
* Retrieves expired file (e.g., `v1-expired.md`)

**✅ Fixed in:** V7 (Metadata filtering)

---

### A2 — Ambiguous Campaign Discount

```text
What discount applied during this California laptop campaign?
```

**✅ Expected:** `12%` (current campaign)

**🔍 Check in UI:** Mixed campaign versions in retrieved chunks

**❌ Typical Failure:**

* Returns `10%` (expired campaign)
* Mixes `10%` and `12%`

**✅ Fixed in:** V5 + V7

---

### A3 — Current Policy Status

```text
What is the status of the current California laptop promotion policy?
```

**✅ Expected:** `approved`

**🔍 Check in UI:** Expired and current chunks appear together

**❌ Typical Failure:**

* Returns `expired`
* Mentions both policies without prioritization

**✅ Fixed in:** V7

---

### A4 — Expired Campaign Trap

```text
What discount applied in the expired California laptop campaign?
```

**✅ Expected:** `10%`

**🔍 Check in UI:** Current policy chunks dominate ranking

**❌ Typical Failure:**

* Returns `12%` (ignores "expired" intent)

**✅ Fixed in:** V5 + V7

---

# B. Chunking Failures

### 🚨 Why V1 Fails

Fixed chunking splits content mid-sentence or section. Without overlap, important information may be fragmented or lost.

---

### B1 — Chunk Boundary Issue

```text
When did the California laptop promotion end?
```

**✅ Expected:** Clear answer from a complete section

**🔍 Check in UI:**

* Chunks start/end mid-sentence
* Same document appears fragmented

**❌ Typical Failure:**

* Incomplete or inconsistent answers

**✅ Fixed in:** V2 (Section-aware chunking)

---

### B2 — Boundary Fact Loss

```text
What is the electronics return window?
```

**✅ Expected:** `15 days`

**🔍 Check in UI:** Sentence split across chunks

**❌ Typical Failure:**

* Vague answer
* Wrong policy retrieved

**✅ Fixed in:** V2 + V4

---

# C. Dense-Only Retrieval Failures

### 🚨 Why V1 Fails

Dense embeddings struggle with exact matches like SKUs, IDs, and codes.

---

### C1 — Exact SKU

```text
Which SKU is called out as below reorder in the April 2026 inventory risk report?
```

**✅ Expected:** `NRG-LAP-1001`

**🔍 Check in UI:** Correct report retrieval

**❌ Typical Failure:**

* Wrong SKU
* Generic inventory answer

**✅ Fixed in:** V3 (Hybrid search)

---

### C2 — Catalog SKU Confusion

```text
What is the flagship SKU in the laptop product catalog?
```

**✅ Expected:** `NRG-LAP-1002`

**🔍 Check in UI:** SKU confusion

**❌ Typical Failure:**

* Mixes similar SKUs
* Retrieves wrong document

**✅ Fixed in:** V3 + V4

---

### C3 — Document ID Query

```text
What does document NRG-POL-INV-003 say the laptop reorder point is?
```

**✅ Expected:** `100 sellable units`

**🔍 Check in UI:** Document prioritization

**❌ Typical Failure:**

* Ignores document ID
* Returns similar but incorrect info

**✅ Fixed in:** V3 + V7

---

# D. No Reranking

### 🚨 Why V1 Fails

Top cosine matches are used directly without reordering relevance.

---

### D1 — Return Policy Edge Case

```text
Can an opened non-defective laptop be returned after 20 days?
```

**✅ Expected:** No (15-day limit)

**🔍 Check in UI:** Ranking order of chunks

**❌ Typical Failure:**

* "Yes" or "Maybe"
* Wrong document cited

**✅ Fixed in:** V4 (Reranking)

---

# E. No Query Rewrite / Multi-Query

### 🚨 Why V1 Fails

V1 uses only the original query without clarification or expansion.

---

### E1 — Vague Query

```text
What discount applied during this California laptop campaign?
```

**✅ Expected:** `12%`

**❌ Typical Failure:**

* Returns `10%` or mixed answers

**✅ Fixed in:** V5

---

### E2 — Paraphrase Drift

```text
How much off laptops in CA for the big Q1 promo?
```

**✅ Expected:** `12%`

**🔍 Check in UI:** Irrelevant documents retrieved

**❌ Typical Failure:**

* Misses policy
* Retrieves unrelated content

**✅ Fixed in:** V5 + V6

---

# F. Multi-Hop Failures

### 🚨 Why V1 Fails

Only one retrieval step → cannot combine multiple sources.

---

### F1 — Sales Decline (⭐ Star Demo)

```text
Why did California laptop sales decline in April 2026?
```

**✅ Expected:**
Sales declined due to:

* Promotion ending
* Inventory dropping below reorder point

**🔍 Check in UI:** Number of relevant documents retrieved

**❌ Typical Failure:**

* Only one cause identified
* Missing key documents

**📄 Ideal Sources:**

* NRG-RPT-SALES-010
* NRG-RPT-INV-011
* NRG-POL-SALES-001
* NRG-POL-INV-003

**✅ Fixed in:** V6 + V8

---

# G. Grounding & Generation Failures

### 🚨 Why V1 Fails

Weak enforcement of grounding → leads to hallucinations or ignoring conflicts.

---

### G1 — Conflicting Context

```text
When did the California laptop promotion end?
```

**✅ Expected:**

* Prefer current policy (`2026-03-31`)
* OR mention multiple versions

**🔍 Check in UI:** Conflicting chunks

**❌ Typical Failure:**

* Confidently returns wrong (expired) date

**✅ Fixed in:** V7 + V10

---

### G2 — Out-of-Scope Question

```text
What is Nirvana Retail's CEO bonus for 2026?
```

**✅ Expected:**

* Refusal / "Not available in corpus"

**🔍 Check in UI:** No relevant chunks (CEO *name* is in `NRG-MAN-HR-013`; CEO *bonus* is not)

**❌ Typical Failure:**

* Fabricated answer

**✅ Fixed in:** V10

Control (in corpus): `Who is the CEO of Nirvana Retail Group?` → **Krishna Turlapati** (`NRG-MAN-HR-013`)

---

# H. Control Questions (Baseline Works)

Use these first to show V1 works for simple queries.

| Question                                                   | Expected Answer    |
| ---------------------------------------------------------- | ------------------ |
| What is the standard laptop reorder point?                 | 100 sellable units |
| What is the electronics return window?                     | 15 days            |
| Is MFA required by the information security policy?        | Yes                |
| After how many hours should a supplier delay be escalated? | 24 hours           |

✅ If these succeed but A1 or F1 fails → proves baseline limitations clearly.

---

# 🎯 Recommended Demo Flow

1. ✅ Control:
   `What is the standard laptop reorder point?`

2. 🚨 Freshness Failure:
   `When did the California laptop promotion end?`
   → Show expired chunk in UI

3. 🔗 Multi-Hop Failure:
   `Why did California laptop sales decline in April 2026?`

4. 🔍 SKU Failure:
   `Which SKU is called out as below reorder in the April 2026 inventory risk report?`

5. ✅ Close with:
   “Same corpus is used. Each version (V2–V7) fixes one failure type.”

---

# 📋 Paste-Only Cheat Sheet

```text
What is the standard laptop reorder point?
When did the California laptop promotion end?
Why did California laptop sales decline in April 2026?
Which SKU is called out as below reorder in the April 2026 inventory risk report?
What discount applied during this California laptop campaign?
Can an opened non-defective laptop be returned after 20 days?
How much off laptops in CA for the big Q1 promo?
What is Nirvana Retail's CEO bonus for 2026?
```

---

# 🔄 Version → Improvement Mapping

| Version | Improvement                     |
| ------- | ------------------------------- |
| V2      | Better chunking with overlap    |
| V3      | Hybrid (dense + lexical) search |
| V4      | Reranking                       |
| V5      | Query rewriting                 |
| V6      | Multi-query retrieval           |
| V7      | Metadata filtering              |
| V8      | Agentic retrieval               |
| V10     | Self-checking & grounding       |
