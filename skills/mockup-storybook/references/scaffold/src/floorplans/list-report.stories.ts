import type { Meta, StoryObj } from '@storybook/vue3-vite'
import ListReport from './list-report.vue'

const meta = {
  title: 'Floorplans/list-report',
  component: ListReport,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof ListReport>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Peek opened from a row. */
export const WithPeek: Story = { args: { peek: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Peek as a bottom sheet. */
export const NarrowPeek: Story = { args: { peek: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }
