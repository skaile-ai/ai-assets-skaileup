import type { Meta, StoryObj } from '@storybook/vue3-vite'
import App from './App.vue'

const meta = {
  title: 'App',
  component: App,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof App>

export default meta

/** The whole app inside the shell, opened at its first screen. */
export const Default: StoryObj<typeof meta> = {}
