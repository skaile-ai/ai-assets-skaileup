import type { Meta, StoryObj } from '@storybook/vue3-vite'
import ObjectPage from './object-page.vue'

const meta = {
  title: 'Floorplans/object-page',
  component: ObjectPage,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof ObjectPage>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** History disclosure expanded. */
export const HistoryOpen: Story = { args: { historyOpen: true }, globals: { viewport: { value: 'wide', isRotated: false } } }
