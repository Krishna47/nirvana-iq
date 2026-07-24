import { useState, type FormEvent } from 'react'
import { compare, type CompareRow } from '../api'
import { VERSIONS, getVersion } from '../versions'

const DEFAULT_COMPARE = ['v1_basic_rag']

export function Compare() {
  const [question, setQuestion] = useState(
    'When did the California laptop promotion end?',
  )
  const [selected, setSelected] = useState<string[]>(DEFAULT_COMPARE)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [rows, setRows] = useState<CompareRow[] | null>(null)

  function toggle(id: string) {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    )
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const q = question.trim()
    if (!q || selected.length === 0) return
    setLoading(true)
    setError(null)
    try {
      const data = await compare(q, selected)
      setRows(data.rows)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel compare">
      <p className="compare-intro">
        Run the same question across pipeline versions. Only runnable versions hit Qdrant;
        stubs return placeholder answers until implemented.
      </p>

      <div className="compare-versions">
        {VERSIONS.map((v) => (
          <label key={v.id} className={`compare-check ${v.runnable ? '' : 'stub'}`}>
            <input
              type="checkbox"
              checked={selected.includes(v.id)}
              onChange={() => toggle(v.id)}
            />
            <span>
              {v.short} {v.title}
              {!v.runnable && ' (stub)'}
            </span>
          </label>
        ))}
      </div>

      <form className="ask-form" onSubmit={onSubmit}>
        <label htmlFor="compare-question" className="sr-only">
          Question
        </label>
        <textarea
          id="compare-question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          placeholder="Question to compare…"
        />
        <button type="submit" disabled={loading || !question.trim() || selected.length === 0}>
          {loading ? 'Comparing…' : 'Compare'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {rows && (
        <div className="compare-table-wrap">
          <p className="compare-q">
            <span>Question:</span> {question}
          </p>
          <table className="compare-table">
            <thead>
              <tr>
                <th>Version</th>
                <th>Latency</th>
                <th>Citations</th>
                <th>Answer</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const meta = getVersion(row.version)
                return (
                  <tr key={row.version}>
                    <td>
                      <strong>
                        {meta?.short ?? row.version} {meta?.title ?? ''}
                      </strong>
                    </td>
                    <td>{(row.latency_ms / 1000).toFixed(2)}s</td>
                    <td>
                      {row.citations.length
                        ? row.citations.map((c) => (
                            <code key={c} className="cite">
                              {c}
                            </code>
                          ))
                        : '—'}
                    </td>
                    <td className="answer-cell">{row.answer}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
