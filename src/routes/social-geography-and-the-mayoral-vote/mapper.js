// Two linked maps of Toronto's census tracts — census variables and mayoral vote
// shares — with correlations between them. Ported from Zack Taylor's prototype
// (github.com/zacktayloruwo/toronto-elections-mapper); runs in the browser only,
// started from the page's onMount.

import { parquetReadObjects } from 'hyparquet'
import { interpolateRdBu } from 'd3'
import maplibregl, { createBaseMapStyle } from '$lib/maps/maplibre.js'
import Wards from '$data/wards.geo.json' // the 25 wards in use since the 2018 election

import metaUrl from './data/meta.json?url'
import tractsUrl from './data/tracts.geojson?url'
import censusUrl from './data/census.parquet?url'
import electionsUrl from './data/elections.parquet?url'
import turnoutUrl from './data/turnout.parquet?url'
// The 44 wards used for the 2000-2014 elections, and each tract's ward among them
// (see analysis/social_geography_and_the_mayoral_vote/README.md)
import wards2000Url from './data/wards-2000-2014.geojson?url'
import tractWards2000Url from './data/tract-wards-2000-2014.json?url'
// The city's outline, dissolved from the current wards
import cityUrl from './data/city-boundary.geojson?url'

// Quintile palettes, light to dark, ending in brand dark green and dark blue
const CENSUS_COLOURS = ['#e6f2ef', '#b3dbd2', '#6fbcae', '#2e8f80', '#0d534d']
const VOTE_COLOURS = ['#e8ebf5', '#b9c3e3', '#8698cc', '#4f64ad', '#1e3765']
const NA_COLOR = '#e6e6e1'

// Bivariate map: tertiles of the census variable (x, teal-blue) and the vote share
// (y, rust), meeting in dark aubergine where both are high. BIVARIATE[x + 3 * y],
// 0 = lowest third. Cells are blended from four corner colours. Blue against orange
// keeps the nine cells apart under red-green colour blindness (deuteranopia and
// protanopia), which a green against pink palette does not.
const BI_CORNERS = { low: '#f1efea', x: '#2f8a9e', y: '#c8643c', both: '#3a2e3a' }
const BIVARIATE = (() => {
  const rgb = (c) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16))
  const hex = (v) => `#${v.map((c) => Math.round(c).toString(16).padStart(2, '0')).join('')}`
  const [lo, hx, hy, hb] = ['low', 'x', 'y', 'both'].map((k) => rgb(BI_CORNERS[k]))
  const out = []
  for (let j = 0; j < 3; j++) {
    for (let i = 0; i < 3; i++) {
      const u = i / 2, w = j / 2
      out.push(hex(lo.map((_, k) => lo[k] * (1 - u) * (1 - w) + hx[k] * u * (1 - w) + hy[k] * (1 - u) * w + hb[k] * u * w)))
    }
  }
  return out
})()
const QUINTILES = 5

const BEARING = -17.1 // same rotation as the site's other maps
const FIT_PADDING = 16
const TOP_SHARE = 0.3
// How far the maps can be panned: the site maps' box around Toronto, made 10%
// larger (5% of its width and height added on each side) for a little more room
const PAN_BOX = [
  [-79.6772, 43.4400], // SW
  [-79.04763, 44.03074], // NE
]
const PAN_MARGIN = 0.05
const MAX_BOUNDS = (([[w, s], [e, n]]) => {
  const dx = (e - w) * PAN_MARGIN, dy = (n - s) * PAN_MARGIN
  return [[w - dx, s - dy], [e + dx, n + dy]]
})(PAN_BOX)
const FILL_OPACITY = 0.81
// Everything outside the city is faded by an "inverted polygon": a large box with
// the city cut out of it, filled white at this opacity (like QGIS's inverted polygons)
const OUTSIDE_FADE = 0.8

function outsideMask(city) {
  const box = [[-81, 42.5], [-77.5, 42.5], [-77.5, 45], [-81, 45], [-81, 42.5]]
  const holes = city.features.flatMap((f) =>
    f.geometry.type === 'Polygon' ? [f.geometry.coordinates[0]] : f.geometry.coordinates.map((poly) => poly[0]))
  return { type: 'Feature', properties: {}, geometry: { type: 'Polygon', coordinates: [box, ...holes] } }
}

// Street types drawn on the maps (Shortbread `streets` kinds); paths and service lanes are left out
const STREET_KINDS = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'living_street']
const WATER_COLOR = '#d6d5d1' // a little darker than the site basemap's #e6e4e0

// The site basemap, with lighter water for these maps only
function baseStyle() {
  const style = createBaseMapStyle()
  for (const layer of style.layers) {
    if (layer.id === 'water' || layer.id === 'ocean') layer.paint['fill-color'] = WATER_COLOR
  }
  return style
}
const HOVER_COLOR = '#F1C500' // --brandYellow

// Which ward boundaries match an election year. The 28 wards of the 1997 election
// aren't in the City's open data, so no wards are shown for it.
const wardSetFor = (year) => (year >= 2018 ? 'current' : year >= 2000 ? 'wards2000' : null)
const WARD_SETS = ['current', 'wards2000']

// Minimal element builder: h('div', {class: 'x'}, 'text', childEl, ...)
function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag)
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'style') Object.assign(el.style, v)
    else el.setAttribute(k, v)
  }
  el.append(...children.filter((c) => c != null))
  return el
}

async function loadParquet(url) {
  const buf = await (await fetch(url)).arrayBuffer()
  return parquetReadObjects({ file: buf })
}

// ---- Formatting --------------------------------------------------------------
const fmtPct = (v, d = 1) => `${(v * 100).toFixed(d)}%`
const fmtZ = (v) => `${v >= 0 ? '+' : '−'}${Math.abs(v).toFixed(2)} SD`
const fmtValue = (v, kind) => (v == null ? 'No data' : kind === 'z' ? fmtZ(v) : fmtPct(v))
const fmtCount = (v) => (v == null ? 'n/a' : Math.round(v).toLocaleString('en-CA'))

// ---- Classification ----------------------------------------------------------
// Breaks that split the tracts into `n` groups of (as near as ties allow) equal size.
// When many tracts share a value (often 0% for small groups), fewer groups are
// possible; a break at the minimum would leave an empty lowest group, so it's dropped.
function quantileBreaks(values, n) {
  const v = values.filter((x) => x != null && Number.isFinite(x)).sort((a, b) => a - b)
  if (!v.length) return []
  const breaks = []
  for (let i = 1; i < n; i++) {
    const q = v[Math.min(v.length - 1, Math.floor((i * v.length) / n))]
    if (q > v[0] && (!breaks.length || q > breaks[breaks.length - 1])) breaks.push(q)
  }
  return breaks
}

// Pick `k` colours spread evenly across a palette
function spread(palette, k) {
  if (k >= palette.length) return palette.slice()
  if (k === 1) return [palette[palette.length - 1]]
  return Array.from({ length: k }, (_, i) => palette[Math.round((i * (palette.length - 1)) / (k - 1))])
}

function colorExpression(breaks, colors) {
  const step = ['step', ['feature-state', 'v'], colors[0]]
  breaks.forEach((b, i) => step.push(b, colors[i + 1]))
  return ['case', ['!=', ['typeof', ['feature-state', 'v']], 'number'], NA_COLOR, step]
}

// A horizontal bar of the classes, with each break labelled once where two classes
// meet. "No data" is only shown when some tracts have none.
// It sits under the dropdowns, which already name the variable or candidate.
function renderLegend(el, subtitle, breaks, colors, fmt, hasMissing) {
  const n = colors.length
  const bar = h('div', { class: 'legend-bar' },
    ...colors.map((c) => h('span', { style: { background: c } })))
  const ticks = h('div', { class: 'legend-ticks' },
    ...breaks.map((b, i) => h('span', { style: { left: `${((i + 1) / n) * 100}%` } }, fmt(b))))
  el.replaceChildren(
    h('div', { class: 'legend-sub' }, subtitle),
    h('div', { class: 'legend-row' },
      h('div', { class: 'legend-scale' }, bar, ticks),
      hasMissing ? h('div', { class: 'legend-na' }, h('span', { class: 'swatch-na' }), 'No data') : null),
  )
}

// ---- Correlation -------------------------------------------------------------
// Regularized incomplete beta, for the two-sided p-value of Pearson's r
function betacf(a, b, x) {
  const tiny = 1e-30
  let qab = a + b, qap = a + 1, qam = a - 1, c = 1, d = 1 - (qab * x) / qap
  if (Math.abs(d) < tiny) d = tiny
  d = 1 / d
  let h = d
  for (let m = 1; m <= 200; m++) {
    const m2 = 2 * m
    let aa = (m * (b - m) * x) / ((qam + m2) * (a + m2))
    d = 1 + aa * d; if (Math.abs(d) < tiny) d = tiny
    c = 1 + aa / c; if (Math.abs(c) < tiny) c = tiny
    d = 1 / d
    h *= d * c
    aa = (-(a + m) * (qab + m) * x) / ((a + m2) * (qap + m2))
    d = 1 + aa * d; if (Math.abs(d) < tiny) d = tiny
    c = 1 + aa / c; if (Math.abs(c) < tiny) c = tiny
    d = 1 / d
    const del = d * c
    h *= del
    if (Math.abs(del - 1) < 3e-7) break
  }
  return h
}

function lgamma(z) {
  const g = [76.18009172947146, -86.50532032941677, 24.01409824083091,
    -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]
  let x = z, y = z, tmp = x + 5.5
  tmp -= (x + 0.5) * Math.log(tmp)
  let ser = 1.000000000190015
  for (let j = 0; j < 6; j++) ser += g[j] / ++y
  return -tmp + Math.log((2.5066282746310005 * ser) / x)
}

function ibeta(a, b, x) {
  if (x <= 0) return 0
  if (x >= 1) return 1
  const front = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) +
    a * Math.log(x) + b * Math.log(1 - x))
  return x < (a + 1) / (a + b + 2)
    ? (front * betacf(a, b, x)) / a
    : 1 - (front * betacf(b, a, 1 - x)) / b
}

// Pearson correlation over the tracts where both variables are present
function pearson(pairs) {
  const n = pairs.length
  if (n < 5) return null
  let sx = 0, sy = 0
  for (const [x, y] of pairs) { sx += x; sy += y }
  const mx = sx / n, my = sy / n
  let sxy = 0, sxx = 0, syy = 0
  for (const [x, y] of pairs) {
    const dx = x - mx, dy = y - my
    sxy += dx * dy; sxx += dx * dx; syy += dy * dy
  }
  if (sxx === 0 || syy === 0) return null
  const r = sxy / Math.sqrt(sxx * syy)
  const df = n - 2
  const t2 = (r * r * df) / Math.max(1e-12, 1 - r * r)
  const p = ibeta(df / 2, 0.5, df / (df + t2))   // two-sided
  return { r, n, p }
}

const fmtP = (p) => (p < 0.001 ? 'p < 0.001' : `p = ${p.toFixed(3)}`)
const fmtR = (r) => `${r < 0 ? '−' : '+'}${Math.abs(r).toFixed(2)}`

// ---- Maps --------------------------------------------------------------------
// Zoom in / zoom out / back to the whole city, in one control group
function navControl(map, fit) {
  return {
    onAdd() {
      const button = (cls, label, onClick) => {
        const b = h('button', { class: cls, type: 'button', title: label, 'aria-label': label },
          h('span', { class: 'maplibregl-ctrl-icon', 'aria-hidden': 'true' }))
        b.addEventListener('click', onClick)
        return b
      }
      return h('div', { class: 'maplibregl-ctrl maplibregl-ctrl-group' },
        button('maplibregl-ctrl-zoom-in', 'Zoom in', () => map.zoomIn()),
        button('maplibregl-ctrl-zoom-out', 'Zoom out', () => map.zoomOut()),
        button('ctrl-fit', 'Zoom out to the whole city', () => fit(true)))
    },
    onRemove() {},
  }
}

// The camera that fits the city's actual outline once rotated. (Fitting the
// north-up bounding box instead leaves wide margins: rotating the box pushes its
// corners well beyond the city.) Points are Web Mercator coordinates at zoom 0.
const WORLD = 512
const mercX = (lng) => ((lng + 180) / 360) * WORLD
const mercY = (lat) => ((180 - (180 / Math.PI) * Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360))) / 360) * WORLD
const mercLng = (x) => (x / WORLD) * 360 - 180
const mercLat = (y) => (360 / Math.PI) * Math.atan(Math.exp(((180 - (y / WORLD) * 360) * Math.PI) / 180)) - 90

function outlinePoints(tracts) {
  const pts = []
  const walk = (c) => (typeof c[0] === 'number' ? pts.push([mercX(c[0]), mercY(c[1])]) : c.forEach(walk))
  tracts.features.forEach((f) => walk(f.geometry.coordinates))
  return pts
}

function rotatedFit(points, width, height, padding) {
  const b = (BEARING * Math.PI) / 180, cos = Math.cos(b), sin = Math.sin(b)
  // map coordinates to screen orientation: with bearing b, the direction b is "up"
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity
  for (const [x, y] of points) {
    const rx = x * cos + y * sin, ry = -x * sin + y * cos
    if (rx < x0) x0 = rx
    if (rx > x1) x1 = rx
    if (ry < y0) y0 = ry
    if (ry > y1) y1 = ry
  }
  const zoom = Math.log2(Math.min((width - 2 * padding) / (x1 - x0), (height - 2 * padding) / (y1 - y0)))
  // Centre of the rotated extent, nudged so the city sits nearer the top: of the
  // spare height, TOP_SHARE goes above the city rather than half.
  const spare = (height - 2 * padding) / 2 ** zoom - (y1 - y0)
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2 + spare * (0.5 - TOP_SHARE)
  const mx = cx * cos - cy * sin, my = cx * sin + cy * cos
  return { center: [mercLng(mx), mercLat(my)], zoom }
}

function makeMap(container, tracts, bounds, wardData, city) {
  const map = new maplibregl.Map({
    container,
    style: baseStyle(),
    bounds,
    fitBoundsOptions: { padding: FIT_PADDING, bearing: BEARING },
    bearing: BEARING,
    maxBounds: MAX_BOUNDS,
    dragRotate: false,
    pitchWithRotate: false,
    touchPitch: false,
    attributionControl: false, // credited in the data note under the maps instead
  })
  map.touchZoomRotate.disableRotation()
  map.scrollZoom.disable()

  // The whole city, rotated to match the site's other maps
  const outline = outlinePoints(tracts)
  const cityCamera = () => {
    const el = map.getContainer()
    if (!el.clientWidth || !el.clientHeight) return null
    return rotatedFit(outline, el.clientWidth, el.clientHeight, FIT_PADDING)
  }
  const fit = (animate) => {
    const cam = cityCamera()
    if (!cam) return
    const view = { center: cam.center, zoom: cam.zoom, bearing: BEARING }
    if (animate) map.easeTo(view)
    else map.jumpTo(view)
  }
  map.addControl(navControl(map, fit), 'top-right')

  // Never zoom out past the whole city, which depends on the map's size
  const limitZoom = () => {
    const cam = cityCamera()
    if (cam) map.setMinZoom(cam.zoom - 0.01)
  }

  const ready = new Promise((resolve) => {
    map.on('load', () => {
      limitZoom()
      fit(false)
      map.addSource('tracts', { type: 'geojson', data: tracts, promoteId: 'ct' })
      for (const set of WARD_SETS) map.addSource(set, { type: 'geojson', data: wardData[set] })
      map.addSource('city', { type: 'geojson', data: city })
      map.addSource('outside', { type: 'geojson', data: outsideMask(city) })
      map.addLayer({
        id: 'fill',
        type: 'fill',
        source: 'tracts',
        paint: { 'fill-color': NA_COLOR, 'fill-opacity': FILL_OPACITY },
      })
      // Thin mid grey streets from the basemap's OpenStreetMap tiles, drawn under the
      // tract colours; minor streets appear as you zoom in
      map.addLayer({
        id: 'streets',
        type: 'line',
        source: 'osm',
        'source-layer': 'streets',
        filter: ['in', ['get', 'kind'], ['literal', STREET_KINDS]],
        layout: { 'line-cap': 'round', 'line-join': 'round' },
        paint: {
          'line-color': '#6e6e6e',
          'line-width': ['interpolate', ['linear'], ['zoom'],
            10, ['match', ['get', 'kind'], ['motorway', 'trunk'], 0.8, ['primary', 'secondary'], 0.5, 0.25],
            15, ['match', ['get', 'kind'], ['motorway', 'trunk'], 2.4, ['primary', 'secondary'], 1.6, 0.9]],
        },
      }, 'fill')
      map.addLayer({
        id: 'outside',
        type: 'fill',
        source: 'outside',
        paint: { 'fill-color': '#ffffff', 'fill-opacity': OUTSIDE_FADE },
      })
      map.addLayer({
        id: 'outline',
        type: 'line',
        source: 'tracts',
        paint: { 'line-color': '#ffffff', 'line-width': 0.5, 'line-opacity': 0.9 },
      })
      // one pair of ward lines per boundary set; setWards() shows the one for the election year
      for (const set of WARD_SETS) {
        map.addLayer({
          id: `${set}-white`,
          type: 'line',
          source: set,
          layout: { visibility: 'none' },
          paint: { 'line-color': '#ffffff', 'line-width': 3 },
        })
        map.addLayer({
          id: `${set}-black`,
          type: 'line',
          source: set,
          layout: { visibility: 'none' },
          paint: { 'line-color': '#000000', 'line-width': 1 },
        })
      }
      // the city boundary, over the ward lines and a little heavier, shown for every year
      map.addLayer({
        id: 'city-white',
        type: 'line',
        source: 'city',
        paint: { 'line-color': '#ffffff', 'line-width': 4.5 },
      })
      map.addLayer({
        id: 'city-black',
        type: 'line',
        source: 'city',
        paint: { 'line-color': '#000000', 'line-width': 1.5 },
      })
      map.addLayer({
        id: 'hover',
        type: 'line',
        source: 'tracts',
        paint: {
          'line-color': HOVER_COLOR,
          'line-width': ['case', ['boolean', ['feature-state', 'hover'], false], 3, 0],
        },
      })
      resolve(map)
    })
  })
  const setWards = (shown) => {
    for (const set of WARD_SETS) {
      for (const layer of [`${set}-white`, `${set}-black`]) {
        map.setLayoutProperty(layer, 'visibility', set === shown ? 'visible' : 'none')
      }
    }
  }

  return { map, ready, fit, limitZoom, setWards }
}

// Keep the whole city in view across resizes. The maps are synced, so all their
// zoom floors are updated before refitting; otherwise the map that hasn't resized
// yet clamps the synced view to its old, larger floor.
function fitOnResize(maps) {
  const [lead] = maps
  let showingCity = true
  lead.map.on('moveend', () => { showingCity = lead.map.getZoom() - lead.map.getMinZoom() < 0.02 })
  let queued = false
  const onResize = () => {
    if (queued) return
    queued = true
    const wasShowingCity = showingCity
    requestAnimationFrame(() => {
      queued = false
      maps.forEach((m) => m.limitZoom())
      if (wasShowingCity) lead.fit(false)
    })
  }
  maps.forEach((m) => m.map.on('resize', onResize))
}

// Moving any of the maps moves the others to match
function syncMaps(maps) {
  let syncing = false
  for (const src of maps) {
    src.on('move', () => {
      if (syncing) return
      syncing = true
      for (const dst of maps) if (dst !== src) dst.jumpTo({ center: src.getCenter(), zoom: src.getZoom() })
      syncing = false
    })
  }
}

// ---- App ---------------------------------------------------------------------
// `root` is the page element holding the controls; `replaceHash` writes the view
// to the URL hash so it can be shared. Returns a function that tears everything down.
export async function startMapper(root, { replaceHash }) {
  const $ = (id) => root.querySelector(`#${id}`)
  const cleanup = []

  const [meta, tracts, censusRows, electionRows, turnoutRows, wards2000, tractWards2000, city] = await Promise.all([
    fetch(metaUrl).then((r) => r.json()),
    fetch(tractsUrl).then((r) => r.json()),
    loadParquet(censusUrl),
    loadParquet(electionsUrl),
    loadParquet(turnoutUrl),
    fetch(wards2000Url).then((r) => r.json()),
    fetch(tractWards2000Url).then((r) => r.json()),
    fetch(cityUrl).then((r) => r.json()),
  ])
  const wards2000Name = new Map(wards2000.features.map((f) => [f.properties.num, f.properties.name]))

  const tractIds = tracts.features.map((f) => f.properties.ct)
  const tractName = new Map(tracts.features.map((f) => [f.properties.ct, f.properties.name]))
  const tractGeog = new Map(tracts.features.map((f) => [f.properties.ct, f.properties]))

  // census: year -> ct -> row ; elections: "year|cand" -> ct -> {share, votes}
  const censusByYear = new Map()
  for (const r of censusRows) {
    if (!censusByYear.has(r.year)) censusByYear.set(r.year, new Map())
    censusByYear.get(r.year).set(r.ct, r)
  }
  const elections = new Map()
  for (const r of electionRows) {
    const key = `${r.year}|${r.candidate}`
    if (!elections.has(key)) elections.set(key, new Map())
    elections.get(key).set(r.ct, { share: r.share, votes: r.votes })
  }
  // Denominators per tract and election: "year|ct" -> {votes_cast, eligible}
  const turnout = new Map(turnoutRows.map((r) =>
    [`${r.year}|${r.ct}`, { cast: r.votes_cast, eligible: r.eligible }]))

  // Category names as shown on the page: sentence case, "and" rather than "&"
  const GROUP_NAMES = {
    'Age & Family': 'Age and family',
    'Commuting': 'Commuting',
    'Density, Location & Access': 'Location and access (2021)',
    'Education & Labour Force': 'Education and labour force',
    'Ethnic Origin': 'Ethnic origin',
    'Housing': 'Housing',
    'Immigration & Language': 'Immigration and language',
    'Income': 'Income',
    'Occupation': 'Occupation',
    'Religion': 'Religion',
    'Visible Minority & Indigenous Identity': 'Visible minority and Indigenous identity',
  }
  for (const v of meta.variables) v.group = GROUP_NAMES[v.group] ?? v.group
  // Population density stands on its own at the top (no category); location and
  // access goes last, in the dropdowns and the correlation table
  const DENSITY = 's_popdsqkm__nc'
  const LAST_GROUP = GROUP_NAMES['Density, Location & Access']
  meta.variables.find((v) => v.id === DENSITY).group = ''
  meta.variables = [
    ...meta.variables.filter((v) => v.id === DENSITY),
    ...meta.variables.filter((v) => v.id !== DENSITY && v.group !== LAST_GROUP),
    ...meta.variables.filter((v) => v.group === LAST_GROUP),
  ]
  const varById = new Map(meta.variables.map((v) => [v.id, v]))
  const electionByYear = new Map(meta.elections.map((e) => [e.year, e]))

  // Bounds of all tracts
  let [minX, minY, maxX, maxY] = [Infinity, Infinity, -Infinity, -Infinity]
  const walk = (c) => {
    if (typeof c[0] === 'number') {
      minX = Math.min(minX, c[0]); maxX = Math.max(maxX, c[0])
      minY = Math.min(minY, c[1]); maxY = Math.max(maxY, c[1])
    } else c.forEach(walk)
  }
  tracts.features.forEach((f) => walk(f.geometry.coordinates))
  const bounds = [[minX, minY], [maxX, maxY]]

  // ---- State (initialised from URL hash, so views can be shared) ----
  // every census variable is offered (the prototype's curated short list isn't used)
  const state = { cvar: 'jwmdauto_pct', cyear: 2011, eyear: 2010, ecand: 'ford', eall: false }  // % Car Commute (2011 census), Rob Ford 2010
  const hash = new URLSearchParams(location.hash.slice(1))
  if (varById.has(hash.get('cvar'))) state.cvar = hash.get('cvar')
  if (hash.get('cyear')) state.cyear = +hash.get('cyear')
  if (electionByYear.has(+hash.get('eyear'))) state.eyear = +hash.get('eyear')
  if (hash.get('ecand')) state.ecand = hash.get('ecand')
  if (hash.get('eall') === '1') state.eall = true

  const writeHash = () => {
    const p = new URLSearchParams({
      cvar: state.cvar, cyear: state.cyear,
      eyear: state.eyear, ecand: state.ecand, eall: state.eall ? 1 : 0,
    })
    replaceHash(`#${p}`)
  }

  // ---- Controls ----
  const selVar = $('census-var'), selCYear = $('census-year')
  const selCand = $('election-cand'), selEYear = $('election-year')

  // Copies of the top dropdowns sit above the bivariate map and above the
  // correlation table, so choices can be changed without scrolling back up. They
  // copy the top dropdowns' options and values, and pass their changes on to them.
  const mirrors = [
    [selVar, $('census-var-2')], [selCYear, $('census-year-2')],
    [selCand, $('election-cand-2')], [selEYear, $('election-year-2')],
    [selCand, $('election-cand-3')], [selCYear, $('census-year-3')],
    [selCand, $('election-cand-4')],
  ]
  function syncMirrors() {
    for (const [src, copy] of mirrors) {
      copy.replaceChildren(...[...src.children].map((c) => c.cloneNode(true)))
      copy.value = src.value
      copy.disabled = src.disabled
    }
    $('census-year-field-2').hidden = $('census-year-field').hidden
    // every "which candidates" toggle shows the current choice
    for (const r of root.querySelectorAll('.cand-scope input')) r.checked = (r.value === '1') === state.eall
  }

  // Proximity measures are 2021 data shown beside every census and election, so
  // their names say so in the dropdowns and the correlation table
  const listLabel = (v) => (v.id.startsWith('s_pmi_') ? `${v.label} (2021)` : v.label)

  function fillVarSelect() {
    const groups = new Map()
    for (const v of meta.variables) {
      if (!groups.has(v.group)) groups.set(v.group, [])
      groups.get(v.group).push(v)
    }
    // variables without a category (population density) sit above the groups
    selVar.replaceChildren(...[...groups].flatMap(([g, vs]) => g
      ? [h('optgroup', { label: g }, ...vs.map((v) => new Option(listLabel(v), v.id)))]
      : vs.map((v) => new Option(listLabel(v), v.id))))
    selVar.value = state.cvar
  }

  function fillCensusYears() {
    const v = varById.get(state.cvar)
    selCYear.replaceChildren(...v.years.map((y) => new Option(y, y)))
    if (!v.years.includes(state.cyear)) state.cyear = v.years[v.years.length - 1]
    selCYear.value = state.cyear
    // Scores, proximity measures and distance are measured once, not per census
    $('census-year-field').hidden = v.fixed_in_time
  }

  // Candidates are matched across elections by full name, since the column id
  // can differ between years (e.g. "tory" vs "tory_john").
  const people = new Map() // label -> [{ year, id }], ascending by year
  for (const e of meta.elections) {
    for (const c of e.candidates) {
      if (!people.has(c.label)) people.set(c.label, [])
      people.get(c.label).push({ year: e.year, id: c.id })
    }
  }

  const currentPerson = () =>
    electionByYear.get(state.eyear)?.candidates.find((c) => c.id === state.ecand)?.label

  // Default to the top candidate of the latest election if the hash is invalid
  if (!currentPerson()) {
    const latest = meta.elections[meta.elections.length - 1]
    if (!electionByYear.has(state.eyear)) state.eyear = latest.year
    state.ecand = electionByYear.get(state.eyear).candidates[0].id
  }

  // Everyone in the data took at least 1% of the citywide vote; the short list is
  // those who took more than 2%.
  function candidatesFor(year) {
    const all = electionByYear.get(year).candidates
    if (state.eall) return all
    const short = all.filter((c) => c.city_share > 0.02)
    // never hide the current selection
    const selected = all.find((c) => c.id === state.ecand)
    if (year === state.eyear && selected && !short.includes(selected)) short.push(selected)
    return short
  }

  const electionYears = meta.elections.map((e) => e.year).sort((a, b) => b - a)

  // Candidates grouped by election year, newest first
  function fillCandSelect() {
    selCand.replaceChildren(...electionYears.map((y) =>
      h('optgroup', { label: y },
        // the year is in the name too, since a closed dropdown doesn't show its group
        ...candidatesFor(y).map((c) => new Option(`${c.label} (${y})`, `${y}|${c.id}`)))))
    selCand.value = `${state.eyear}|${state.ecand}`
  }

  // Restrict the year list to the elections the selected candidate ran in
  function fillYearSelect() {
    const runs = people.get(currentPerson())
      .filter((r) => r.year === state.eyear || candidatesFor(r.year).some((c) => c.id === r.id))
    selEYear.replaceChildren(...runs.map((r) => new Option(r.year, r.year)))
    selEYear.value = state.eyear
    selEYear.disabled = runs.length === 1
  }

  function fillElectionControls() {
    fillCandSelect()
    fillYearSelect()
  }

  fillVarSelect()
  fillCensusYears()
  fillElectionControls()

  // ---- Maps ----
  const wardData = { current: Wards, wards2000 }
  const left = makeMap($('map-census'), tracts, bounds, wardData, city)
  const right = makeMap($('map-election'), tracts, bounds, wardData, city)
  const bi = makeMap($('map-bi'), tracts, bounds, wardData, city)
  const allMaps = [left, right, bi]
  cleanup.push(() => allMaps.forEach((m) => m.map.remove()))
  await Promise.all(allMaps.map((m) => m.ready))
  syncMaps(allMaps.map((m) => m.map))
  fitOnResize(allMaps)
  bi.map.setPaintProperty('fill', 'fill-opacity', 0.91)
  bi.map.setPaintProperty('fill', 'fill-color', ['case',
    ['!=', ['typeof', ['feature-state', 'bi']], 'number'], NA_COLOR,
    ['match', ['feature-state', 'bi'], ...BIVARIATE.flatMap((c, k) => [k, c]), NA_COLOR]])
  $('loading').hidden = true

  const current = { census: new Map(), election: new Map() }

  // updateCensus/updateElection both fire on one interaction; recompute once
  let corrQueued = false
  const updateCorrelationsLater = () => {
    if (corrQueued) return
    corrQueued = true
    queueMicrotask(() => { corrQueued = false; updateCorrelations() })
  }

  function censusValues(year) {
    const rows = censusByYear.get(year)
    return new Map(tractIds.map((ct) => [ct, rows?.get(ct)?.[state.cvar] ?? null]))
  }

  function updateCensus() {
    const v = varById.get(state.cvar)
    const values = censusValues(state.cyear)
    current.census = values

    const breaks = quantileBreaks([...values.values()], QUINTILES)
    const colors = spread(CENSUS_COLOURS, breaks.length + 1)

    for (const [ct, val] of values) left.map.setFeatureState({ source: 'tracts', id: ct }, { v: val })
    left.map.setPaintProperty('fill', 'fill-color', colorExpression(breaks, colors))
    left.map.getCanvas().setAttribute('aria-label',
      `Map of ${v.label}${v.fixed_in_time ? '' : ` (${state.cyear} census)`} by census tract, shaded in quintiles`)

    const fmt = v.kind === 'z' ? (x) => `${x > 0 ? '+' : x < 0 ? '−' : ''}${Math.abs(x).toFixed(2)}` : (x) => fmtPct(x, 1)
    renderLegend($('legend-census'),
      v.kind === 'z' ? 'SD from the mean tract, quintiles' : 'Quintiles of tracts',
      breaks, colors, fmt, [...values.values()].some((x) => x == null))

    const vals = [...values.values()].filter((x) => x != null).sort((a, b) => a - b)
    const median = vals.length ? vals[Math.floor(vals.length / 2)] : null
    updateCorrelationsLater()
    // the variable and year are already in the dropdowns, so the note only adds the stat
    $('census-note').replaceChildren(...(
      v.fixed_in_time
        ? ['Measured once, not by census year. Standard deviations from the tract mean.']
        : v.kind === 'z'
          ? ['Standard deviations from the tract mean for that census year.']
          : ['Median tract: ', h('strong', {}, median == null ? 'n/a' : fmtPct(median))]
    ))
    writeHash()
    syncMirrors()
  }

  function updateElection() {
    const e = electionByYear.get(state.eyear)
    const cand = e.candidates.find((c) => c.id === state.ecand)
    const rows = elections.get(`${state.eyear}|${state.ecand}`) ?? new Map()
    const values = new Map(tractIds.map((ct) => [ct, rows.get(ct)?.share ?? null]))
    current.election = values
    current.electionVotes = new Map(tractIds.map((ct) => [ct, rows.get(ct)?.votes ?? null]))

    const breaks = quantileBreaks([...values.values()], QUINTILES)
    const colors = spread(VOTE_COLOURS, breaks.length + 1)

    for (const [ct, val] of values) right.map.setFeatureState({ source: 'tracts', id: ct }, { v: val })
    right.map.setPaintProperty('fill', 'fill-color', colorExpression(breaks, colors))
    right.map.getCanvas().setAttribute('aria-label',
      `Map of ${cand.label}'s ${state.eyear} vote share by census tract, shaded in quintiles`)
    renderLegend($('legend-election'), 'Vote share, quintiles of tracts',
      breaks, colors, (x) => fmtPct(x, 1), [...values.values()].some((x) => x == null))

    // both maps show the ward boundaries of the selected election
    for (const m of allMaps) m.setWards(wardSetFor(state.eyear))

    updateCorrelationsLater()
    $('election-note').replaceChildren(
      'Citywide share, election day: ', h('strong', {}, fmtPct(cand.city_share)),
      ` (${fmtCount(cand.city_votes)} of ${fmtCount(e.city_votes_cast)} votes)`,
    )
    writeHash()
    syncMirrors()
  }

  // ---- Linked hover ----
  // Second line of the census readout: the counts behind a share, or the
  // nominal value behind a z-score.
  const NOMINAL = {
    dollars: (x) => `$${Math.round(x).toLocaleString('en-CA')}`,
    per_km2: (x) => `${fmtCount(x)} people per km²`,
    km: (x) => `${x.toFixed(1)} km`,
    index: (x) => `Index ${x.toFixed(3)} (0–1)`,
  }

  function censusDetail(v, ct) {
    const row = censusByYear.get(state.cyear)?.get(ct)
    if (!row) return null
    if (v.kind === 'z') {
      const nom = row[v.nom]
      return nom == null ? null : NOMINAL[v.unit](nom)
    }
    const num = row[v.num]
    const den = row[v.den]
    if (num == null || den == null) return null
    return `${fmtCount(num)} / ${fmtCount(den)}`
  }

  // The tract's ward in the boundaries of the selected election
  function wardLabel(ct, g) {
    const set = wardSetFor(state.eyear)
    if (set === 'current') return g.ward ? `Ward ${+g.ward} ${g.wardname}` : ''
    if (set === 'wards2000') {
      const num = tractWards2000[ct]
      return num ? `Ward ${num} ${wards2000Name.get(num)}` : ''
    }
    return ''
  }

  let hovered = null
  // The tract's name and place lines, shared by all the hover boxes
  const tractLines = (ct) => {
    const g = tractGeog.get(ct) ?? {}
    return [
      h('div', { class: 'ct' }, `Tract ${tractName.get(ct) ?? ct}`),
      h('div', { class: 'place' }, [g.nname, g.oldcity].filter(Boolean).join(' · ')),
      h('div', { class: 'place' }, wardLabel(ct, g)),
    ]
  }

  // `aside` (e.g. "451 / 1,294") sits to the right of the big value; `detail` lines go below
  function readout(el, ct, label, value, aside, ...detail) {
    el.replaceChildren(
      ...tractLines(ct),
      h('div', {}, label),
      h('div', { class: 'val-row' }, h('span', { class: 'val' }, value), aside ? h('span', { class: 'aside' }, aside) : null),
      ...detail.filter(Boolean).map((d) => h('div', { class: 'detail' }, d)),
    )
    el.hidden = false
  }

  function setHover(ct) {
    if (ct === hovered) return
    for (const { map: m } of allMaps) {
      if (hovered) m.setFeatureState({ source: 'tracts', id: hovered }, { hover: false })
      if (ct) m.setFeatureState({ source: 'tracts', id: ct }, { hover: true })
    }
    hovered = ct
    highlightDot(ct)
    if (!ct) {
      for (const id of ['readout-census', 'readout-election', 'readout-bi']) $(id).hidden = true
      return
    }
    const v = varById.get(state.cvar)
    const cand = electionByYear.get(state.eyear).candidates.find((c) => c.id === state.ecand)
    readout($('readout-census'), ct, v.fixed_in_time ? v.label : `${v.label}, ${state.cyear}`,
      fmtValue(current.census.get(ct), v.kind), censusDetail(v, ct))
    const votes = current.electionVotes.get(ct)
    const den = turnout.get(`${state.eyear}|${ct}`)
    readout($('readout-election'), ct, `${cand.label}, ${state.eyear}`,
      fmtValue(current.election.get(ct), 'pct'),
      votes == null ? null : `${fmtCount(votes)} / ${fmtCount(den?.cast)}`,  // beside the value
      den?.eligible == null ? null
        : `Election-day turnout ${fmtPct(den.cast / den.eligible, 0)} of ${fmtCount(den.eligible)} eligible`)
    // the bivariate map's box shows both values, a size down from the other maps' boxes
    $('readout-bi').replaceChildren(
      ...tractLines(ct),
      h('div', { class: 'pair-row' },
        h('div', {}, h('div', {}, v.fixed_in_time ? v.label : `${v.label}, ${state.cyear}`),
          h('div', { class: 'val-md' }, fmtValue(current.census.get(ct), v.kind))),
        h('div', {}, h('div', {}, `${cand.label}, ${state.eyear}`),
          h('div', { class: 'val-md' }, fmtValue(current.election.get(ct), 'pct')))),
    )
    $('readout-bi').hidden = false
  }

  for (const { map: m } of allMaps) {
    m.on('mousemove', 'fill', (ev) => {
      m.getCanvas().style.cursor = 'crosshair'
      setHover(ev.features[0]?.id ?? null)
    })
    m.on('mouseleave', 'fill', () => {
      m.getCanvas().style.cursor = ''
      setHover(null)
    })
  }

  const refreshHover = () => { const ct = hovered; hovered = null; setHover(ct) }

  // ---- Correlations ----
  const svgNS = 'http://www.w3.org/2000/svg'
  const s = (tag, attrs = {}, ...kids) => {
    const el = document.createElementNS(svgNS, tag)
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v)
    el.append(...kids.filter((x) => x != null))
    return el
  }

  // Charts are drawn to fill whatever width flex gave their container
  const widthOf = (id) => Math.max(180, Math.floor($(id).clientWidth) - 2)

  // Vote share against one census variable, over tracts holding both
  function pairsFor(varId) {
    const rows = censusByYear.get(state.cyear)
    const out = []
    for (const ct of tractIds) {
      const x = rows?.get(ct)?.[varId]
      const y = current.election.get(ct)
      if (x != null && y != null) out.push([x, y, ct])
    }
    return out
  }

  // Vote share against the census variable, one dot per tract, drawn W x H. The
  // dots' screen positions are kept on the svg for hover lookups.
  // `classes` ({ bx, by }: the bivariate map's tertile breaks) shades the plot behind
  // the dots in the same 3 x 3 colours as the map.
  function scatter(pairs, v, stat, W, H, classes) {   // stat drawn inside the plot area
    // standard-deviation variables get a second line under the axis title saying so
    const unitNote = v.kind === 'z' ? 'standard deviations from the tract mean' : null
    const m = { l: 56, r: 12, t: 10, b: unitNote ? 60 : 46 }
    if (!pairs.length) return s('svg', { width: W, height: H, role: 'img' })
    const xs = pairs.map((p) => p[0]), ys = pairs.map((p) => p[1])
    // Axes start at 0% rather than at the lowest tract; standard-deviation variables
    // go below zero, so theirs start at the data's minimum
    const xMin = Math.min(...xs), x1 = Math.max(...xs), y1 = Math.max(...ys)
    const x0 = v.kind === 'z' ? xMin : Math.min(0, xMin), y0 = Math.min(0, ...ys)
    const sx = (x) => m.l + ((x - x0) / (x1 - x0 || 1)) * (W - m.l - m.r)
    const sy = (y) => H - m.b - ((y - y0) / (y1 - y0 || 1)) * (H - m.t - m.b)
    const tick = (x, y, text, anchor) => s('text', { x, y, 'text-anchor': anchor, class: 'ax' }, text)
    const fmtX = (x) => (v.kind === 'z' ? x.toFixed(1) : fmtPct(x, 0))
    // trim an axis title that would run past the plot
    const fit = (text, px) => (text.length * 5.6 <= px ? text : `${text.slice(0, Math.max(6, Math.floor(px / 5.6) - 1))}…`)

    // least-squares line through the cloud
    const n = pairs.length
    const mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n
    let sxy = 0, sxx = 0
    for (const [x, y] of pairs) { sxy += (x - mx) * (y - my); sxx += (x - mx) ** 2 }
    const slope = sxx ? sxy / sxx : 0
    // drawn across the data only, not extended to the axis
    const line = s('line', {
      x1: sx(xMin), y1: sy(my + slope * (xMin - mx)), x2: sx(x1), y2: sy(my + slope * (x1 - mx)),
      class: 'fit',
    })


    // one rectangle per bivariate class, between the tertile cuts on each axis
    const bands = (lo, hi, br) => {
      const edges = [lo, ...br.filter((b) => b > lo && b < hi), hi]
      return edges.slice(1).map((e, k) => ({ from: edges[k], to: e, cls: br.length ? Math.round((k * 2) / br.length) : 0 }))
    }
    const background = classes ? bands(x0, x1, classes.bx).flatMap((bxk) => bands(y0, y1, classes.by).map((byk) =>
      s('rect', {
        x: sx(bxk.from), y: sy(byk.to), width: Math.max(0, sx(bxk.to) - sx(bxk.from)),
        height: Math.max(0, sy(byk.from) - sy(byk.to)), fill: BIVARIATE[bxk.cls + 3 * byk.cls], class: 'band',
      }))) : []

    const svg = s('svg', { width: W, height: H, role: 'img' },
      ...background,
      s('line', { x1: m.l, y1: H - m.b, x2: W - m.r, y2: H - m.b, class: 'axis' }),
      s('line', { x1: m.l, y1: m.t, x2: m.l, y2: H - m.b, class: 'axis' }),
      ...pairs.map(([x, y, ct]) => s('circle', { cx: sx(x).toFixed(1), cy: sy(y).toFixed(1), r: 2.4, class: 'pt', 'data-ct': ct })),
      stat && stat.p < 0.05 ? line : null,
      tick(m.l, H - m.b + 16, fmtX(x0), 'start'),
      tick(W - m.r, H - m.b + 16, fmtX(x1), 'end'),
      tick(m.l - 6, sy(y0), fmtPct(y0, 0), 'end'),
      tick(m.l - 6, sy(y1) + 10, fmtPct(y1, 0), 'end'),
      // axis titles
      s('text', {
        x: m.l + (W - m.l - m.r) / 2, y: unitNote ? H - 22 : H - 8, 'text-anchor': 'middle', class: 'axlab',
      }, fit(v.label, W - m.l - m.r)),
      unitNote ? s('text', { x: m.l + (W - m.l - m.r) / 2, y: H - 8, 'text-anchor': 'middle', class: 'ax' }, unitNote) : null,
      // horizontal, on two lines, beside the middle of the axis (the ticks are only at its ends)
      s('text', { x: m.l - 14, y: m.t + (H - m.b - m.t) / 2 - 2, 'text-anchor': 'end', class: 'axlab' }, 'Vote'),
      s('text', { x: m.l - 14, y: m.t + (H - m.b - m.t) / 2 + 12, 'text-anchor': 'end', class: 'axlab' }, 'share'))
    svg.points = pairs.map(([x, y, ct]) => ({ ct, px: sx(x), py: sy(y) }))
    return svg
  }

  // Outline the hovered tract's dot, drawn last so it sits on top of the others
  function highlightDot(ct) {
    const svg = $('scatter-big').querySelector('svg')
    if (!svg) return
    svg.querySelectorAll('circle.hl').forEach((c) => { c.classList.remove('hl'); c.setAttribute('r', 2.4) })
    const dot = ct && svg.querySelector(`circle[data-ct="${ct}"]`)
    if (!dot) return
    dot.classList.add('hl')
    dot.setAttribute('r', 5)
    dot.parentNode.append(dot)
  }

  function updateScatter() {
    const v = varById.get(state.cvar)
    const cand = electionByYear.get(state.eyear).candidates.find((c) => c.id === state.ecand)
    const pairs = pairsFor(state.cvar)
    const el = $('scatter-big')
    const stat = pearson(pairs)
    // r, p and the number of tracts, as a line of text above the plot
    $('scatter-stat').replaceChildren(...(!stat ? ['Not enough data'] : [
      h('strong', {}, `r = ${fmtR(stat.r)}`),
      ` · ${fmtP(stat.p)} · ${stat.n} tracts${stat.p < 0.05 ? '' : ' · not significant'}`,
    ]))
    const size = Math.max(220, el.clientWidth)
    const plot = scatter(pairs, v, stat, size, size, biClasses)
    // what the plot shows, for screen readers
    const censusYear = v.fixed_in_time ? '' : ` (${state.cyear} census)`
    const rText = !stat ? 'not enough data for a correlation'
      : `r = ${fmtR(stat.r)}, ${fmtP(stat.p)}, ${stat.n} tracts${stat.p < 0.05 ? '' : ', not significant'}`
    plot.setAttribute('aria-label',
      `Scatter plot of ${cand.label}'s ${state.eyear} vote share against ${v.label}${censusYear}, one dot per census tract: ${rText}`)
    el.replaceChildren(plot)
    highlightDot(hovered)
    announce(`Showing ${v.label}${censusYear} and ${cand.label}'s ${state.eyear} vote share: ${rText}`)
  }

  // Tell screen readers what's now shown, through a polite live region, when the
  // selection changes. Not on the first draw, and not on redraws for a resize,
  // where the text is unchanged.
  let lastAnnounced = null
  function announce(text) {
    if (lastAnnounced !== null && text !== lastAnnounced) $('live-status').textContent = text
    lastAnnounced = text
  }

  // Hovering the scatter picks the nearest dot within a few pixels
  const scatterEl = $('scatter-big')
  const nearestDot = (ev) => {
    const svg = scatterEl.querySelector('svg')
    if (!svg?.points) return null
    const r = svg.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top
    let best = null, bestD = 8 * 8
    for (const p of svg.points) {
      const d = (p.px - x) ** 2 + (p.py - y) ** 2
      if (d < bestD) { bestD = d; best = p.ct }
    }
    return best
  }

  let biClasses = null
  function updateBivariate() {
    const tertile = (x, br) => {
      if (x == null) return null
      let k = 0
      while (k < br.length && x >= br[k]) k++
      // with heavy ties there are fewer than three classes; spread them over 0-2
      return br.length ? Math.round((k * 2) / br.length) : 0
    }
    const bx = quantileBreaks([...current.census.values()], 3)
    const by = quantileBreaks([...current.election.values()], 3)
    biClasses = { bx, by }
    for (const ct of tractIds) {
      const i = tertile(current.census.get(ct), bx), j = tertile(current.election.get(ct), by)
      bi.map.setFeatureState({ source: 'tracts', id: ct }, { bi: i == null || j == null ? null : i + 3 * j })
    }
    const v = varById.get(state.cvar)
    const cand = electionByYear.get(state.eyear).candidates.find((c) => c.id === state.ecand)
    // One key for both the map and the scatter behind it: 3 x 3, low-low at bottom
    // left, vote share labelled in a left-aligned column beside the grid's middle
    // (arrow, then "Vote", then "share"), the census variable below it, and one line of text.
    const C = 20, X0 = 44, Y0 = 2, G = 3 * C, midY = Y0 + G / 2
    const cells = [0, 1, 2].flatMap((j) => [0, 1, 2].map((i) =>
      s('rect', { x: X0 + i * C, y: Y0 + G - (j + 1) * C, width: C, height: C, fill: BIVARIATE[i + 3 * j], class: 'bi-cell' })))
    const censusYear = v.fixed_in_time ? '' : ` (${state.cyear})`
    bi.map.getCanvas().setAttribute('aria-label',
      `Map combining ${v.label}${v.fixed_in_time ? '' : ` (${state.cyear} census)`} and ${cand.label}'s ${state.eyear} vote share by census tract, each split into thirds`)
    $('legend-bi').replaceChildren(
      s('svg', {
        width: X0 + G + 4, height: Y0 + G + 22, class: 'bi-key', role: 'img',
        'aria-label': `Colour key: ${v.label} in thirds from low to high, left to right, and ${cand.label}'s vote share in thirds from low to high, bottom to top`,
      },
        ...cells,
        s('text', { x: 2, y: midY - 11, class: 'bi-lab' }, '↑'),
        s('text', { x: 2, y: midY + 3, class: 'bi-lab' }, 'Vote'),
        s('text', { x: 2, y: midY + 16, class: 'bi-lab' }, 'share'),
        s('text', { x: X0, y: Y0 + G + 15, class: 'bi-lab bi-x' }, `${v.label} →`)),
      h('p', { class: 'bi-text' },
        'Tracts split into thirds by ', h('strong', {}, `${v.label}${censusYear}`),
        ' and by ', h('strong', {}, `${cand.label}'s ${state.eyear} vote share`),
        '. Each dot in the scatter plot is a tract, on the same colours as the map.'),
    )
    const key = $('legend-bi').querySelector('svg')
    key.setAttribute('width', Math.ceil(Math.max(X0 + G + 4, X0 + key.querySelector('.bi-x').getComputedTextLength() + 4)))
  }

  function updateCorrelations() {
    const v = varById.get(state.cvar)
    const cand = electionByYear.get(state.eyear).candidates.find((c) => c.id === state.ecand)
    updateBivariate()   // first: the scatter's background uses its tertile breaks
    updateScatter()

    updateCorrTable(cand)
    updateCandTable(cand)
  }

  // Every census variable's correlation with the selected vote share, grouped by
  // theme and coloured like the which-candidates-are-most-alike page (red-blue,
  // blue positive); hatched where p >= 0.05 (variables not in that census are left out).
  // Clicking a variable maps it.
  // 'group': by theme, as in the data; 'r': one list from the highest r to the lowest
  let tableSort = 'group'
  // 'year': by election, newest first; 'r': one list from the highest r to the lowest
  let candSort = 'year'

  // A coloured r (red-blue, as on the which-candidates-are-most-alike page), hatched
  // where p >= 0.05, in a row that runs `onPick` when clicked. The text is white
  // beyond ±0.6, black otherwise (white is a little under 4.5:1 contrast between
  // ±0.6 and ±0.7, a choice for looks). Non-significant cells are half way to white,
  // with dark grey text and diagonal hatching (.ns in the page's styles); they're all
  // near r = 0, so a fade alone barely shows. Strong correlations (|r| >= 0.5) are bold.
  const rCell = (st) => {
    const sig = st.p < 0.05
    const [r, g, b] = interpolateRdBu((st.r + 1) / 2).match(/\d+/g).map(Number)
    const bg = sig ? [r, g, b] : [r, g, b].map((c) => (c + 255) / 2)
    // compared as shown, to two decimals, so every cell reading ±0.60 matches
    const color = !sig ? '#595959' : Math.abs(st.r).toFixed(2) > 0.6 ? 'white' : 'black'
    return h('span', {
      class: `ct-r${sig ? '' : ' ns'}${Math.abs(st.r) >= 0.5 ? ' strong' : ''}`,
      // the colour only, so the hatching's background-image isn't overridden
      style: { backgroundColor: `rgb(${bg.map(Math.round).join(', ')})`, color },
      title: `r = ${fmtR(st.r)}, ${fmtP(st.p)}, ${st.n} tracts`,
    }, fmtR(st.r), sig ? null : h('span', { class: 'sr-only' }, ', not significant'))
  }
  const tableRow = (label, st, selected, onPick) => {
    const row = h('div', { class: `ct-row${selected ? ' sel' : ''}`, role: 'button', tabindex: '0' }, label, rCell(st))
    row.addEventListener('click', onPick)
    row.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onPick() } })
    return row
  }

  function updateCorrTable(cand) {
    const censusYear = varById.get(state.cvar).fixed_in_time ? '' : `, ${state.cyear} census`
    $('corr-rank-title').textContent =
      `How every neighbourhood characteristic relates to voting for ${cand.label} in ${state.eyear}${censusYear}`
    const pick = (id) => {
      state.cvar = id
      selVar.value = id
      fillCensusYears()
      updateCensus()
      refreshHover()
    }
    const rows = meta.variables.map((x) => ({ x, st: x.years.includes(state.cyear) ? pearson(pairsFor(x.id)) : null }))

    // one row: the variable (with its theme underneath when sorted by r) and its coloured r
    const rowFor = ({ x, st }, showGroup) => tableRow(
      showGroup && x.group
        ? h('span', { class: 'ct-label' }, listLabel(x), h('span', { class: 'ct-cat' }, x.group))
        : h('span', { class: 'ct-label' }, listLabel(x)),
      st, x.id === state.cvar, () => pick(x.id))

    // Variables without data for this census year (religion is only asked every ten
    // years, for example) are left out, and so is a category with none at all
    const present = rows.filter((d) => d.st)
    if (tableSort === 'r') {
      $('corr-table').replaceChildren(...[...present].sort((a, b) => b.st.r - a.st.r).map((d) => rowFor(d, true)))
      return
    }
    const groups = new Map()
    for (const d of present) {
      if (!groups.has(d.x.group)) groups.set(d.x.group, [])
      groups.get(d.x.group).push(d)
    }
    $('corr-table').replaceChildren(...[...groups].map(([group, ds]) =>
      h('div', { class: 'ct-group' },
        group ? h('div', { class: 'ct-group-name' }, group) : null,
        ...ds.map((d) => rowFor(d, false)))))
  }

  // Every other candidate's map against the selected one: r between their vote
  // shares across tracts, for the candidates the "which candidates" toggle lists.
  // Clicking a candidate selects them.
  function updateCandTable(cand) {
    $('corr-cand-title').textContent =
      `How similar every other candidate's electoral map is to ${cand.label}'s in ${state.eyear}`
    const mine = elections.get(`${state.eyear}|${state.ecand}`) ?? new Map()
    const rows = []
    for (const e of [...meta.elections].sort((a, b) => b.year - a.year)) {
      for (const c of candidatesFor(e.year)) {
        if (e.year === state.eyear && c.id === state.ecand) continue
        const theirs = elections.get(`${e.year}|${c.id}`) ?? new Map()
        const pairs = []
        for (const ct of tractIds) {
          const x = theirs.get(ct)?.share, y = mine.get(ct)?.share
          if (x != null && y != null) pairs.push([x, y])
        }
        const st = pearson(pairs)
        if (st) rows.push({ year: e.year, c, st })
      }
    }
    const pick = (d) => () => {
      state.eyear = d.year
      state.ecand = d.c.id
      fillElectionControls()
      updateElection()
      syncCensusYear()
      refreshHover()
    }
    if (candSort === 'r') {
      $('cand-table').replaceChildren(...[...rows].sort((a, b) => b.st.r - a.st.r).map((d) =>
        tableRow(h('span', { class: 'ct-label' }, `${d.c.label} (${d.year})`), d.st, false, pick(d))))
      return
    }
    const years = new Map()
    for (const d of rows) {
      if (!years.has(d.year)) years.set(d.year, [])
      years.get(d.year).push(d)
    }
    $('cand-table').replaceChildren(...[...years].map(([year, ds]) =>
      h('div', { class: 'ct-group' },
        h('div', { class: 'ct-group-name' }, `${year} election`),
        ...ds.map((d) => tableRow(h('span', { class: 'ct-label' }, d.c.label), d.st, false, pick(d))))))
  }

  // Redraw the charts at their new size when the layout changes
  let lastWidths = ''
  const redrawIfResized = () => {
    const now = widthOf('scatter-big') + 'x' + $('scatter-big').clientHeight
    if (now === lastWidths) return
    lastWidths = now
    updateCorrelations()
  }
  const resizeObserver = new ResizeObserver(redrawIfResized)
  resizeObserver.observe($('corr'))
  resizeObserver.observe(scatterEl)
  cleanup.push(() => resizeObserver.disconnect())

  // ---- Wire controls ----
  const on = (el, type, fn) => { el.addEventListener(type, fn); cleanup.push(() => el.removeEventListener(type, fn)) }

  on(scatterEl, 'mousemove', (ev) => {
    const ct = nearestDot(ev)
    scatterEl.style.cursor = ct ? 'crosshair' : ''
    setHover(ct)
  })
  on(scatterEl, 'mouseleave', () => setHover(null))

  for (const btn of root.querySelectorAll('#cand-sort button')) {
    on(btn, 'click', () => {
      candSort = btn.dataset.sort
      root.querySelectorAll('#cand-sort button').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)))
      updateCandTable(electionByYear.get(state.eyear).candidates.find((c) => c.id === state.ecand))
    })
  }
  for (const btn of root.querySelectorAll('#corr-sort button')) {
    on(btn, 'click', () => {
      tableSort = btn.dataset.sort
      root.querySelectorAll('#corr-sort button').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)))
      updateCorrTable(electionByYear.get(state.eyear).candidates.find((c) => c.id === state.ecand))
    })
  }

  for (const [src, copy] of mirrors) {
    on(copy, 'change', () => {
      src.value = copy.value
      src.dispatchEvent(new Event('change'))
    })
  }

  on(selVar, 'change', () => { state.cvar = selVar.value; fillCensusYears(); updateCensus(); refreshHover() })
  on(selCYear, 'change', () => { state.cyear = +selCYear.value; updateCensus(); refreshHover() })

  // Move the census map to the year with data closest to the election
  // (ties go to the earlier census).
  function syncCensusYear() {
    if (varById.get(state.cvar).fixed_in_time) return
    const years = varById.get(state.cvar).years
    const nearest = years.reduce((best, y) =>
      Math.abs(y - state.eyear) < Math.abs(best - state.eyear) ? y : best)
    if (nearest === state.cyear) return
    state.cyear = nearest
    selCYear.value = nearest
    updateCensus()
  }

  const onElectionChange = () => {
    fillElectionControls()
    updateElection()
    syncCensusYear()
    refreshHover()
  }
  on(selCand, 'change', () => {
    const [year, id] = selCand.value.split('|')
    state.eyear = +year
    state.ecand = id
    onElectionChange()
  })
  on(selEYear, 'change', () => {
    // keep the same candidate, in the year just picked
    const person = currentPerson()
    state.eyear = +selEYear.value
    state.ecand = people.get(person).find((r) => r.year === state.eyear).id
    onElectionChange()
  })
  for (const r of root.querySelectorAll('.cand-scope input')) {
    on(r, 'change', () => { state.eall = r.value === '1'; onElectionChange() })
  }

  updateCensus()
  updateElection()

  return () => cleanup.forEach((fn) => fn())
}
