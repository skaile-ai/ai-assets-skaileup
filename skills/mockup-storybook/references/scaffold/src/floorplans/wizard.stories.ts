import type { Meta, StoryObj } from '@storybook/vue3-vite'
import Wizard from './wizard.vue'

const meta = {
  title: 'Floorplans/wizard',
  component: Wizard,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof Wizard>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Third of three steps. */
export const LastStep: Story = { args: { current: 2 }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Folded step line on the last step. */
export const NarrowLastStep: Story = { args: { current: 2 }, globals: { viewport: { value: 'narrow', isRotated: false } } }
