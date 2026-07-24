# v1 RAG flow (how the pieces connect)

## Simple example

**Offline (once):**  
Cut each gold doc into short pieces → fingerprint each piece → put fingerprints + text into Qdrant.

**Online (every question):**  
Fingerprint the question → find nearest pieces → ask the chat model to answer using only those pieces.

```text
  Gold markdown
       │
       ▼
  Chunk (800 chars) ──embed──► Vector ──┐
       │                                │
       └── text + metadata ─────────────┼──► Qdrant point
                                        │
  User question ──embed──► Query vector ┘
                              │
                              ▼
                     Top-4 similar points
                              │
                              ▼
                     LLM sees chunk texts
                              │
                              ▼
                          Answer + citations
```

---

## Detailed notes

### Two phases

| Phase | Command / API | Models |
|-------|----------------|--------|
| Index | `cli.py index --version v1_basic_rag` | Embeddings only |
| Ask | `POST /ask` or Lab UI | Embeddings + chat |

### Design choices in v1 (intentional limits)

| Choice | Effect |
|--------|--------|
| Fixed 800-char chunks, 0 overlap | Mid-sentence cuts; fixed in v2 |
| Dense-only cosine | Weak on SKUs/ids; hybrid in v3 |
| No metadata filter | Expired docs can win; v7 |
| Top-4, no rerank | Near-misses; v4 |
| One-shot retrieve→generate | Weak multi-hop; v8 |

### Where to read more

- [Embeddings](embeddings.md)  
- [Cosine similarity](cosine-similarity.md)  
- [Qdrant storage](qdrant-storage.md)  
- [v1 demo failure cases](../../evaluation/demo-cases/v1_basic_rag.md)  
