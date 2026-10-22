import type { Meta, StoryObj } from '@storybook/vue3-vite'
import type { NavEntry } from '../components/nav-types'
import ShellSidebar from './shell-sidebar.vue'
import MasterDetail from './master-detail.vue'

const nav: NavEntry[] = [
  { label: 'Inbox', to: '/inbox', group: 'Work', pinned: true },
  { label: 'Projects', to: '/projects', group: 'Work', pinned: true },
  { label: 'Tasks', to: '/tasks', group: 'Work' },
  { label: 'Invoices', to: '/invoices', group: 'Money', pinned: true },
  { label: 'Reports', to: '/reports', group: 'Money' },
  { label: 'Settings', to: '/settings', group: 'Admin' },
]

const meta = {
  title: 'Floorplans/shell-sidebar',
  component: ShellSidebar,
  parameters: { layout: 'fullscreen' },
  args: { nav, title: 'Projects' },
} satisfies Meta<typeof ShellSidebar>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Slideover docked at the right. */
export const SlideoverOpen: Story = { args: { slideover: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Sidebar as a drawer over a scrim. */
export const NarrowDrawer: Story = { args: { drawer: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Slideover as a bottom sheet. */
export const NarrowSlideover: Story = { args: { slideover: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Command palette. */
export const PaletteOpen: Story = { args: { palette: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** A screen floorplan inside the shell's work area. */
export const WithScreen: Story = {
  globals: { viewport: { value: 'wide', isRotated: false } },
  render: (args) => ({
    components: { ShellSidebar, MasterDetail },
    setup: () => ({ args }),
    template: '<ShellSidebar v-bind="args"><MasterDetail :chrome="false" /></ShellSidebar>',
  }),
}
