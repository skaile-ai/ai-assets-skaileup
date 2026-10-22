import type { Meta, StoryObj } from '@storybook/vue3-vite'
import Settings from './settings.vue'

const meta = {
  title: 'Floorplans/settings',
  component: Settings,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof Settings>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }
