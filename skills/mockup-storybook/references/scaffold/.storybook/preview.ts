import { mountAnnotationToolbar } from '@skaile/forge-annotation-inbox/mount'
import { setup } from '@storybook/vue3-vite'
import type { Preview } from '@storybook/vue3-vite'
import ui from '@nuxt/ui/vue-plugin'
import { router } from '../src/app/router'
import StoryFrame from '../src/components/StoryFrame.vue'
import { applyGlobals, controls, defaultScenario, scenarioNames } from '../src/model/scenario'
import { createStore, provideStore } from '../src/model/store'
import '../src/styles/main.css'

setup((app) => {
  app.use(router)
  app.use(ui)
})
// `setup()` rather than a decorator: only Storybook's own renderer runs it, so Vitest never mounts the toolbar.
setup(() => mountAnnotationToolbar())

const preview: Preview = {
  initialGlobals: { scenario: defaultScenario, fail: 'off', theme: 'light', viewport: { value: 'wide', isRotated: false } },
  globalTypes: {
    scenario: {
      description: 'Seed scenario the stories show',
      toolbar: { title: 'Scenario', icon: 'database', items: scenarioNames, dynamicTitle: true },
    },
    fail: {
      description: 'Make every write of the fake store fail',
      toolbar: { title: 'Writes', icon: 'alert', items: [{ value: 'off', title: 'Writes succeed' }, { value: 'on', title: 'Writes fail' }], dynamicTitle: true },
    },
    theme: {
      description: 'Colour mode',
      toolbar: { title: 'Theme', icon: 'circlehollow', items: ['light', 'dark'], dynamicTitle: true },
    },
  },
  parameters: {
    layout: 'padded',
    viewport: {
      options: {
        narrow: { name: 'Narrow 390', styles: { width: '390px', height: '844px' } },
        wide: { name: 'Wide 1280', styles: { width: '1280px', height: '800px' } },
      },
    },
  },
  decorators: [
    (story, context) => {
      applyGlobals(context.globals)
      document.documentElement.classList.toggle('dark', context.globals.theme === 'dark')
      return {
        components: { story, StoryFrame },
        setup() {
          provideStore(createStore(controls))
        },
        template: '<StoryFrame><story /></StoryFrame>',
      }
    },
  ],
}

export default preview
