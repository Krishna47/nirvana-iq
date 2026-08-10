# Demo cases — v7 Metadata filters

Hybrid retrieve on **v3** with Qdrant payload filters (status / region / year).

## Setup

```bash
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
# (only if collection missing; filters reuse existing points + payload indexes)
pip install -r modules/enterprise-rag/api/requirements.txt
```

Open Evolution Lab → select **V7**.

---

# A. Expired-policy trap fixed

### A1 — Operational promo end date (exclude expired)

```text
When did the California laptop promotion end?
```

**✅ Expected:** End date from **approved** v2.0 (`2026-03-31` / 12% era), cite `NRG-POL-SALES-001`.

**🔍 Check in UI:**

* **Applied filters:** `exclude_expired: true`, `region: California`
* **Chunks:** `status` is `approved` (not `expired`); path should not be `…v1-expired.md`

### A2 — 2026 campaign discount (year + exclude expired)

```text
What discount applied during the 2026 California laptop campaign?
```

**✅ Expected:** `12%` from approved policy (not expired `10%`).

**🔍 Check in UI:** Filters show `year: 2026` and `exclude_expired: true`.

---

# B. Intentional expired access still works

### B1 — Explicit expired campaign

```text
What discount applied in the expired California laptop campaign?
```

**✅ Expected:** `10%` from expired v1.0 trap doc is allowed.

**🔍 Check in UI:** `exclude_expired: false` (expired intent detected).

---

# Interview talking points

1. v1–v6 can retrieve expired policies because embeddings ignore lifecycle metadata.
2. v7 applies enterprise payload filters before generate — same collection, better ops answers.
3. Intent-aware: default exclude expired; allow when the user asks about expired/retired docs.
4. Point at the scorecard after `cli.py eval --version v7_metadata`.
