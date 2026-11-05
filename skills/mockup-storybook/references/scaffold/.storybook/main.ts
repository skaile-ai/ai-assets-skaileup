import { annotationInbox } from '@skaile/forge-annotation-inbox/vite'
import type { StorybookConfig } from '@storybook/vue3-vite'
import { VueTracer } from 'vite-plugin-vue-tracer'
import { writeConcept } from '../scripts/gen-concept.ts'
import { inboxEndpoint } from '../scripts/inbox.ts'

// The concept index and the `Features/*` story files are generated here, at module load,
// rather than in a Vite `config` hook like the tokens: Storybook builds its story index from
// the `stories` globs before Vite runs, so a feature story written any later is not indexed.
writeConcept()

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.ts'],
  addons: ['@storybook/addon-docs', '@storybook/addon-links', '@storybook/addon-vitest'],
  framework: { name: '@storybook/vue3-vite', options: { docgen: 'vue-component-meta' } },
  core: { disableTelemetry: true },
  viteFinal: (viteConfig) => ({
    ...viteConfig,
    plugins: [
      ...(viteConfig.plugins ?? []),
      // Annotations: `VueTracer` records `file:line:col` of every template element, so a note
      // names the SFC line it was made on; `annotationInbox()` is the client half (no endpoint
      // of its own) and `inboxEndpoint()` answers `/__annotations` into `<project>/.data/`.
      // None of it belongs in a headless Vitest run.
      ...(process.env.VITEST ? [] : [VueTracer(), annotationInbox(), inboxEndpoint()]),
    ],
  }),
}

export default config
