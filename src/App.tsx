import './App.css'
import { guideHref, guides } from './guides'
import GuidePage from './GuidePage'

function Home() {
  return (
    <main className="home">
      <header className="home-head">
        <h1>AAOIFI Prep</h1>
        <p>Bilingual (English &amp; Bangla) study guides to the AAOIFI Shari'ah Standards.</p>
      </header>

      <ul className="guide-list">
        {guides.map((g) => (
          <li key={g.slug}>
            <a href={guideHref(g.slug)}>
              <span className="guide-std">{g.standard}</span>
              <span className="guide-title">{g.title}</span>
              <span className="guide-bn" lang="bn">
                {g.bangla}
              </span>
            </a>
          </li>
        ))}
      </ul>

      <footer className="footer">
        A personal study project, not affiliated with AAOIFI. For study purposes — not a fatwa.
      </footer>
    </main>
  )
}

function App() {
  const slug = new URLSearchParams(window.location.search).get('guide')
  const guide = guides.find((g) => g.slug === slug)
  return guide ? <GuidePage guide={guide} /> : <Home />
}

export default App
