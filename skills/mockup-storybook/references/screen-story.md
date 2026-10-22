# Screen stories — a worked example

One screen, `inbox`, laid out in the `master-detail` floorplan. Both files ran green under `npm run check` in a smoke project (build, `vue-tsc`, the stories rendered in Chromium at both viewport presets). The step is `tree/09_mockup/storybook/README.md § Writing it` step 4; the screen spec it reads is `tree/07_screens/[screen].md § Format`.

## What the spec decides

- `floorplan: master-detail` names the component: `src/floorplans/master-detail.vue`, one of the 16 that ship with the package.
- `regions:` binds floorplan regions to what they show. The floorplan's slots are named after its `§ Regions` in `rulebook/floorplans/master-detail/README.md`, in kebab-case (`toolbar`, `list`, `activity-strip`, `detail`); a region the spec leaves unbound keeps the floorplan's neutral placeholder.
- The seed supplies the rows. `useStore().rows('task')` follows the `scenario` toolbar, so the same screen shows `populated`, `empty` and `edge_cases` data without a line of story code.
- `Screen` wraps the root with `data-screen="inbox"`. `useInShell()` is true when the screen renders inside the app's shell (the `App` and `Journeys/*` stories) and false alone, so a screen passes `:chrome="!inShell"` to its floorplan: `Screens/inbox` shows the floorplan's `shell` region as a placeholder and the app does not draw the shell twice.
- Master-detail's `detail` prop picks the pane shown at the `narrow` breakpoint, so the screen binds it to its selection.

## The screen

`src/screens/inbox.vue`:

```vue
<script setup lang="ts">
// Screen `inbox` (_concept/07_screens/inbox.md): floorplan master-detail. The task list is the
// master, the editor of the selected task the detail, the toolbar holds the one create action.
import { ref } from 'vue'
import type { Task } from '@model/model'
import type { Infer } from '@model/skaile-model'
import Screen from '../components/Screen.vue'
import { useInShell } from '../components/shell-context'
import MasterDetail from '../floorplans/master-detail.vue'
import TaskEditor from '../entities/Task/TaskEditor.vue'
import TaskRow from '../entities/Task/TaskRow.vue'
import { useStore } from '../model/store'

const tasks = useStore().rows<Infer<typeof Task>>('task')
const inShell = useInShell()
const selected = ref<string>()
</script>

<template>
  <Screen id="inbox">
    <MasterDetail :chrome="!inShell" :detail="selected !== undefined" @back="selected = undefined">
      <template #toolbar>
        <div class="flex items-center justify-between gap-3">
          <h1 class="text-lg font-semibold">Inbox</h1>
          <UButton to="/task-new">New task</UButton>
        </div>
      </template>
      <template #list>
        <p v-if="tasks.length === 0" class="p-3 text-muted">No tasks yet.</p>
        <button v-for="task in tasks" :key="task.id" type="button" class="block w-full text-left" @click="selected = task.id">
          <TaskRow :task="task" />
        </button>
      </template>
      <template #detail>
        <TaskEditor v-if="selected" :key="selected" :task-id="selected" @saved="selected = undefined" />
        <p v-else class="text-muted">Select a task to edit it.</p>
      </template>
    </MasterDetail>
  </Screen>
</template>
```

## The story

`src/screens/inbox.stories.ts`: `Default` shows the `populated` scenario (the toolbar's default), `Empty` the empty state the spec's `### Situations` lists. A situation the globals do not cover, such as a loading list, is one more story with its own args.

```ts
import type { Meta, StoryObj } from '@storybook/vue3-vite'
import Inbox from './inbox.vue'

const meta = {
  title: 'Screens/inbox',
  component: Inbox,
  tags: ['autodocs'],
} satisfies Meta<typeof Inbox>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {}

export const Empty: Story = { globals: { scenario: 'empty' } }
```

Open the story at `narrow` and `wide` (the viewport toolbar) before reporting the screen: the floorplan's `§ Responsive` is what the review checks.

## A screen without a floorplan region to bind

A screen that is one form, like `task-new` (the `Task` editor on its own page), skips the floorplan: `Screen` as the root, a heading, and the entity component. The floorplan is a choice the spec records, and a screen whose spec has none takes the plain form:

```vue
<script setup lang="ts">
// Screen `task-new`: the Task editor on its own page. Spec: _concept/07_screens/task-new.md.
import { useRouter } from 'vue-router'
import Screen from '../components/Screen.vue'
import TaskEditor from '../entities/Task/TaskEditor.vue'

const router = useRouter()
</script>

<template>
  <Screen id="task-new" class="flex flex-col gap-4 p-6">
    <h1 class="text-xl font-semibold">New task</h1>
    <TaskEditor @saved="router.push('/inbox')" />
  </Screen>
</template>
```
