import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import vue from '@vitejs/plugin-vue'
import ui from '@nuxt/ui/vite'
import { defineConfig } from 'vite'
import { brandFiles, writeTokens } from './scripts/gen-tokens.ts'

const packageDir = dirname(fileURLToPath(import.meta.url))
// `_concept/10_blueprint/datamodel`: the authored `model.ts` and `seed.ts` live there and are
// imported as `@model/model` and `@model/seed`.
const datamodelDir = resolve(packageDir, '../../10_blueprint/datamodel')

export default defineConfig({
  plugins: [
    vue(),
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
  ],
  resolve: { alias: { '@model': datamodelDir } },
  server: { fs: { allow: [packageDir, datamodelDir] } },
})
