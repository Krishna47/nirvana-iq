import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { Compare } from './components/Compare'
import { Documents } from './components/Documents'
import { Lab } from './components/Lab'
import './styles.css'

function Shell({
  title,
  tagline,
  showNav = true,
  children,
}: {
  title: string
  tagline: string
  showNav?: boolean
  children: React.ReactNode
}) {
  return (
    <div className="app">
      <div className="atmosphere" aria-hidden="true" />
      <header className="hero">
        <p className="eyebrow">Nirvana IQ · Nirvana Retail Group</p>
        <h1>{title}</h1>
        <p className="tagline">{tagline}</p>
        {showNav && (
          <nav className="mode-nav" aria-label="Views">
            <NavLink to="/lab" className={({ isActive }) => (isActive ? 'active' : '')}>
              Lab
            </NavLink>
            <NavLink to="/compare" className={({ isActive }) => (isActive ? 'active' : '')}>
              Compare
            </NavLink>
            <NavLink
              to="/documents"
              className={({ isActive }) => (isActive ? 'active' : '')}
              target="_blank"
              rel="noreferrer"
              title="Opens Documents in a new tab"
            >
              Documents ↗
            </NavLink>
          </nav>
        )}
      </header>
      <main>{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/lab" replace />} />
      <Route
        path="/lab"
        element={
          <Shell
            title="Enterprise RAG Evolution Lab"
            tagline="Versioned pipelines with multi-turn, conversation-aware retrieval on one gold corpus."
          >
            <Lab />
          </Shell>
        }
      />
      <Route
        path="/compare"
        element={
          <Shell
            title="Enterprise RAG Evolution Lab"
            tagline="Same question across pipeline versions."
          >
            <Compare />
          </Shell>
        }
      />
      <Route
        path="/documents"
        element={
          <Shell title="Gold Document Lookup" tagline="Fetch policies and reports by document_id." showNav={false}>
            <Documents />
          </Shell>
        }
      />
      <Route
        path="/documents/:documentId"
        element={
          <Shell title="Gold Document Lookup" tagline="Fetch policies and reports by document_id." showNav={false}>
            <Documents />
          </Shell>
        }
      />
      <Route path="*" element={<Navigate to="/lab" replace />} />
    </Routes>
  )
}
