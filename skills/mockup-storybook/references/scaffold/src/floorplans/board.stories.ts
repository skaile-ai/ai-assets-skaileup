import type { Meta, StoryObj } from '@storybook/vue3-vite'
import Board from './board.vue'

const meta = {
  title: 'Floorplans/board',
  component: Board,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof Board>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Card drawer closed. */
export const DrawerClosed: Story = { args: { drawer: false }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Bottom sheet closed. */
export const NarrowDrawerClosed: Story = { args: { drawer: false }, globals: { viewport: { value: 'narrow', isRotated: false } } }
