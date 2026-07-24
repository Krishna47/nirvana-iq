# What Qdrant stores (vectors + chunks)

## Simple example

Think of a library card for each paragraph:

| On the card | Example |
|-------------|---------|
| **Barcode for search** | 1536 numbers (the embedding vector) |
| **The paragraph itself** | The ~800-character text chunk |
| **Sticky notes** | `document_id`, `status`, `path`, dates… |

Qdrant shelves thousands of these cards (~3409 for gold v1).

When you ask a question:

1. Make a barcode for the question  
2. Find cards whose barcodes point the same way (**cosine**)  
3. Hand the **paragraph text** (not the barcode) to the LLM  

So: **vectors find**, **chunk text answers**.

```text
One Qdrant "point"
├── id:        UUID from hash(document_id|path|chunk_index)
├── vector:    [float × 1536]     ← search key
└── payload:   { text, document_id, status, path, … }  ← what we read back
```

---

## Detailed notes

### Point = vector + payload

We do **not** store “only vectors” or “only markdown files.” Each indexed chunk is a `PointStruct`:

- `id` — stable UUID derived from `document_id|path|chunk_index`  
- `vector` — embedding from OpenAI  
- `payload` — JSON fields including the **raw chunk string** under `text`

Code: `shared/indexing.py` (build payloads) + `shared/qdrant_store.py` (upsert / search).

### Payload fields we store

| Field | Role |
|-------|------|
| `text` | Chunk body sent to the LLM |
| `document_id` | Citation id (e.g. `NRG-POL-SALES-001`) |
| `path` | Path under `data/gold/` |
| `chunk_index` | Order within that file |
| `title`, `document_type`, `department`, `region` | Context |
| `doc_version`, `status`, `effective_date`, `expiry_date` | Metadata for later filters |

v1 **searches** only on the vector. Payload metadata is returned for display/citations but not used as filters yet.

### Collection naming

`{QDRANT_COLLECTION_PREFIX}_{pipeline_version}`  
Default: `nrg_gold_v1_basic_rag`

Distance metric: **Cosine**. Vector size: **1536**.

### What is *not* in Qdrant

- The chat model’s answer (generated on the fly)  
- Separate “document” rows for the whole file (we store **chunks**)  
- A second copy of embeddings for hybrid/BM25 (that’s a later design)

Original full files still live on disk under `data/gold/raw/…` and are also exposed by `GET /documents/{document_id}` for the Documents UI.

### Interview talking points

- “Vector DB holds dual representation: dense vector for recall, payload text for generation.”
- “Idempotent point ids let us re-index without random duplicates.”
- “Payload-rich design unlocks metadata filtering without re-embedding.”
