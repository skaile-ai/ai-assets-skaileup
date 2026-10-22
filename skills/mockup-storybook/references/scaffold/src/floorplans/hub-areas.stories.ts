import type { Meta, StoryObj } from '@storybook/vue3-vite'
import HubAreas from './hub-areas.vue'

const meta = {
  title: 'Floorplans/hub-areas',
  component: HubAreas,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof HubAreas>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Peek opened from a row of the area. */
export const WidePeek: Story = { args: { peek: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** One frame at a time: the area. */
export const NarrowArea: Story = { args: { frame: 'area' }, globals: { viewport: { value: 'narrow', isRotated: false } } }

/** One frame at a time: the walk. */
export const NarrowWalk: Story = { args: { frame: 'walk' }, globals: { viewport: { value: 'narrow', isRotated: false } } }
