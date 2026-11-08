import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import vue from '@vitejs/plugin-vue'
import ui from '@nuxt/ui/vite'
import { defineConfig } from 'vite'
import { skaileModel } from '@skaile/model/vite'
import { conceptSources, writeConcept } from './scripts/gen-concept.ts'
import { brandFiles, writeTokens } from './scripts/gen-tokens.ts'

const packageDir = dirname(fileURLToPath(import.meta.url))
// `_concept/10_blueprint/datamodel`: the authored `model.yaml` and `seed.yaml` live there. The
// `skaileModel` plugin serves them as `@model/model` and `@model/seed` and writes the row types of
// `@model/types` to `.skaile-model/model.d.ts` on start and on every change of the two files.
const datamodelDir = resolve(packageDir, '../../10_blueprint/datamodel')

export default defineConfig({
  plugins: [
    vue(),
    skaileModel({ dir: datamodelDir }),
    ui(),
    {
      // `src/styles/tokens.css` is generated from the brand tokens on every start, and again
      // when a brand file changes, so no run depends on a separate step.
      name: 'mockup:tokens',
      config: () => {
        writeTokens()
      },
      configureServer(server) {
        server.watcher.add(brandFiles)
        server.watcher.on('change', (file) => {
          if (brandFiles.includes(file)) writeTokens()
        })
      },
    },
    {
      // `src/generated/concept.json` and `src/features/` are written by `.storybook/main.ts` on
      // start; this rewrites them when a feature spec, screen spec, dossier or the stories file
      // changes, is added or is removed while `storybook dev` runs.
      name: 'mockup:concept',
      configureServer(server) {
        server.watcher.add(conceptSources)
        const regenerate = (file: string) => {
          if (conceptSources.some((source) => file.startsWith(source))) writeConcept()
        }
        server.watcher.on('change', regenerate)
        server.watcher.on('add', regenerate)
        server.watcher.on('unlink', regenerate)
      },
    },
  ],
  server: { fs: { allow: [packageDir, datamodelDir] } },
})
