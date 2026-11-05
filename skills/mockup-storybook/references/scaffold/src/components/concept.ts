// Reads the generated concept index; see scripts/gen-concept.ts.
import data from '../generated/concept.json'
import type { Concept, ConceptFeature } from './concept-types'

export const concept = data as Concept

const slug = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')

/** Storybook's story id: the same rule as `slug()` in triage.py. */
export function storyId(title: string, name: string): string {
  return `${slug(title)}--${slug(name)}`
}

export function featureBySpec(spec: string): ConceptFeature | undefined {
  return concept.features.find((f) => f.spec === spec)
}

/** Docs parameters for a screen story: its purpose and the features it implements. */
export function screenDocs(id: string): { description: { component: string } } {
  const screen = concept.screens[id]
  if (!screen) return { description: { component: '' } }
  const parts: string[] = [screen.purpose ?? '']
  const features = screen.features
    .map((spec) => featureBySpec(spec))
    .filter((f): f is ConceptFeature => !!f)
  if (features.length) {
    parts.push('', '**Implements**', '')
    for (const f of features) {
      const name = `${f.featureset}/${f.slug}`
      const outcome = f.outcome ? ` — ${f.outcome}` : ''
      parts.push(`- [${name}](?path=/story/${storyId(`Features/${name}`, 'Overview')})${outcome}`)
    }
  }
  return { description: { component: parts.join('\n') } }
}
