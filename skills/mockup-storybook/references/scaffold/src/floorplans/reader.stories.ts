import type { Meta, StoryObj } from '@storybook/vue3-vite'
import Reader from './reader.vue'

const meta = {
  title: 'Floorplans/reader',
  component: Reader,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof Reader>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Reader as a full-width overlay. */
export const NarrowReader: Story = { args: { readerOpen: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }
