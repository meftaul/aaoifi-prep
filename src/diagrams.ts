import { axisBottom, axisLeft, max, scaleBand, scaleLinear, select } from 'd3'

/** One run of text inside a label: bold flag and colour token. */
interface TextPart {
  t: string
  b?: 1
  c?: string
}

/** A diagram traced from the PDF: vector shapes plus centred text lines, in PDF points. */
interface VectorDiagram {
  type: 'vector'
  w: number
  h: number
  shapes: { d: string; fill?: string; stroke?: string; sw?: number; dash?: string }[]
  texts: { x: number; y: number; s: number; p: TextPart[] }[]
}

/** A chart rebuilt from its numbers. */
interface BarDiagram {
  type: 'bars'
  w: number
  h: number
  groups: string[]
  series: { name: string; tone: string; values: number[] }[]
  yLabel: string
  xLabel: string
}

export type DiagramSpec = VectorDiagram | BarDiagram

// Colour tokens resolve to CSS variables, so diagrams follow light and dark mode.
const fillVar = (t: string) => `var(--dgf-${t})`
const strokeVar = (t: string) => `var(--dgs-${t})`
const textVar = (t: string) => `var(--dgt-${t})`

const SVG_NS = 'http://www.w3.org/2000/svg'

function makeSvg(el: HTMLElement, w: number, h: number) {
  select(el).selectAll('*').remove()
  const svg = select(el)
    .append(() => document.createElementNS(SVG_NS, 'svg'))
    .attr('viewBox', `0 0 ${w} ${h}`)
    .attr('class', 'diagram-svg')
    .attr('aria-hidden', 'true')
  return svg
}

function drawVector(el: HTMLElement, spec: VectorDiagram) {
  const svg = makeSvg(el, spec.w, spec.h)

  svg
    .append('g')
    .selectAll('path')
    .data(spec.shapes)
    .join('path')
    .attr('d', (s) => s.d)
    .attr('fill', (s) => (s.fill ? fillVar(s.fill) : 'none'))
    .attr('stroke', (s) => (s.stroke ? strokeVar(s.stroke) : null))
    .attr('stroke-width', (s) => s.sw ?? null)
    .attr('stroke-dasharray', (s) => s.dash ?? null)
    .attr('stroke-linejoin', 'round')

  svg
    .append('g')
    .attr('class', 'diagram-text')
    .selectAll('text')
    .data(spec.texts)
    .join('text')
    .attr('x', (t) => t.x)
    .attr('y', (t) => t.y)
    .attr('font-size', (t) => t.s)
    .attr('text-anchor', 'middle')
    .selectAll('tspan')
    .data((t) => t.p)
    .join('tspan')
    .text((p) => p.t)
    .attr('font-weight', (p) => (p.b ? 700 : null))
    .attr('fill', (p) => textVar(p.c ?? 'ink'))
}

function drawBars(el: HTMLElement, spec: BarDiagram) {
  const { w, h } = spec
  const m = { top: 14, right: 16, bottom: 30, left: 58 }
  const svg = makeSvg(el, w, h)
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`)
  const iw = w - m.left - m.right
  const ih = h - m.top - m.bottom

  const yMax = max(spec.series.flatMap((s) => s.values)) ?? 0
  const x = scaleBand<string>().domain(spec.groups).range([0, iw]).padding(0.3)
  const xi = scaleBand<number>()
    .domain(spec.series.map((_, i) => i))
    .range([0, x.bandwidth()])
    .padding(0.12)
  const y = scaleLinear().domain([0, yMax]).nice().range([ih, 0])

  // grid + axes
  g.append('g')
    .attr('class', 'diagram-grid')
    .call(axisLeft(y).ticks(4).tickSize(-iw).tickFormat(() => ''))
    .call((a) => a.select('.domain').remove())
  g.append('g')
    .attr('class', 'diagram-axis')
    .call(axisLeft(y).ticks(4).tickSizeOuter(0))
  g.append('g')
    .attr('class', 'diagram-axis')
    .attr('transform', `translate(0,${ih})`)
    .call(axisBottom(x).tickSizeOuter(0))

  const groups = g
    .append('g')
    .selectAll('g')
    .data(spec.groups)
    .join('g')
    .attr('transform', (d) => `translate(${x(d)},0)`)

  const bars = groups
    .selectAll('g')
    .data((_, gi) => spec.series.map((s, si) => ({ si, tone: s.tone, v: s.values[gi], name: s.name })))
    .join('g')

  bars
    .append('rect')
    .attr('x', (d) => xi(d.si) ?? 0)
    .attr('width', xi.bandwidth())
    .attr('y', (d) => y(d.v))
    .attr('height', (d) => ih - y(d.v))
    .attr('rx', 1.5)
    .attr('fill', (d) => fillVar(d.tone))
    .append('title')
    .text((d) => `${d.name}: BDT ${d.v.toLocaleString('en-US')}`)

  bars
    .append('text')
    .attr('x', (d) => (xi(d.si) ?? 0) + xi.bandwidth() / 2)
    .attr('y', (d) => y(d.v) - 3)
    .attr('text-anchor', 'middle')
    .attr('font-size', 6)
    .attr('font-weight', 700)
    .attr('fill', (d) => textVar(d.tone))
    .text((d) => d.v.toLocaleString('en-US'))

  // axis titles
  g.append('text')
    .attr('transform', `translate(${-34},${ih / 2}) rotate(-90)`)
    .attr('text-anchor', 'middle')
    .attr('font-size', 6.5)
    .attr('fill', textVar('muted'))
    .text(spec.yLabel)
  g.append('text')
    .attr('x', iw / 2)
    .attr('y', ih + 24)
    .attr('text-anchor', 'middle')
    .attr('font-size', 6.5)
    .attr('fill', textVar('muted'))
    .text(spec.xLabel)

  // legend
  const legend = g
    .append('g')
    .attr('transform', 'translate(8,0)')
    .selectAll('g')
    .data(spec.series)
    .join('g')
    .attr('transform', (_, i) => `translate(0,${i * 11})`)
  legend
    .append('rect')
    .attr('width', 7)
    .attr('height', 7)
    .attr('rx', 1)
    .attr('fill', (s) => fillVar(s.tone))
  legend
    .append('text')
    .attr('x', 11)
    .attr('y', 6)
    .attr('font-size', 6.5)
    .attr('fill', textVar('ink'))
    .text((s) => s.name)
}

/** Draw every `<figure data-diagram>` inside `root` from its spec. */
export function drawDiagrams(root: HTMLElement, specs: Record<string, DiagramSpec>) {
  root.querySelectorAll<HTMLElement>('figure[data-diagram]').forEach((el) => {
    const spec = specs[el.dataset.diagram ?? '']
    if (!spec) return
    if (spec.type === 'bars') drawBars(el, spec)
    else drawVector(el, spec)
  })
}
