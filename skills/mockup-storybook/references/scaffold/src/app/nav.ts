// The shell of the app: which shell floorplan frames it and which destinations it lists.
// Written from `_concept/07_screens/shell.md`. With no entries the shell lists every screen.
import type { NavEntry } from '../components/nav-types'
import type { shells } from '../floorplans'

export const shell: keyof typeof shells = 'shell-sidebar'

export const nav: NavEntry[] = []
