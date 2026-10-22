// The fake data layer of the mockup: seed rows in memory, writes that take a moment and can
// be made to fail. No network, no persistence. Provided once per story by the preview decorator.
import { inject, provide, reactive, ref, watch } from 'vue'
import type { InjectionKey, Ref } from 'vue'
import { controls, entityKeys, scenarioData } from './scenario'
import type { Row } from './scenario'

/** A row to save: new rows have no `id` yet. */
export type Draft<R extends { id: string }> = Omit<R, 'id'> & { id?: string }

export interface Store {
  /** The active scenario's rows of one entity (`task` for `Task`). */
  rows<R extends { id: string } = Row>(entity: string): R[]
  /** Insert or replace by `id`; resolves with the stored row, rejects while `fail` is on. */
  save<R extends { id: string }>(entity: string, row: Draft<R>): Promise<R>
  remove(entity: string, id: string): Promise<void>
  /** True while a write is in flight. */
  saving: Readonly<Ref<boolean>>
  /** The last write's failure, cleared by the next write. */
  error: Readonly<Ref<string | null>>
}

const NO_ROWS: Row[] = []
const LATENCY_MS = 600
const key: InjectionKey<Store> = Symbol('mockup-store')

export function createStore(source: { scenario: string; fail: boolean } = controls): Store {
  const data = reactive<Record<string, Row[]>>({})
  const saving = ref(false)
  const error = ref<string | null>(null)

  watch(
    () => source.scenario,
    (name) => {
      // One array per entity for the store's lifetime, replaced in place: a screen that holds
      // `rows('task')` keeps seeing the active scenario after the toolbar switches it.
      const next = scenarioData(name)
      for (const entity of new Set([...entityKeys, ...Object.keys(data)])) {
        data[entity] ??= []
        data[entity].splice(0, data[entity].length, ...(next[entity] ?? []))
      }
    },
    { immediate: true },
  )

  const write = async <T>(apply: () => T): Promise<T> => {
    saving.value = true
    error.value = null
    await new Promise((done) => setTimeout(done, LATENCY_MS))
    saving.value = false
    if (source.fail) {
      error.value = 'The server did not answer. Nothing was saved.'
      throw new Error(error.value)
    }
    return apply()
  }

  return {
    rows: <R extends { id: string } = Row>(entity: string) => (data[entity] ?? NO_ROWS) as unknown as R[],
    save: <R extends { id: string }>(entity: string, row: Draft<R>) =>
      write(() => {
        const list = (data[entity] ??= [])
        const stored = { ...row, id: row.id ?? crypto.randomUUID() } as unknown as R
        const at = list.findIndex((existing) => existing.id === stored.id)
        if (at >= 0) list[at] = stored as unknown as Row
        else list.push(stored as unknown as Row)
        return stored
      }),
    remove: (entity, id) =>
      write(() => {
        const list = (data[entity] ??= [])
        const at = list.findIndex((row) => row.id === id)
        if (at >= 0) list.splice(at, 1)
      }),
    saving,
    error,
  }
}

export const provideStore = (store: Store): void => provide(key, store)

export function useStore(): Store {
  const store = inject(key)
  if (!store) throw new Error('useStore() needs the store the preview decorator provides; render the component in a story')
  return store
}
