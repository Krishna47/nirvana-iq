# Embeddings

## Simple example

Imagine three sticky notes:

1. “California laptop promo ends March 31, 2026.”
2. “When did the CA laptop promotion end?”
3. “Reset the store Wi‑Fi password.”

An **embedding model** turns each note into a long list of numbers (a vector), like a fingerprint of meaning.

- Notes 1 and 2 get fingerprints that look **similar**.
- Note 3 looks **different**.

You don’t read the numbers yourself. The computer uses them to find “which stored notes match this question?”

In Nirvana IQ v1 we use OpenAI **`text-embedding-3-small`** → each text becomes **1536 numbers**.

```text
"promo ends March 31"     →  [0.02, -0.11, 0.07, …]   (1536 floats)
"when did CA promo end?"  →  [0.03, -0.10, 0.06, …]   (similar)
"reset Wi-Fi password"    →  [-0.4,  0.22, -0.01, …]  (different)
```

---

## Detailed notes

### What an embedding is

An embedding is a **fixed-length vector** produced by a neural network trained so that texts with related meaning land near each other in vector space.

- Input: string (chunk or question)
- Output: `list[float]` of length `d` (here `d = 1536`)
- Same model must be used at **index time** and **query time** (otherwise spaces don’t match)

### Why RAG needs them

Keyword search finds shared words. Embeddings find **semantic** overlap (“end date” ≈ “when did it end”) even when wording differs.

v1 flow:

1. **Index:** embed every chunk → store vectors in Qdrant  
2. **Ask:** embed the question → find nearest chunk vectors  
3. **Generate:** send those chunk **texts** to the chat LLM (not the raw floats)

Code: `shared/openai_client.py` (`embed_texts`, `embed_query`).

### What embeddings are *not*

- Not a summary the user reads  
- Not the final answer  
- Not a substitute for metadata filters (`status=expired` is invisible to pure embedding search)

### Interview talking points

- “Embeddings map text into a space where cosine similarity approximates topical relatedness.”
- “We pay once at index time (all chunks) and once per query (question only).”
- “Chunk quality matters: garbage in → misleading neighbors out.”

### Our project settings

| Setting | Value |
|---------|--------|
| Model | `text-embedding-3-small` (from `api/.env`) |
| Dimensions | 1536 |
| Used in | `cli.py index`, `v1_basic_rag` ask path |
