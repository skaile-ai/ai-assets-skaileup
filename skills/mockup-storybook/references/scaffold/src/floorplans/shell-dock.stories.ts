import type { Meta, StoryObj } from '@storybook/vue3-vite'
import type { NavEntry } from '../components/nav-types'
import ShellDock from './shell-dock.vue'

const nav: NavEntry[] = [
  { label: 'Inbox', to: '/inbox', group: 'Work', pinned: true },
  { label: 'Projects', to: '/projects', group: 'Work', pinned: true },
  { label: 'Tasks', to: '/tasks', group: 'Work' },
  { label: 'Invoices', to: '/invoices', group: 'Money', pinned: true },
  { label: 'Reports', to: '/reports', group: 'Money' },
  { label: 'Settings', to: '/settings', group: 'Admin' },
]

const meta = {
  title: 'Floorplans/shell-dock',
  component: ShellDock,
  parameters: { layout: 'fullscreen' },
  args: { nav, title: 'Projects' },
} satisfies Meta<typeof ShellDock>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Command palette. */
export const PaletteOpen: Story = { args: { palette: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow: the navigation pane. */
export const NarrowNavigate: Story = { args: { pane: 'nav' }, globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Narrow: the detail pane. */
export const NarrowDetail: Story = { args: { pane: 'detail' }, globals: { viewport: { value: 'narrow', isRotated: false } } }
