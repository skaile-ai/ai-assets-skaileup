import type { Meta, StoryObj } from '@storybook/vue3-vite'
import ThreePane from './three-pane.vue'

const meta = {
  title: 'Floorplans/three-pane',
  component: ThreePane,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof ThreePane>

export default meta
type Story = StoryObj<typeof meta>

/** Wide, >= 960 px (viewport preset `wide`). */
export const Wide: Story = { globals: { viewport: { value: 'wide', isRotated: false } } }

/** Narrow, <= 640 px (viewport preset `narrow`). */
export const Narrow: Story = { globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Rail collapsed to a strip. */
export const RailCollapsed: Story = { args: { rail: 'collapsed' }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Management drawer closed. */
export const DrawerClosed: Story = { args: { drawer: false }, globals: { viewport: { value: 'wide', isRotated: false } } }

/** Rail as an overlay from the left. */
export const NarrowRail: Story = { args: { overlay: 'rail' }, globals: { viewport: { value: 'narrow', isRotated: false } } }

/** Drawer as a bottom sheet. */
export const NarrowDrawer: Story = { args: { overlay: 'drawer' }, globals: { viewport: { value: 'narrow', isRotated: false } } }
