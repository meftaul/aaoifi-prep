import { useEffect, useState } from 'react'

type Theme = 'light' | 'dark'

const current = (): Theme => (document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light')

function stored(): Theme | null {
  try {
    const t = localStorage.getItem('theme')
    return t === 'light' || t === 'dark' ? t : null
  } catch {
    return null
  }
}

function apply(t: Theme, animate: boolean) {
  const root = document.documentElement
  if (animate) {
    root.classList.add('theme-anim')
    window.setTimeout(() => root.classList.remove('theme-anim'), 400)
  }
  root.dataset.theme = t
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(current)

  // Follow the OS setting until the reader picks a theme themselves.
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const onChange = () => {
      if (stored()) return
      const t: Theme = mq.matches ? 'dark' : 'light'
      apply(t, true)
      setTheme(t)
    }
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])

  const toggle = () => {
    const next: Theme = theme === 'dark' ? 'light' : 'dark'
    apply(next, true)
    setTheme(next)
    try {
      localStorage.setItem('theme', next)
    } catch {
      /* storage unavailable: theme still applies for this visit */
    }
  }

  const label = theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'
  return (
    <button type="button" className={`theme-toggle is-${theme}`} onClick={toggle} aria-label={label} title={label}>
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <g className="tt-sun">
          <circle cx="12" cy="12" r="4.2" />
          {[0, 45, 90, 135, 180, 225, 270, 315].map((a) => (
            <line key={a} x1="12" y1="2.5" x2="12" y2="5" transform={`rotate(${a} 12 12)`} />
          ))}
        </g>
        <path className="tt-moon" d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5a8.5 8.5 0 1 0 10.7 10.7Z" />
      </svg>
    </button>
  )
}
