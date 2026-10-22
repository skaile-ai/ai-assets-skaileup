import type { Meta, StoryObj } from '@storybook/vue3-vite'
import TabbedTool from './tabbed-tool.vue'

const meta = {
  title: 'Floorplans/tabbed-tool',
  component: TabbedTool,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof TabbedTool>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Detail panel over the dimmed list. */
export const DetailOpen: Story = { args: { detailOpen: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Filter drawer. */
export const FiltersOpen: Story = { args: { filtersOpen: true, filtersApplied: 2 }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Empty-state-first variant. */
export const EmptyFirst: Story = { args: { emptyFirst: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Detail full-screen. */
export const NarrowDetail: Story = { args: { detailOpen: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Filters as a bottom sheet. */
export const NarrowFilters: Story = { args: { filtersOpen: true, filtersApplied: 2 }, globals: { viewport: { value: 'narrow', isRotated: false } } }
