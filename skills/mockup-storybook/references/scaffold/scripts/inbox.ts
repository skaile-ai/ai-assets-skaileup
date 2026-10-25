// Annotation endpoint for `storybook dev`: answers `/__annotations` and writes every note to
// `<project>/.data/annotations/`, the store forge lists and the `annotation-inbox` skills read.
//
// It is not the package's own `annotationInbox({ endpoint: true })`: that plugin keeps the store
// under Vite's workspace root, which for this nested package is the package itself. This one
// opens the store at the project root, the directory holding `_concept/`.
import type { IncomingMessage, ServerResponse } from 'node:http'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { INBOX_DIR, INBOX_ROUTE, openFileInbox } from '@skaile/forge-annotation-inbox/inbox'
import { DEV_PRINCIPAL, handleInboxRequest } from '@skaile/forge-annotation-inbox/server'
import type { Plugin } from 'vite'

/** `_concept/09_mockup/storybook/scripts` -> the directory that holds `_concept/`. */
export const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../../../..')

export function inboxEndpoint(): Plugin {
  return {
    name: 'mockup:annotation-inbox',
    apply: 'serve',
    configureServer(server) {
      const inbox = openFileInbox(projectRoot)
      server.middlewares.use(INBOX_ROUTE, (req: IncomingMessage, res: ServerResponse) => {
        void (async () => {
          const response = await handleInboxRequest(inbox, {
            method: req.method ?? 'GET',
            // Connect strips the mount prefix; the handler wants the whole path.
            url: `${INBOX_ROUTE}${req.url ?? '/'}`,
            // A dev server is its owner's machine: whoever reaches it is the reviewer.
            principal: DEV_PRINCIPAL,
            body: async () => {
              const chunks: Buffer[] = []
              for await (const chunk of req) chunks.push(chunk as Buffer)
              return Buffer.concat(chunks).toString('utf8')
            },
          })
          res.statusCode = response.status
          for (const [name, value] of Object.entries(response.headers)) res.setHeader(name, value)
          res.end(response.body || undefined)
        })().catch((error: unknown) => {
          res.statusCode = 500
          res.end(String(error))
        })
      })
      server.config.logger.info(`annotation inbox: ${INBOX_ROUTE} -> ${resolve(projectRoot, INBOX_DIR)}/`)
    },
  }
}
