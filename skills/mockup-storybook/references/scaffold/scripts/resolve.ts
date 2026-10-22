// Close annotations the agent has acted on: marks them `implemented` or `rejected` in
// `<project>/.data/annotations/`, the store the toolbar and forge read. Run from the package:
//   npx tsx scripts/resolve.ts --ids <inboxId>,<inboxId> --status implemented|rejected --resolution "<why>"
// `rejected` needs a resolution (the library's own rule over HTTP, applied here through the same
// request handler). `--root <dir>` points at another project root.
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parseArgs } from 'node:util'
import { INBOX_RESOLVE_ROUTE, openFileInbox } from '@ecsplico/annotation-inbox/inbox'
import { handleInboxRequest } from '@ecsplico/annotation-inbox/server'

const { values } = parseArgs({
  options: {
    ids: { type: 'string' },
    status: { type: 'string' },
    resolution: { type: 'string' },
    root: { type: 'string' },
  },
})

const fail = (message: string): never => {
  console.error(`resolve: ${message}`)
  process.exit(1)
}

const ids = (values.ids ?? '').split(',').map((id) => id.trim()).filter(Boolean)
if (ids.length === 0) fail('--ids <inboxId>[,<inboxId>...] is required')
if (values.status !== 'implemented' && values.status !== 'rejected') fail('--status must be implemented or rejected')

const root = values.root
  ? resolve(values.root)
  : resolve(dirname(fileURLToPath(import.meta.url)), '../../../..')

const response = await handleInboxRequest(openFileInbox(root), {
  method: 'POST',
  url: INBOX_RESOLVE_ROUTE,
  principal: { kind: 'agent', id: 'mockup-feedback', label: 'mockup-feedback' },
  body: JSON.stringify({ ids, status: values.status, resolution: values.resolution }),
})

if (response.status !== 200) fail(response.body)
const { resolved, unknown } = JSON.parse(response.body) as { resolved: string[]; unknown: string[] }
console.log(JSON.stringify({ resolved, unknown }))
if (unknown.length > 0) fail(`unknown ids: ${unknown.join(', ')}`)
