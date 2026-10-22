import type { Meta, StoryObj } from '@storybook/vue3-vite'
import Overview from './overview.vue'

const meta = {
  title: 'Floorplans/overview',
  component: Overview,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof Overview>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Row peek opened. */
export const WithPeek: Story = { args: { peek: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Row peek as an inline expansion. */
export const NarrowPeek: Story = { args: { peek: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }
