export type RetrievedChunk = {
  document_id: string
  path: string
  text: string
  score: number
  metadata: Record<string, unknown>
}

export type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

export type AskResult = {
  version: string
  question: string
  answer: string
  citations: string[]
  retrieved_chunks: RetrievedChunk[]
  latency_ms: number
  notes: string
  search_query?: string
  search_queries?: string[]
}

export type CompareRow = {
  version: string
  answer: string
  citations: string[]
  latency_ms: number
  notes: string
}

export type CorpusDocument = {
  document_id: string
  title?: string
  document_type?: string
  department?: string
  region?: string
  version?: string
  status?: string
  effective_date?: string
  expiry_date?: string
  path?: string
  trap_tag?: string
  confidentiality?: string
  text?: string
  error?: string
}

export type DocumentsResponse = {
  document_id: string
  count: number
  documents: CorpusDocument[]
}

export type FetchDocumentOptions = {
  status?: string
  version?: string
  document_type?: string
  include_text?: boolean
}

const BASE = '/api'

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json()
    if (typeof data?.detail === 'string') return data.detail
    return JSON.stringify(data)
  } catch {
    return res.statusText || `HTTP ${res.status}`
  }
}

export async function fetchVersions(): Promise<string[]> {
  const res = await fetch(`${BASE}/versions`)
  if (!res.ok) throw new Error(await parseError(res))
  const data = await res.json()
  return data.versions as string[]
}

export async function ask(
  question: string,
  version: string,
  messages: ChatMessage[] = [],
): Promise<AskResult> {
  const res = await fetch(`${BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, version, messages }),
  })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function compare(
  question: string,
  versions: string[],
): Promise<{ question: string; rows: CompareRow[] }> {
  const res = await fetch(`${BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, versions }),
  })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function fetchDocuments(
  documentId: string,
  options: FetchDocumentOptions = {},
): Promise<DocumentsResponse> {
  const params = new URLSearchParams()
  if (options.status) params.set('status', options.status)
  if (options.version) params.set('version', options.version)
  if (options.document_type) params.set('document_type', options.document_type)
  if (options.include_text === false) params.set('include_text', 'false')

  const qs = params.toString()
  const url = `${BASE}/documents/${encodeURIComponent(documentId)}${qs ? `?${qs}` : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}
