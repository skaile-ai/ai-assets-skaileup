import type { Meta, StoryObj } from '@storybook/vue3-vite'
import type { NavEntry } from '../components/nav-types'
import ShellMobileTabs from './shell-mobile-tabs.vue'

const nav: NavEntry[] = [
  { label: 'Inbox', to: '/inbox', group: 'Work', pinned: true },
  { label: 'Projects', to: '/projects', group: 'Work', pinned: true },
  { label: 'Tasks', to: '/tasks', group: 'Work' },
  { label: 'Invoices', to: '/invoices', group: 'Money', pinned: true },
  { label: 'Reports', to: '/reports', group: 'Money' },
  { label: 'Settings', to: '/settings', group: 'Admin' },
]

const meta = {
  title: 'Floorplans/shell-mobile-tabs',
  component: ShellMobileTabs,
  parameters: { layout: 'fullscreen' },
  args: { nav, title: 'Projects' },
} satisfies Meta<typeof ShellMobileTabs>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** More sheet with the remaining destinations. */
export const MoreOpen: Story = { args: { more: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Detail sheet. */
export const DetailOpen: Story = { args: { detail: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** More sheet, narrow. */
export const NarrowMore: Story = { args: { more: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Full-screen search. */
export const NarrowPalette: Story = { args: { palette: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }
