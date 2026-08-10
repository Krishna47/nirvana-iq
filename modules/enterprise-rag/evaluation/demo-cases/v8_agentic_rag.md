# Demo cases — v8 Agentic RAG

LangGraph **retrieve → check → re-retrieve → generate** on **v3** hybrid with **v7** filters.

## Setup

```bash
python modules/enterprise-rag/cli.py index --version v3_hybrid_search --recreate
pip install -r modules/enterprise-rag/api/requirements.txt
```

Open Evolution Lab → select **V8**.

---

# A. Multi-hop coverage

### A1 — California sales decline (star demo)

```text
Why did California laptop sales decline in April 2026?
```

**✅ Expected:** Promotion expired **and** inventory below reorder; cite among
`NRG-RPT-SALES-010`, `NRG-RPT-INV-011`, `NRG-POL-SALES-001`, `NRG-POL-INV-003`.

**🔍 Check in UI:**

* **Agent steps** shows retrieve → check → generate (and a second retrieve when the check finds a gap)
* Answer mentions both promo and inventory/reorder

---

# B. Single-hop stays cheap

### B1 — Reorder point

```text
What is the standard laptop reorder point?
```

**✅ Expected:** 100 sellable units (`NRG-POL-INV-003`).

**🔍 Check in UI:** Usually one retrieve round; check marks sufficient.

---

# C. Filters still apply

Operational California promo asks still exclude `status=expired` on each retrieve round
(see **Applied filters** inside retrieve steps / chunk status).

---

# Interview talking points

1. v8 adds a **coverage check**, not just better ranking or more queries up front.
2. Max 1 retry keeps latency bounded for demos.
3. Distinct from v10 (answer critique / self-correct).
4. Point at the scorecard after `cli.py eval --version v8_agentic_rag`.
