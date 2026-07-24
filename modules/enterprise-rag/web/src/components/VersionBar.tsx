import { VERSIONS, type VersionMeta } from '../versions'

type Props = {
  selected: string
  onSelect: (id: string) => void
}

export function VersionBar({ selected, onSelect }: Props) {
  return (
    <div className="version-bar" role="tablist" aria-label="RAG pipeline versions">
      {VERSIONS.map((v: VersionMeta) => (
        <button
          key={v.id}
          type="button"
          role="tab"
          aria-selected={selected === v.id}
          className={`version-chip ${selected === v.id ? 'active' : ''} ${v.runnable ? '' : 'stub'}`}
          onClick={() => onSelect(v.id)}
          title={v.runnable ? v.title : `${v.title} (stub)`}
        >
          {v.short}
        </button>
      ))}
    </div>
  )
}
