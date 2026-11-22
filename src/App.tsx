import './App.css'

const features = [
  {
    title: 'Standards summaries',
    body: 'Concise notes on each standard: purpose, key rulings and the points examiners like to test.',
  },
  {
    title: 'Practice questions',
    body: 'Question banks by topic, with explanations that point back to the relevant clause.',
  },
  {
    title: 'Progress tracking',
    body: 'See which standards you have covered, where you score well and what to revise next.',
  },
]

const topics = [
  { name: "Shari'ah Standards", note: 'Murabaha, Ijarah, Musharakah, Sukuk and more' },
  { name: 'Financial Accounting Standards', note: 'Recognition, measurement and disclosure' },
  { name: 'Governance Standards', note: "Shari'ah supervisory boards and internal review" },
  { name: 'Auditing Standards', note: 'Objectives, principles and the auditor’s report' },
  { name: 'Ethics', note: 'Code of ethics for accountants and auditors' },
]

function App() {
  return (
    <>
      <header className="nav">
        <a className="brand" href="#top">
          <span className="brand-mark" aria-hidden="true">A</span>
          AAOIFI Prep
        </a>
        <nav>
          <a href="#features">Features</a>
          <a href="#topics">Topics</a>
        </nav>
      </header>

      <main id="top">
        <section className="hero">
          <p className="eyebrow">Personal study companion</p>
          <h1>Prepare for AAOIFI, one standard at a time.</h1>
          <p className="lede">
            A focused place to study the AAOIFI Shari'ah, accounting, governance and auditing
            standards, practise questions and track how close you are to exam-ready.
          </p>
          <div className="actions">
            <a className="btn primary" href="#topics">Start studying</a>
            <a className="btn ghost" href="#features">What's inside</a>
          </div>
        </section>

        <section id="features" className="section">
          <h2>What's inside</h2>
          <div className="cards">
            {features.map((f) => (
              <article className="card" key={f.title}>
                <span className="badge">Coming soon</span>
                <h3>{f.title}</h3>
                <p>{f.body}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="topics" className="section">
          <h2>Study areas</h2>
          <ul className="topics">
            {topics.map((t, i) => (
              <li key={t.name}>
                <span className="topic-num">{String(i + 1).padStart(2, '0')}</span>
                <div>
                  <strong>{t.name}</strong>
                  <span>{t.note}</span>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </main>

      <footer className="footer">
        <p>AAOIFI Prep is a personal study project and is not affiliated with AAOIFI.</p>
      </footer>
    </>
  )
}

export default App
