// Concept index -> `src/generated/concept.json` and one `src/features/<featureset>/<feature>.stories.ts`
// per feature spec.
//
// Reads the roster `_concept/05_features/featuresets.md`, every feature spec
// `05_features/<featureset>/<feature>.md`, the screen specs `07_screens/*.md`, the dossiers'
// `08_dossiers/<feature>/index.md` and `04_journeys/stories.yaml`, joins them on the spec path in
// both directions, and writes what the `Features/*` pages and the screens' Docs pages show, as
// `tree/09_mockup/storybook/README.md § Feature pages` says. Nothing in the output is authored
// here: change the specs. A missing file counts as empty and an unreadable one is skipped with a
// warning, so no run fails on the concept. `.storybook/main.ts` calls `writeConcept()` on every
// start, `vite.config.ts` again on a change; `npm run concept` is the manual form.
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, rmdirSync, statSync, writeFileSync } from 'node:fs'
import { basename, dirname, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse } from 'yaml'
import type { Concept, ConceptCriterion, ConceptFeature, ConceptLink, ConceptScreen, StoryRef } from '../src/components/concept-types.ts'

const packageDir = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const conceptDir = resolve(packageDir, '../..')
const featuresDir = resolve(conceptDir, '05_features')
const screensDir = resolve(conceptDir, '07_screens')
const dossiersDir = resolve(conceptDir, '08_dossiers')
const storiesFile = resolve(conceptDir, '04_journeys/stories.yaml')
const outFile = resolve(packageDir, 'src/generated/concept.json')
const featurePagesDir = resolve(packageDir, 'src/features')

/** The concept files and directories `writeConcept` reads; the dev server watches them. */
export const conceptSources: string[] = [featuresDir, screensDir, dossiersDir, storiesFile]

type Json = Record<string, unknown>

const isObject = (value: unknown): value is Json =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

const warn = (file: string, error: unknown): void => {
  console.warn(`gen-concept: skipped ${relative(conceptDir, file)}: ${error instanceof Error ? error.message : String(error)}`)
}

const readText = (file: string): string | undefined => {
  try {
    return existsSync(file) && statSync(file).isFile() ? readFileSync(file, 'utf8') : undefined
  } catch (error) {
    warn(file, error)
    return undefined
  }
}

const list = (dir: string): string[] => {
  try {
    return existsSync(dir) && statSync(dir).isDirectory() ? readdirSync(dir).sort() : []
  } catch {
    return []
  }
}

const isDir = (path: string): boolean => existsSync(path) && statSync(path).isDirectory()

const str = (value: unknown): string | undefined =>
  typeof value === 'string' ? value : typeof value === 'number' ? String(value) : undefined

const strings = (value: unknown): string[] =>
  Array.isArray(value) ? value.map(str).filter((s): s is string => s !== undefined) : []

/** `05_features/x.md` from a string or `{ path }` entry; a leading `_concept/` or `./` is dropped. */
const pathOf = (entry: unknown): string | undefined => {
  const path = str(entry) ?? (isObject(entry) ? str(entry.path) : undefined)
  return path?.trim().replace(/^\.\//, '').replace(/^_concept\//, '')
}

const pathsOf = (value: unknown): string[] =>
  (Array.isArray(value) ? value : value === undefined ? [] : [value]).map(pathOf).filter((p): p is string => !!p)

interface Doc { frontmatter: Json; body: string }

/** Frontmatter between a leading `---` line and the next `---` line, parsed as YAML; the rest is the body. */
function readDoc(file: string): Doc | undefined {
  const text = readText(file)
  if (text === undefined) return undefined
  const lines = text.split(/\r?\n/)
  if (lines[0]?.trim() !== '---') return { frontmatter: {}, body: text }
  const end = lines.findIndex((line, i) => i > 0 && line === '---')
  if (end < 0) return { frontmatter: {}, body: text }
  try {
    const data: unknown = parse(lines.slice(1, end).join('\n'))
    if (data !== null && data !== undefined && !isObject(data)) throw new Error('frontmatter is not a mapping')
    return { frontmatter: (data ?? {}) as Json, body: lines.slice(end + 1).join('\n') }
  } catch (error) {
    warn(file, error)
    return undefined
  }
}

/** The lines under the first heading matching `heading` (case-insensitive), up to a line matching `stop`. */
function section(body: string, heading: RegExp, stop: RegExp): string[] | undefined {
  const lines = body.split(/\r?\n/)
  const start = lines.findIndex((line) => heading.test(line))
  if (start < 0) return undefined
  const rest = lines.slice(start + 1)
  const end = rest.findIndex((line) => stop.test(line))
  return end < 0 ? rest : rest.slice(0, end)
}

const sectionText = (body: string, heading: RegExp, stop: RegExp): string | undefined =>
  section(body, heading, stop)?.join('\n').trim() || undefined

interface Featureset { purpose?: string; outcomes: Map<string, string> }

/** `05_features/featuresets.md`: featureset -> its purpose line and the `feature` -> `outcome` table. */
function readRoster(): Map<string, Featureset> {
  const sets = new Map<string, Featureset>()
  const text = readText(resolve(featuresDir, 'featuresets.md'))
  if (text === undefined) return sets
  let current: Featureset | undefined
  let columns: { feature: number; outcome: number } | undefined
  for (const line of text.split(/\r?\n/)) {
    const heading = /^##\s+(.+?)\s*$/.exec(line)
    if (heading) {
      const name = heading[1]!
      current = /^(roles|ideas|cut)$/i.test(name) ? undefined : { outcomes: new Map() }
      if (current) sets.set(name, current)
      columns = undefined
      continue
    }
    if (!current) continue
    const trimmed = line.trim()
    if (!trimmed.startsWith('|')) {
      if (trimmed && current.purpose === undefined) current.purpose = trimmed
      continue
    }
    if (/^\|\s*:?-/.test(trimmed)) continue
    const cells = trimmed.replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim())
    if (!columns) {
      const names = cells.map((c) => c.toLowerCase())
      columns = { feature: names.indexOf('feature'), outcome: names.indexOf('outcome') }
      continue
    }
    const feature = cells[columns.feature]
    const outcome = cells[columns.outcome]
    if (columns.feature >= 0 && columns.outcome >= 0 && feature && outcome) current.outcomes.set(feature, outcome)
  }
  return sets
}

interface Journey { title?: string; stage?: string }

/** `04_journeys/stories.yaml`: journey id -> title and stage, criterion id -> EARS text. */
function readJourneys(): { journeys: Map<string, Journey>; ears: Map<string, string> } {
  const journeys = new Map<string, Journey>()
  const ears = new Map<string, string>()
  const text = readText(storiesFile)
  if (text === undefined) return { journeys, ears }
  let data: unknown
  try {
    data = parse(text)
  } catch (error) {
    warn(storiesFile, error)
    return { journeys, ears }
  }
  const entries = isObject(data) && Array.isArray(data.journeys) ? data.journeys : []
  for (const journey of entries) {
    if (!isObject(journey)) continue
    const id = str(journey.id)
    if (id) journeys.set(id, { title: str(journey.title), stage: str(journey.stage) })
    for (const step of Array.isArray(journey.steps) ? journey.steps : []) {
      if (!isObject(step)) continue
      for (const criterion of Array.isArray(step.acceptance) ? step.acceptance : []) {
        if (!isObject(criterion)) continue
        const cid = str(criterion.id)
        const text = str(criterion.ears)
        if (cid && text) ears.set(cid, text)
      }
    }
  }
  return { journeys, ears }
}

interface ScreenSpec { id: string; title?: string; purpose?: string; implements: string[] }

/** `07_screens/*.md` except `shell.md`. */
function readScreens(): ScreenSpec[] {
  const screens: ScreenSpec[] = []
  for (const name of list(screensDir)) {
    if (!name.endsWith('.md') || name === 'shell.md') continue
    const file = resolve(screensDir, name)
    if (isDir(file)) continue
    const doc = readDoc(file)
    if (!doc) continue
    screens.push({
      id: str(doc.frontmatter.screen_id) ?? basename(name, '.md'),
      title: str(doc.frontmatter.title),
      purpose: sectionText(doc.body, /^###\s+purpose\s*$/i, /^#{1,3}\s/),
      implements: pathsOf(doc.frontmatter.implements),
    })
  }
  return screens
}

interface FeatureSpec {
  spec: string; featureset: string; slug: string
  priority?: string; permissions: Record<string, string[]>; storyRefs: string[]; screens: string[]
  scope: string[]; criteria: { id: string; label: string }[]
}

const CRITERION = /^\s*-\s+(AC-[a-z0-9_-]+-\d{2})\b\s*(?:[-–—:]\s*)?(.*)$/

/** Every `05_features/<featureset>/<feature>.md`, exactly two levels deep. */
function readFeatures(): FeatureSpec[] {
  const features: FeatureSpec[] = []
  for (const featureset of list(featuresDir)) {
    const setDir = resolve(featuresDir, featureset)
    if (!isDir(setDir)) continue
    for (const name of list(setDir)) {
      if (!name.endsWith('.md')) continue
      const file = resolve(setDir, name)
      if (isDir(file)) continue
      const doc = readDoc(file)
      if (!doc) continue
      const fm = doc.frontmatter
      const permissions: Record<string, string[]> = {}
      if (isObject(fm.permissions)) for (const [role, actions] of Object.entries(fm.permissions)) permissions[role] = strings(actions)
      const scope = (section(doc.body, /^##\s+scope\s*$/i, /^##\s/) ?? [])
        .filter((line) => /^\s*-\s/.test(line))
        .map((line) => line.replace(/^\s*-\s+/, '').trim())
      const criteria: { id: string; label: string }[] = []
      for (const line of doc.body.split(/\r?\n/)) {
        const match = CRITERION.exec(line)
        if (match && !criteria.some((c) => c.id === match[1])) criteria.push({ id: match[1]!, label: match[2]!.trim() })
      }
      features.push({
        spec: `05_features/${featureset}/${name}`,
        featureset,
        slug: basename(name, '.md'),
        priority: str(fm.priority),
        permissions,
        storyRefs: strings(fm.story_refs),
        screens: pathsOf(fm.screens).map((path) => basename(path, '.md')),
        scope,
        criteria,
      })
    }
  }
  return features.sort((a, b) => a.featureset.localeCompare(b.featureset) || a.slug.localeCompare(b.slug))
}

const storyIf = (layer: 'Screens' | 'Journeys', id: string): StoryRef | undefined =>
  existsSync(resolve(packageDir, `src/${layer.toLowerCase()}/${id}.stories.ts`)) ? { title: `${layer}/${id}`, name: 'Default' } : undefined

const sorted = (values: Iterable<string>): string[] => [...new Set(values)].sort()

/** Build the concept index from `_concept/`. */
function buildConcept(): Concept {
  const roster = readRoster()
  const { journeys, ears } = readJourneys()
  const screenSpecs = readScreens()
  const featureSpecs = readFeatures()
  const screenById = new Map(screenSpecs.map((screen) => [screen.id, screen]))

  const screens: Record<string, ConceptScreen> = {}
  for (const screen of screenSpecs) {
    const features = sorted([
      ...screen.implements,
      ...featureSpecs.filter((f) => f.screens.includes(screen.id)).map((f) => f.spec),
    ])
    screens[screen.id] = { id: screen.id, title: screen.title, purpose: screen.purpose, features }
  }

  const features: ConceptFeature[] = featureSpecs.map((f) => {
    const screenIds = sorted([...f.screens, ...screenSpecs.filter((s) => s.implements.includes(f.spec)).map((s) => s.id)])
    const screenLinks: ConceptLink[] = screenIds.map((id) => ({ id, title: screenById.get(id)?.title, story: storyIf('Screens', id) }))
    const journeyLinks: ConceptLink[] = sorted(f.storyRefs).map((id) => {
      const journey = journeys.get(id)
      return {
        id,
        title: journey?.title,
        stage: journey?.stage,
        story: journey?.stage === 'backlog' ? undefined : storyIf('Journeys', id),
      }
    })
    const criteria: ConceptCriterion[] = f.criteria.map((c) => ({ ...c, ears: ears.get(c.id) }))
    const featureset = roster.get(f.featureset)
    const dossier = readDoc(resolve(dossiersDir, f.slug, 'index.md'))
    return {
      spec: f.spec,
      slug: f.slug,
      featureset: f.featureset,
      featuresetPurpose: featureset?.purpose,
      outcome: featureset?.outcomes.get(f.slug),
      priority: f.priority,
      framing: dossier ? sectionText(dossier.body, /^##\s+framing\s*$/i, /^##\s/) : undefined,
      permissions: f.permissions,
      scope: f.scope,
      criteria,
      screens: screenLinks,
      journeys: journeyLinks,
    }
  })

  return { features, screens }
}

/** The generated `Features/<featureset>/<feature>` story for one spec. */
function featureStory(feature: ConceptFeature): string {
  return `// Generated by scripts/gen-concept.ts from _concept/${feature.spec}; edit the spec, never this file.
import type { Meta, StoryObj } from '@storybook/vue3-vite'
import FeatureDoc from '../../components/FeatureDoc.vue'

const meta = {
  title: ${JSON.stringify(`Features/${feature.featureset}/${feature.slug}`)},
  component: FeatureDoc,
  args: { spec: ${JSON.stringify(feature.spec)} },
} satisfies Meta<typeof FeatureDoc>

export default meta

export const Overview: StoryObj<typeof meta> = {}
`
}

// Skip identical writes: a rewrite would make Storybook re-index or Vite reload for nothing.
function writeIfChanged(file: string, content: string): void {
  if (existsSync(file) && readFileSync(file, 'utf8') === content) return
  mkdirSync(dirname(file), { recursive: true })
  writeFileSync(file, content)
}

/** Every file below `dir`, depth first. */
function walk(dir: string): string[] {
  return list(dir).flatMap((name) => {
    const path = join(dir, name)
    return isDir(path) ? walk(path) : [path]
  })
}

/** Remove the directories below `dir` that are left empty. */
function pruneEmpty(dir: string): void {
  for (const name of list(dir)) {
    const path = join(dir, name)
    if (!isDir(path)) continue
    pruneEmpty(path)
    if (list(path).length === 0) rmdirSync(path)
  }
}

/** Generate `src/generated/concept.json` and the feature pages; returns what was indexed. */
export function writeConcept(): { features: number; screens: number } {
  const concept = buildConcept()
  writeIfChanged(outFile, `${JSON.stringify(concept, null, 2)}\n`)
  const wanted = new Map(concept.features.map((f) => [resolve(featurePagesDir, f.featureset, `${f.slug}.stories.ts`), featureStory(f)]))
  for (const file of walk(featurePagesDir)) if (!wanted.has(file)) rmSync(file)
  for (const [file, content] of wanted) writeIfChanged(file, content)
  pruneEmpty(featurePagesDir)
  return { features: concept.features.length, screens: Object.keys(concept.screens).length }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  console.log(`wrote ${writeConcept().features} feature pages`)
}
