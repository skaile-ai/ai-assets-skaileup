// Seed scenarios of the data model. `_concept/10_blueprint/datamodel/seed.ts` is optional: an
// empty project has one empty scenario, so the package builds before the model exists.
import { reactive } from 'vue'

export type Row = { id: string } & Record<string, unknown>

export interface SeedLike {
  scenarios: Record<string, { description?: string; data: Record<string, Row[]> }>
}

const found = import.meta.glob<{ seed: SeedLike }>('@model/seed.ts', { eager: true })
const seed: SeedLike = Object.values(found)[0]?.seed ?? { scenarios: { empty: { description: 'No data model yet', data: {} } } }

/** Toolbar items of the `scenario` global: the keys of `seed.scenarios`. */
export const scenarioNames = Object.keys(seed.scenarios)
/** Every entity key any scenario has rows for: the store keeps one stable array per key. */
export const entityKeys = [...new Set(Object.values(seed.scenarios).flatMap((scenario) => Object.keys(scenario.data)))]
export const defaultScenario = scenarioNames.includes('populated') ? 'populated' : (scenarioNames[0] ?? 'empty')

/** A private copy of one scenario's rows per entity key, so a story's edits never reach the seed. */
export function scenarioData(name: string): Record<string, Row[]> {
  return structuredClone(seed.scenarios[name]?.data ?? {})
}

/** The two story globals the store follows. Updated by the preview decorator. */
export const controls = reactive({ scenario: defaultScenario, fail: false })

export function applyGlobals(globals: Record<string, unknown>): void {
  if (typeof globals.scenario === 'string') controls.scenario = globals.scenario
  controls.fail = globals.fail === 'on'
}
