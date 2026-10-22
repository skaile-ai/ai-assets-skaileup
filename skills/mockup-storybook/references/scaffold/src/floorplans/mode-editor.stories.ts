import type { Meta, StoryObj } from '@storybook/vue3-vite'
import ModeEditor from './mode-editor.vue'

const meta = {
  title: 'Floorplans/mode-editor',
  component: ModeEditor,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof ModeEditor>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Studio drawer from the right. */
export const StudioOpen: Story = { args: { studioOpen: true }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Outline overlay from the left. */
export const NarrowTreeOpen: Story = { args: { treeOpen: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Studio drawer as a bottom sheet. */
export const NarrowStudioOpen: Story = { args: { studioOpen: true }, globals: { viewport: { value: 'narrow', isRotated: false } } }
