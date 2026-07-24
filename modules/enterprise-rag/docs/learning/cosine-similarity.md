# Cosine similarity

## Simple example

Think of two arrows drawn from the same origin.

- If they point **almost the same way**, cosine similarity is close to **1** → “related.”
- If they point at **right angles**, cosine is about **0** → “unrelated.”
- If they point **opposite** ways, cosine is near **-1** (rare with typical text embeddings).

Length of the arrow matters less than **direction**. A short sentence and a longer paragraph can still match if they are “about the same thing.”

```text
Question vector  ↗
Chunk A vector   ↗   small angle  → high cosine → retrieve A
Chunk B vector   →   large angle → low cosine  → skip B
```

In Lab UI, the **score** on each retrieved chunk is essentially this similarity from Qdrant (cosine).

---

## Detailed notes

### Definition (intuition)

For vectors \(a\) and \(b\):

\[
\cos(\theta) = \frac{a \cdot b}{\|a\| \|b\|}
\]

- Numerator: how much they agree (dot product)  
- Denominator: normalize by lengths so magnitude doesn’t dominate  

So cosine is a **normalized** relatedness score based on angle \(\theta\).

### Why Qdrant uses it here

Collection `nrg_gold_v1_basic_rag` is created with `Distance.COSINE` (`shared/qdrant_store.py`). At ask time we:

1. Embed the question  
2. `query_points` with that vector  
3. Take **top_k = 4** highest scores  

No keyword score, no metadata filter — **only** this geometric neighborhood.

### Why this causes the v1 “expired policy” demo

Expired and current California promo policies share similar language (“California”, “laptop”, “promotion”, “end date”). Their chunk embeddings sit near the question. Cosine happily ranks the **expired** chunk high because **freshness is not part of the vector**. Metadata like `status` lives in the payload but is unused until **v7**.

### Scores in practice

- You’ll often see scores like `0.65–0.85` for “pretty related,” not always 0.99  
- Absolute thresholds vary by model and corpus; **ranking order** usually matters more than a magic cutoff  
- Top-4 means “best of cosine,” not “all correct”

### Interview talking points

- “Cosine ignores vector length and compares orientation — good for semantic retrieval.”
- “Similarity ≠ truthfulness or currency; that’s why we add filters and rerankers later.”
- “Dense-only retrieval fails on exact IDs/SKUs when lexical match would win — hybrid is v3.”

### Related ladder fixes

| Limitation of cosine-only | Later version |
|---------------------------|---------------|
| No freshness / status | v7 metadata |
| Weak exact tokens | v3 hybrid |
| Near-misses in top-k | v4 rerank |
