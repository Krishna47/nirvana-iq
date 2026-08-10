export type VersionId =
  | 'v1_basic_rag'
  | 'v2_better_chunking'
  | 'v3_hybrid_search'
  | 'v4_reranking'
  | 'v5_query_rewrite'
  | 'v6_multi_query'
  | 'v7_metadata'
  | 'v8_agentic_rag'
  | 'v9_multimodal'
  | 'v10_self_rag'

export type VersionMeta = {
  id: VersionId
  short: string
  title: string
  blurb: string
  runnable: boolean
}

export const VERSIONS: VersionMeta[] = [
  {
    id: 'v1_basic_rag',
    short: 'V1',
    title: 'Basic RAG',
    blurb: 'Fixed chunks + dense Qdrant retrieve + OpenAI generate.',
    runnable: true,
  },
  {
    id: 'v2_better_chunking',
    short: 'V2',
    title: 'Better Chunking',
    blurb: 'Section-aware chunks with overlap.',
    runnable: true,
  },
  {
    id: 'v3_hybrid_search',
    short: 'V3',
    title: 'Hybrid Search',
    blurb: 'BM25 + dense fusion.',
    runnable: true,
  },
  {
    id: 'v4_reranking',
    short: 'V4',
    title: 'Reranking',
    blurb: 'Retrieve top-N, rerank to top-K.',
    runnable: true,
  },
  {
    id: 'v5_query_rewrite',
    short: 'V5',
    title: 'Query Rewrite',
    blurb: 'LlamaIndex rewrite, then hybrid retrieve.',
    runnable: true,
  },
  {
    id: 'v6_multi_query',
    short: 'V6',
    title: 'Multi-Query',
    blurb: 'Expand queries and fuse results.',
    runnable: false,
  },
  {
    id: 'v7_metadata',
    short: 'V7',
    title: 'Metadata Filters',
    blurb: 'Status / date / region filters (expired policies).',
    runnable: false,
  },
  {
    id: 'v8_agentic_rag',
    short: 'V8',
    title: 'Agentic RAG',
    blurb: 'Retrieve → check → re-retrieve.',
    runnable: false,
  },
  {
    id: 'v9_multimodal',
    short: 'V9',
    title: 'Multimodal',
    blurb: 'Image / table-aware retrieval.',
    runnable: false,
  },
  {
    id: 'v10_self_rag',
    short: 'V10',
    title: 'Self-RAG',
    blurb: 'Critique and self-correct before answering.',
    runnable: false,
  },
]

export function getVersion(id: string): VersionMeta | undefined {
  return VERSIONS.find((v) => v.id === id)
}
