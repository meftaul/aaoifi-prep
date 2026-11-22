import { useEffect, useRef, useState } from 'react'
import { drawDiagrams } from './diagrams'
import type { Guide, GuideContent } from './guides'

export default function GuidePage({ guide }: { guide: Guide }) {
  const [content, setContent] = useState<GuideContent | null>(null)
  const [tocOpen, setTocOpen] = useState(false)
  const docRef = useRef<HTMLElement>(null)

  useEffect(() => {
    document.title = `${guide.standard} — ${guide.title} · AAOIFI Prep`
    guide.load().then(setContent)
  }, [guide])

  // Draw the D3 diagrams, then jump to the hash target, once the content has rendered.
  useEffect(() => {
    if (!content) return
    if (docRef.current) drawDiagrams(docRef.current, content.diagrams)
    if (!window.location.hash) return
    document.getElementById(decodeURIComponent(window.location.hash.slice(1)))?.scrollIntoView()
  }, [content])

  return (
    <div className="guide">
      <header className="topbar">
        <a href={import.meta.env.BASE_URL} className="back">
          ← All study guides
        </a>
        <button className="toc-toggle" onClick={() => setTocOpen((o) => !o)} aria-expanded={tocOpen}>
          Contents
        </button>
      </header>

      <section className="cover">
        <p className="cover-eyebrow">{guide.standard} · Study guide</p>
        <h1>{guide.title}</h1>
        <p className="cover-ar" lang="ar" dir="rtl">
          {guide.arabic}
        </p>
        <p className="cover-bn" lang="bn">
          {guide.bangla}
        </p>
        <p className="cover-summary">{guide.summary}</p>
        <div className="cover-meta">
          {guide.meta.map((m) => (
            <p key={m}>{m}</p>
          ))}
        </div>
      </section>

      <div className="guide-layout">
        <nav className={`toc ${tocOpen ? 'open' : ''}`} aria-label="Contents">
          <p className="toc-title">Contents</p>
          <ol>
            {content?.toc.map(([level, id, title]) => (
              <li key={id} className={`toc-l${level}`}>
                <a href={`#${id}`} onClick={() => setTocOpen(false)}>
                  {title}
                </a>
              </li>
            ))}
          </ol>
        </nav>

        <article
          className="doc"
          ref={docRef}
          dangerouslySetInnerHTML={{ __html: content ? content.html : '<p>Loading…</p>' }}
        />
      </div>
    </div>
  )
}
