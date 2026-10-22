import type { Meta, StoryObj } from '@storybook/vue3-vite'
import type { NavEntry } from '../components/nav-types'
import ShellTopbar from './shell-topbar.vue'

const nav: NavEntry[] = [
  { label: 'Inbox', to: '/inbox', group: 'Work', pinned: true },
  { label: 'Projects', to: '/projects', group: 'Work', pinned: true },
  { label: 'Tasks', to: '/tasks', group: 'Work' },
  { label: 'Invoices', to: '/invoices', group: 'Money', pinned: true },
  { label: 'Reports', to: '/reports', group: 'Money' },
  { label: 'Settings', to: '/settings', group: 'Admin' },
]

const meta = {
  title: 'Floorplans/shell-topbar',
  component: ShellTopbar,
  parameters: { layout: 'fullscreen' },
  args: { nav, title: 'Projects' },
} satisfies Meta<typeof ShellTopbar>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Peek anchored to a row. */
export const PeekOpen: Story = { args: { peek: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Destination panel under the bar. */
export const NarrowMenu: Story = { args: { menu: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Peek as a bottom sheet. */
export const NarrowPeek: Story = { args: { peek: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }
