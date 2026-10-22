import type { Meta, StoryObj } from '@storybook/vue3-vite'
import MasterDetail from './master-detail.vue'

const meta = {
  title: 'Floorplans/master-detail',
  component: MasterDetail,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof MasterDetail>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Narrow: the detail as its own view. */
export const NarrowDetail: Story = { args: { detail: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }
