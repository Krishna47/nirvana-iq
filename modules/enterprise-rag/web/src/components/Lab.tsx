import { useState, type FormEvent } from 'react'
import { ask, type AskResult, type ChatMessage } from '../api'
import { getVersion } from '../versions'
import { VersionBar } from './VersionBar'

type Tab = 'sources' | 'chunks' | 'metrics'

type VersionChatState = {
  messages: ChatMessage[]
  result: AskResult | null
  error: string | null
  draft: string
  tab: Tab
}

const DEFAULT_DRAFT = 'When did the California laptop promotion end?'

function emptyChatState(): VersionChatState {
  return {
    messages: [],
    result: null,
    error: null,
    draft: DEFAULT_DRAFT,
    tab: 'sources',
  }
}

export function Lab() {
  const [version, setVersion] = useState('v1_basic_rag')
  const [sessions, setSessions] = useState<Record<string, VersionChatState>>({})
  const [loading, setLoading] = useState(false)

  const chat = sessions[version] ?? emptyChatState()
  const meta = getVersion(version)

  function patchSession(
    targetVersion: string,
    update: Partial<VersionChatState> | ((prev: VersionChatState) => VersionChatState),
  ) {
    setSessions((prev) => {
      const base = prev[targetVersion] ?? emptyChatState()
      const next = typeof update === 'function' ? update(base) : { ...base, ...update }
      return { ...prev, [targetVersion]: next }
    })
  }

  function clearChat() {
    patchSession(version, emptyChatState())
  }

  function onSelectVersion(next: string) {
    if (next === version || loading) return
    setVersion(next)
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const q = chat.draft.trim()
    if (!q || loading) return

    const askVersion = version
    const prior: ChatMessage[] = chat.messages.map(({ role, content }) => ({ role, content }))

    setLoading(true)
    patchSession(askVersion, (prev) => ({
      ...prev,
      error: null,
      draft: '',
      messages: [...prev.messages, { role: 'user', content: q }],
    }))

    try {
      const data = await ask(q, askVersion, prior)
      patchSession(askVersion, (prev) => ({
        ...prev,
        result: data,
        tab: 'sources',
        messages: [...prev.messages, { role: 'assistant', content: data.answer }],
      }))
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err)
      patchSession(askVersion, (prev) => {
        const messages =
          prev.messages.length && prev.messages[prev.messages.length - 1]?.role === 'user'
            ? prev.messages.slice(0, -1)
            : prev.messages
        return { ...prev, error: message, draft: q, messages }
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel lab">
      <VersionBar selected={version} onSelect={onSelectVersion} />

      <div className="selected-meta">
        <p className="selected-label">
          Selected: <strong>{meta?.short}</strong> — {meta?.title}
          {!meta?.runnable && <span className="badge">stub</span>}
        </p>
        <p className="selected-blurb">{meta?.blurb}</p>
        <p className="selected-blurb chat-hint">
          Multi-turn chat: follow-ups condense into a standalone search query, then answer with
          conversation context. Each version keeps its own thread.
        </p>
      </div>

      {chat.messages.length > 0 && (
        <div className="chat-toolbar">
          <button type="button" className="ghost-btn" onClick={clearChat} disabled={loading}>
            Clear chat
          </button>
        </div>
      )}

      <div className="chat-thread" aria-live="polite">
        {chat.messages.length === 0 && (
          <p className="chat-empty">Ask a question, then try a follow-up like “What about the return window?”</p>
        )}
        {chat.messages.map((m, i) => (
          <div key={`${m.role}-${i}`} className={`chat-bubble ${m.role}`}>
            <span className="chat-role">{m.role === 'user' ? 'You' : 'Assistant'}</span>
            <div className="chat-content">{m.content}</div>
          </div>
        ))}
        {loading && (
          <div className="chat-bubble assistant pending">
            <span className="chat-role">Assistant</span>
            <div className="chat-content">Retrieving…</div>
          </div>
        )}
      </div>

      <form className="ask-form chat-composer" onSubmit={onSubmit}>
        <label htmlFor="lab-question" className="sr-only">
          Ask a question
        </label>
        <textarea
          id="lab-question"
          value={chat.draft}
          onChange={(e) => patchSession(version, { draft: e.target.value })}
          rows={3}
          placeholder="Ask a question or follow-up..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !chat.draft.trim()}>
          {loading ? 'Retrieving…' : chat.messages.length ? 'Send' : 'Ask'}
        </button>
      </form>

      {chat.error && <p className="error">{chat.error}</p>}

      {chat.result && (
        <div className="result">
          <h2>Latest turn details</h2>

          {version === 'v5_query_rewrite' && (
            <div className="rewrite-panel">
              <h3>Rewritten query</h3>
              <p className="rewrite-label">LlamaIndex rewrite used for hybrid retrieve</p>
              <dl className="rewrite-compare">
                <div>
                  <dt>User question</dt>
                  <dd>{chat.result.question}</dd>
                </div>
                <div>
                  <dt>Rewritten query</dt>
                  <dd className="rewrite-output">
                    {chat.result.search_query || chat.result.question}
                  </dd>
                </div>
              </dl>
            </div>
          )}

          {version === 'v6_multi_query' && (
            <div className="rewrite-panel">
              <h3>Expanded queries</h3>
              <p className="rewrite-label">
                LlamaIndex multi-query expand; each query hybrid-searched then fused with RRF
              </p>
              <dl className="rewrite-compare">
                <div>
                  <dt>User question</dt>
                  <dd>{chat.result.question}</dd>
                </div>
                <div>
                  <dt>Expanded queries</dt>
                  <dd>
                    <ol className="expanded-query-list">
                      {(chat.result.search_queries?.length
                        ? chat.result.search_queries
                        : (chat.result.search_query || chat.result.question)
                            .split(' | ')
                            .map((s) => s.trim())
                            .filter(Boolean)
                      ).map((q, i) => (
                        <li key={`${i}-${q}`} className="rewrite-output">
                          {q}
                        </li>
                      ))}
                    </ol>
                  </dd>
                </div>
              </dl>
            </div>
          )}

          <div className="detail-tabs" role="tablist">
            {(['sources', 'chunks', 'metrics'] as Tab[]).map((t) => (
              <button
                key={t}
                type="button"
                role="tab"
                className={chat.tab === t ? 'active' : ''}
                aria-selected={chat.tab === t}
                onClick={() => patchSession(version, { tab: t })}
              >
                {t === 'sources' ? 'Sources' : t === 'chunks' ? 'Retrieved Chunks' : 'Metrics'}
              </button>
            ))}
          </div>

          <div className="detail-panel">
            {chat.tab === 'sources' && (
              <ul className="source-list">
                {chat.result.citations.length === 0 && <li>No citations</li>}
                {chat.result.citations.map((c) => (
                  <li key={c}>
                    <code>{c}</code>
                  </li>
                ))}
              </ul>
            )}
            {chat.tab === 'chunks' && (
              <div className="chunk-list">
                {chat.result.retrieved_chunks.map((chunk, i) => (
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
            {chat.tab === 'metrics' && (
              <dl className="metrics-grid">
                <div>
                  <dt>Latency</dt>
                  <dd>{(chat.result.latency_ms / 1000).toFixed(2)}s</dd>
                </div>
                <div>
                  <dt>Chunks</dt>
                  <dd>{chat.result.retrieved_chunks.length}</dd>
                </div>
                <div>
                  <dt>Citations</dt>
                  <dd>{chat.result.citations.length}</dd>
                </div>
                <div>
                  <dt>Search query</dt>
                  <dd>{chat.result.search_query || chat.result.question}</dd>
                </div>
                <div>
                  <dt>User question</dt>
                  <dd>{chat.result.question}</dd>
                </div>
                <div>
                  <dt>Notes</dt>
                  <dd>{chat.result.notes || '—'}</dd>
                </div>
              </dl>
            )}
          </div>

          <footer className="metrics-bar">
            <span>Latency: {(chat.result.latency_ms / 1000).toFixed(2)}s</span>
            <span>Citations: {chat.result.citations.length}</span>
            <span>Chunks: {chat.result.retrieved_chunks.length}</span>
          </footer>
        </div>
      )}
    </section>
  )
}
