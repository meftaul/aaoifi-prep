import './App.css'
import { guideHref, guides } from './guides'
import GuidePage from './GuidePage'
import ThemeToggle from './ThemeToggle'
import Arrow from './Arrow'

const tones = ['violet', 'coral', 'mint', 'sun']

function stdNumber(standard: string) {
  const n = standard.match(/(\d+)\s*$/)?.[1]
  return n ? n.padStart(2, '0') : '•'
}

function Home() {
  return (
    <div className="home-wrap">
      <div className="blobs" aria-hidden="true">
        <span className="blob b1" />
        <span className="blob b2" />
        <span className="blob b3" />
      </div>

      <main className="home">
        <nav className="home-nav">
          <a href={import.meta.env.BASE_URL} className="brand">
            <span className="brand-mark">A</span>
            AAOIFI Prep
          </a>
          <ThemeToggle />
        </nav>

        <header className="hero">
          <p className="hero-kicker">Study smarter · পড়ুন সহজে</p>
          <h1>
            Master the <span className="grad-text">Shari'ah Standards</span>
          </h1>
          <p className="hero-sub">
            Bilingual (English &amp; Bangla) study guides to the AAOIFI Shari'ah Standards — rulings, evidence,
            worked examples and practice questions, one standard at a time.
          </p>
          <ul className="chips">
            <li className="chip chip-violet">
              English &amp; <span lang="bn">বাংলা</span>
            </li>
            <li className="chip chip-coral">Diagrams &amp; tables</li>
            <li className="chip chip-mint">Practice questions</li>
            <li className="chip chip-sun">{guides.length} guides</li>
          </ul>
        </header>

        <h2 className="section-title">Pick a standard</h2>
        <ul className="guide-list">
          {guides.map((g, i) => (
            <li key={g.slug} style={{ animationDelay: `${0.08 * i + 0.1}s` }}>
              <a href={guideHref(g.slug)} className={`card tone-${tones[i % tones.length]}`}>
                <span className="card-num" aria-hidden="true">
                  {stdNumber(g.standard)}
                </span>
                <span className="guide-std">{g.standard}</span>
                <span className="guide-title">{g.title}</span>
                <span className="guide-bn" lang="bn">
                  {g.bangla}
                </span>
                <span className="guide-summary">{g.summary}</span>
                <span className="card-cta">
                  Start studying <span className="arrow">
                    <Arrow />
                  </span>
                </span>
              </a>
            </li>
          ))}
        </ul>

        <footer className="footer">
          A personal study project, not affiliated with AAOIFI. For study purposes — not a fatwa.
        </footer>
      </main>
    </div>
  )
}

function App() {
  const slug = new URLSearchParams(window.location.search).get('guide')
  const guide = guides.find((g) => g.slug === slug)
  return guide ? <GuidePage guide={guide} /> : <Home />
}

export default App
