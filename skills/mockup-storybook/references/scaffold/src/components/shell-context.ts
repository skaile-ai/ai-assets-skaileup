import { inject, provide } from 'vue'
import type { InjectionKey } from 'vue'

const key: InjectionKey<boolean> = Symbol('in-shell')

/** Called by the app's shell: everything below it sits inside the real shell. */
export const provideInShell = (): void => provide(key, true)

/**
 * True when the screen renders inside the app's shell (the `App` and `Journeys/*` stories), false
 * when it renders alone (`Screens/*`). A screen passes `:chrome="!useInShell()"` to its floorplan,
 * so the standalone story still shows the floorplan's `shell` region and the app does not
 * draw it twice.
 */
export const useInShell = (): boolean => inject(key, false)
