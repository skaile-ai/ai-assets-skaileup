// Seed scenarios of the data model, served from `_concept/10_blueprint/datamodel/seed.yaml` by the
// `skaileModel` vite plugin. Without a seed file the plugin serves one empty scenario, so the
// package builds before the model exists.
import { reactive } from 'vue'
import { seed } from '@model/seed'

export type Row = { id: string } & Record<string, unknown>

/** Toolbar items of the `scenario` global: the keys of `seed.scenarios`. */
export const scenarioNames = Object.keys(seed.scenarios)
/** Every entity key any scenario has rows for: the store keeps one stable array per key. */
export const entityKeys = [...new Set(Object.values(seed.scenarios).flatMap((scenario) => Object.keys(scenario.data)))]
export const defaultScenario = scenarioNames.includes('populated') ? 'populated' : (scenarioNames[0] ?? 'empty')

/** A private copy of one scenario's rows per entity key, so a story's edits never reach the seed. */
export function scenarioData(name: string): Record<string, Row[]> {
  return structuredClone((seed.scenarios[name]?.data ?? {}) as Record<string, Row[]>)
}

/** The two story globals the store follows. Updated by the preview decorator. */
export const controls = reactive({ scenario: defaultScenario, fail: false })

export function applyGlobals(globals: Record<string, unknown>): void {
  if (typeof globals.scenario === 'string') controls.scenario = globals.scenario
  controls.fail = globals.fail === 'on'
}
