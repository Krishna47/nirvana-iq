import { useState, type FormEvent } from 'react'
import { ask, type AskResult } from '../api'
import { getVersion } from '../versions'
import { VersionBar } from './VersionBar'

type Tab = 'sources' | 'chunks' | 'metrics'

export function Lab() {
  const [version, setVersion] = useState('v1_basic_rag')
  const [question, setQuestion] = useState(
    'When did the California laptop promotion end?',
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AskResult | null>(null)
  const [tab, setTab] = useState<Tab>('sources')

  const meta = getVersion(version)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const q = question.trim()
    if (!q) return
    setLoading(true)
    setError(null)
    try {
      const data = await ask(q, version)
      setResult(data)
      setTab('sources')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel lab">
      <VersionBar selected={version} onSelect={setVersion} />

      <div className="selected-meta">
        <p className="selected-label">
          Selected: <strong>{meta?.short}</strong> — {meta?.title}
          {!meta?.runnable && <span className="badge">stub</span>}
        </p>
        <p className="selected-blurb">{meta?.blurb}</p>
      </div>

      <form className="ask-form" onSubmit={onSubmit}>
        <label htmlFor="lab-question" className="sr-only">
          Ask a question
        </label>
        <textarea
          id="lab-question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          placeholder="Ask a question..."
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? 'Retrieving…' : 'Ask'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <h2>Answer</h2>
          <div className="answer-body">{result.answer}</div>

          <div className="detail-tabs" role="tablist">
            {(['sources', 'chunks', 'metrics'] as Tab[]).map((t) => (
              <button
                key={t}
                type="button"
                role="tab"
                className={tab === t ? 'active' : ''}
                aria-selected={tab === t}
                onClick={() => setTab(t)}
              >
                {t === 'sources' ? 'Sources' : t === 'chunks' ? 'Retrieved Chunks' : 'Metrics'}
              </button>
            ))}
          </div>

          <div className="detail-panel">
            {tab === 'sources' && (
              <ul className="source-list">
                {result.citations.length === 0 && <li>No citations</li>}
                {result.citations.map((c) => (
                  <li key={c}>
                    <code>{c}</code>
                  </li>
                ))}
              </ul>
            )}
            {tab === 'chunks' && (
              <div className="chunk-list">
                {result.retrieved_chunks.map((chunk, i) => (
                  <article key={`${chunk.document_id}-${i}`} className="chunk">
                    <header>
                      <code>{chunk.document_id}</code>
                      <span>score {chunk.score.toFixed(3)}</span>
                    </header>
                    <p className="chunk-path">{chunk.path}</p>
                    <pre>{chunk.text}</pre>
                  </article>
                ))}
              </div>
            )}
            {tab === 'metrics' && (
              <dl className="metrics-grid">
                <div>
                  <dt>Latency</dt>
                  <dd>{(result.latency_ms / 1000).toFixed(2)}s</dd>
                </div>
                <div>
                  <dt>Chunks</dt>
                  <dd>{result.retrieved_chunks.length}</dd>
                </div>
                <div>
                  <dt>Citations</dt>
                  <dd>{result.citations.length}</dd>
                </div>
                <div>
                  <dt>Notes</dt>
                  <dd>{result.notes || '—'}</dd>
                </div>
              </dl>
            )}
          </div>

          <footer className="metrics-bar">
            <span>Latency: {(result.latency_ms / 1000).toFixed(2)}s</span>
            <span>Citations: {result.citations.length}</span>
            <span>Chunks: {result.retrieved_chunks.length}</span>
          </footer>
        </div>
      )}
    </section>
  )
}
