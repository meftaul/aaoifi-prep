import { useEffect, useRef, useState } from 'react'
import { drawDiagrams } from './diagrams'
import type { Guide, GuideContent } from './guides'
import ThemeToggle from './ThemeToggle'

export default function GuidePage({ guide }: { guide: Guide }) {
  const [content, setContent] = useState<GuideContent | null>(null)
  const [tocOpen, setTocOpen] = useState(false)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [showTop, setShowTop] = useState(false)
  const docRef = useRef<HTMLElement>(null)
  const progressRef = useRef<HTMLDivElement>(null)
  const tocRef = useRef<HTMLElement>(null)

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

  // Reading progress bar and back-to-top button.
  useEffect(() => {
    let frame = 0
    const update = () => {
      frame = 0
      const el = document.documentElement
      const max = el.scrollHeight - el.clientHeight
      const p = max > 0 ? Math.min(1, el.scrollTop / max) : 0
      progressRef.current?.style.setProperty('--p', String(p))
      setShowTop(el.scrollTop > 900)
    }
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update)
    }
    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
      if (frame) cancelAnimationFrame(frame)
    }
  }, [content])

  // Highlight the section being read in the contents list.
  useEffect(() => {
    if (!content) return
    const targets = content.toc
      .map(([, id]) => document.getElementById(id))
      .filter((el): el is HTMLElement => el !== null)
    if (!targets.length) return
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting)
        if (visible.length) {
          visible.sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
          setActiveId(visible[0].target.id)
        }
      },
      { rootMargin: '-70px 0px -65% 0px' },
    )
    targets.forEach((t) => obs.observe(t))
    return () => obs.disconnect()
  }, [content])

  // Keep the active entry in view inside the sticky contents panel.
  useEffect(() => {
    if (!activeId || !tocRef.current) return
    const link = tocRef.current.querySelector<HTMLElement>(`a[href="#${CSS.escape(activeId)}"]`)
    link?.scrollIntoView({ block: 'nearest' })
  }, [activeId])

  return (
    <div className="guide">
      <header className="topbar">
        <a href={import.meta.env.BASE_URL} className="back">
          <span aria-hidden="true">←</span> All guides
        </a>
        <span className="topbar-title">{guide.title}</span>
        <div className="topbar-actions">
          <button className="toc-toggle" onClick={() => setTocOpen((o) => !o)} aria-expanded={tocOpen}>
            {tocOpen ? 'Close' : 'Contents'}
          </button>
          <ThemeToggle />
        </div>
        <div className="progress" ref={progressRef} aria-hidden="true" />
      </header>

      <section className="cover">
        <div className="cover-shapes" aria-hidden="true">
          <span className="shape s1" />
          <span className="shape s2" />
          <span className="shape s3" />
        </div>
        <div className="cover-inner">
          <p className="cover-eyebrow">
            <span className="pill">{guide.standard}</span> Study guide
          </p>
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
        </div>
      </section>

      <div className="guide-layout">
        <nav ref={tocRef} className={`toc ${tocOpen ? 'open' : ''}`} aria-label="Contents">
          <p className="toc-title">Contents</p>
          <ol>
            {content?.toc.map(([level, id, title]) => (
              <li key={id} className={`toc-l${level}`}>
                <a
                  href={`#${id}`}
                  className={id === activeId ? 'active' : undefined}
                  aria-current={id === activeId ? 'location' : undefined}
                  onClick={() => setTocOpen(false)}
                >
                  {title}
                </a>
              </li>
            ))}
          </ol>
        </nav>

        <article
          className="doc"
          ref={docRef}
          dangerouslySetInnerHTML={{
            __html: content ? content.html : '<p class="loading"><span></span><span></span><span></span></p>',
          }}
        />
      </div>

      <button
        type="button"
        className={`to-top ${showTop ? 'show' : ''}`}
        onClick={() => window.scrollTo({ top: 0 })}
        aria-label="Back to top"
        tabIndex={showTop ? 0 : -1}
      >
        ↑
      </button>
    </div>
  )
}
