const rotation = { right: 0, down: 90, left: 180, up: 270 }

/** A small hand-drawn arrow that inherits the text colour. */
export default function Arrow({ dir = 'right', size = 16 }: { dir?: keyof typeof rotation; size?: number }) {
  return (
    <svg
      className="arrow-svg"
      viewBox="0 0 16 16"
      width={size}
      height={size}
      aria-hidden="true"
      style={{ transform: `rotate(${rotation[dir]}deg)` }}
    >
      <path d="M2.5 8h10M8.5 3.5 13 8l-4.5 4.5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
