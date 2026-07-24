import { useEffect, useState, type FormEvent } from 'react'
import Markdown from 'react-markdown'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchDocuments, type CorpusDocument, type DocumentsResponse } from '../api'

const EXAMPLES = [
  'NRG-POL-SALES-001',
  'NRG-POL-INV-003',
  'NRG-POL-CX-004',
  'NRG-POL-SEC-009',
  'NRG-RPT-SALES-010',
  'NRG-RPT-INV-011',
]

function statusClass(status?: string): string {
  const s = (status || '').toLowerCase()
  if (s === 'expired') return 'status-pill expired'
  if (s === 'approved') return 'status-pill approved'
  return 'status-pill'
}

/** Prefer readable prose: drop YAML frontmatter and outer markdown fences. */
function prepareMarkdown(raw: string): string {
  let text = raw.trim()

  if (text.startsWith('```')) {
    const firstNl = text.indexOf('\n')
    if (firstNl !== -1) {
      text = text.slice(firstNl + 1)
      if (text.endsWith('```')) {
        text = text.slice(0, -3).trimEnd()
      }
    }
  }

  if (text.startsWith('---')) {
    const close = text.indexOf('\n---', 3)
    if (close !== -1) {
      text = text.slice(close + 4).replace(/^\r?\n+/, '')
    }
  }

  return text.trim()
}

function DocumentCard({ doc }: { doc: CorpusDocument }) {
  const body = doc.text ? prepareMarkdown(doc.text) : ''

  return (
    <article className="doc-card">
      <header className="doc-card-header">
        <div>
          <h2>{doc.title || doc.document_id}</h2>
          <p className="doc-id">
            <code>{doc.document_id}</code>
          </p>
        </div>
        <span className={statusClass(doc.status)}>{doc.status || 'unknown'}</span>
      </header>

      <dl className="doc-meta">
        <div>
          <dt>Type</dt>
          <dd>{doc.document_type || '—'}</dd>
        </div>
        <div>
          <dt>Version</dt>
          <dd>{doc.version || '—'}</dd>
        </div>
        <div>
          <dt>Department</dt>
          <dd>{doc.department || '—'}</dd>
        </div>
        <div>
          <dt>Region</dt>
          <dd>{doc.region || '—'}</dd>
        </div>
        <div>
          <dt>Effective</dt>
          <dd>{doc.effective_date || '—'}</dd>
        </div>
        <div>
          <dt>Expiry</dt>
          <dd>{doc.expiry_date || '—'}</dd>
        </div>
        <div>
          <dt>Trap tag</dt>
          <dd>{doc.trap_tag || '—'}</dd>
        </div>
        <div className="doc-meta-full">
          <dt>Path</dt>
          <dd className="mono">{doc.path || '—'}</dd>
        </div>
      </dl>

      {doc.error && <p className="error">{doc.error}</p>}

      {body && (
        <div className="doc-body">
          <h3>Document body</h3>
          <div className="markdown-body">
            <Markdown>{body}</Markdown>
          </div>
        </div>
      )}
    </article>
  )
}

export function Documents() {
  const params = useParams()
  const navigate = useNavigate()
  const routeId = params.documentId ? decodeURIComponent(params.documentId) : ''

  const [documentId, setDocumentId] = useState(routeId || 'NRG-POL-SALES-001')
  const [status, setStatus] = useState('')
  const [docVersion, setDocVersion] = useState('')
  const [documentType, setDocumentType] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DocumentsResponse | null>(null)

  async function loadDocument(
    id: string,
    filters?: { status: string; version: string; documentType: string },
  ) {
    const trimmed = id.trim()
    if (!trimmed) return
    const f = filters ?? { status, version: docVersion, documentType }
    setLoading(true)
    setError(null)
    try {
      const data = await fetchDocuments(trimmed, {
        status: f.status.trim() || undefined,
        version: f.version.trim() || undefined,
        document_type: f.documentType.trim() || undefined,
        include_text: true,
      })
      setResult(data)
    } catch (err) {
      setResult(null)
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!routeId) return
    setDocumentId(routeId)
    void loadDocument(routeId)
    // eslint-disable-next-line react-hooks/exhaustive-deps -- fetch when URL id changes
  }, [routeId])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const id = documentId.trim()
    if (!id) return
    navigate(`/documents/${encodeURIComponent(id)}`)
    await loadDocument(id)
  }

  return (
    <section className="panel documents">
      <div className="doc-examples">
        <span className="examples-label">Examples</span>
        {EXAMPLES.map((id) => (
          <button
            key={id}
            type="button"
            className="example-chip"
            onClick={() => {
              setDocumentId(id)
              navigate(`/documents/${encodeURIComponent(id)}`)
            }}
          >
            {id}
          </button>
        ))}
      </div>

      <form className="doc-form" onSubmit={onSubmit}>
        <label htmlFor="document-id">
          Document ID
          <input
            id="document-id"
            value={documentId}
            onChange={(e) => setDocumentId(e.target.value)}
            placeholder="NRG-POL-SALES-001"
            autoComplete="off"
          />
        </label>

        <div className="doc-filters">
          <label htmlFor="filter-status">
            Status
            <select
              id="filter-status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="">Any</option>
              <option value="approved">approved</option>
              <option value="expired">expired</option>
            </select>
          </label>
          <label htmlFor="filter-type">
            Type
            <select
              id="filter-type"
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
            >
              <option value="">Any</option>
              <option value="policy">policy</option>
              <option value="procedure">procedure</option>
              <option value="report">report</option>
              <option value="manual">manual</option>
              <option value="runbook">runbook</option>
              <option value="catalog">catalog</option>
            </select>
          </label>
          <label htmlFor="filter-version">
            Doc version
            <input
              id="filter-version"
              value={docVersion}
              onChange={(e) => setDocVersion(e.target.value)}
              placeholder="e.g. 2.0"
              autoComplete="off"
            />
          </label>
        </div>

        <button type="submit" disabled={loading || !documentId.trim()}>
          {loading ? 'Fetching…' : 'Fetch document'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="doc-results">
          <p className="doc-summary">
            Found <strong>{result.count}</strong> match
            {result.count === 1 ? '' : 'es'} for <code>{result.document_id}</code>
          </p>
          <div className="doc-list">
            {result.documents.map((doc) => (
              <DocumentCard
                key={`${doc.document_id}-${doc.version}-${doc.status}-${doc.path}`}
                doc={doc}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
