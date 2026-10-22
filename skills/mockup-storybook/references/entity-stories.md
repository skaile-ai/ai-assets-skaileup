# Entity stories — a worked example

One entity, `Task`, from the model to its stories. Every file below ran green under `npm run check` in a smoke project (build, `vue-tsc`, and the play functions in Chromium). The step is `tree/09_mockup/storybook/README.md § Writing it` step 5; the states are `tree/09_mockup/storybook/README.md § Globals and state stories`.

## The model the components run over

`_concept/10_blueprint/datamodel/model.ts` and `seed.ts`, in the layout `tree/10_blueprint/datamodel/model.md § Format` fixes:

```ts
import { defineModel, entity, f } from './skaile-model'

export const User = entity({
  glossary: 'user',
  display: 'User',
  label_field: 'display_name',
  fields: {
    display_name: f.string({ max_length: 80 }),
    email: f.email({ unique: true }),
  },
})

export const Task = entity({
  glossary: 'task',
  display: 'Task',
  label_field: 'title',
  fields: {
    title: f.string({ max_length: 120 }),
    notes: f.text({ required: false }),
    status: f.enum({ Draft: 'Initial state', Published: 'Live and visible' }),
    due_date: f.date({ required: false }),
    owner_id: f.m2o(() => User, { on_delete: 'cascade' }),
  },
})

export const model = defineModel({
  entities: {
    User,
    Task,
  },
})
```

```ts
import { scenarios } from './skaile-model'
import { model } from './model'

export const seed = scenarios(model, {
  empty: { description: 'Nothing yet', data: { user: [], task: [] } },
  single_user: {
    description: 'One user, no tasks',
    data: { user: [{ id: 'u1', display_name: 'Ada Lovelace', email: 'ada@example.org' }], task: [] },
  },
  populated: {
    description: 'Two users, a few tasks',
    data: {
      user: [
        { id: 'u1', display_name: 'Ada Lovelace', email: 'ada@example.org' },
        { id: 'u2', display_name: 'Grace Hopper', email: 'grace@example.org' },
      ],
      task: [
        { id: 't1', title: 'Write the compiler', status: 'Published', due_date: '2026-11-01', owner_id: 'u1' },
        { id: 't2', title: 'Debug the relay', status: 'Draft', owner_id: 'u2', notes: 'There is a moth.' },
      ],
    },
  },
  edge_cases: {
    description: 'Very long titles and a missing optional field',
    data: {
      user: [{ id: 'u1', display_name: 'A very long display name that keeps going and going past any sensible width', email: 'long@example.org' }],
      task: [{ id: 't1', title: 'An unreasonably long task title '.repeat(4).trim(), status: 'Draft', owner_id: 'u1' }],
    },
  },
})
```

## Rules the files follow

- The directory `src/entities/Task/` is named for the entity id in `model.ts`. Triage maps a note on any file in it to `Task`, so the name is exact.
- Row types come from the model: `import type { Task } from '@model/model'` and `import type { Infer } from '@model/skaile-model'`, then `Infer<typeof Task>`. `model.ts` does not re-export `Infer`.
- `useStore()` is called at the top of `<script setup>`, never inside a `computed` or a callback: `inject` needs the setup context.
- `rows('task')` returns one stable array per entity that follows the `scenario` toolbar; `save<Row>('task', draft)` rejects while the `fail` global is `on`, and `store.saving` and `store.error` drive the busy and failure states.
- Each field is one `Field` wrapper. `Field` checks `name` against the row type, so a field the model lacks fails `vue-tsc` where the editor is written.
- A state is a story. The scenario and failure states are story-level `globals`; interactions are `play` functions importing from `storybook/test`.

## The editor and the row

`src/entities/Task/TaskEditor.vue`:

```vue
<script setup lang="ts">
// Editor of one Task row: a UForm of Field wrappers over the model's fields, saved through the
// fake store. `Field` checks every `name` against the row type, so a field the model lacks fails vue-tsc.
import { ref } from 'vue'
import type { FormError } from '@nuxt/ui'
import type { Task } from '@model/model'
import type { Infer } from '@model/skaile-model'
import Field from '../../components/Field.vue'
import { useStore } from '../../model/store'
import type { Draft } from '../../model/store'

type TaskRow = Infer<typeof Task>

const props = defineProps<{ taskId?: string }>()
const emit = defineEmits<{ saved: [task: TaskRow] }>()

const store = useStore()
const existing = store.rows<TaskRow>('task').find((task) => task.id === props.taskId)
const draft = ref<Draft<TaskRow>>(
  existing
    ? { ...existing }
    : { title: '', status: 'Draft', owner_id: store.rows('user')[0]?.id ?? '' },
)

const validate = (row: Partial<TaskRow>): FormError[] => (row.title ? [] : [{ name: 'title', message: 'A task needs a title' }])

async function submit() {
  try {
    emit('saved', await store.save<TaskRow>('task', draft.value))
  } catch {
    // `store.error` carries the message shown below.
  }
}
</script>

<template>
  <UForm :state="draft" :validate="validate" class="flex max-w-xl flex-col gap-4" @submit="submit">
    <p class="text-sm text-muted">Every task has a title and an owner.</p>
    <Field v-model:row="draft" name="title" label="Title" required />
    <Field v-model:row="draft" name="notes" type="text" label="Notes" />
    <Field v-model:row="draft" name="status" type="enum" :options="['Draft', 'Published']" label="Status" />
    <Field v-model:row="draft" name="due_date" type="date" label="Due date" />
    <Field v-model:row="draft" name="owner_id" type="m2o" relation="user" label-field="display_name" label="Owner" />
    <UAlert v-if="store.error.value" color="error" variant="subtle" :title="store.error.value" />
    <div>
      <UButton type="submit" :loading="store.saving.value">Save</UButton>
    </div>
  </UForm>
</template>
```

`src/entities/Task/TaskRow.vue`:

```vue
<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '@model/model'
import type { Infer } from '@model/skaile-model'
import { useStore } from '../../model/store'

type TaskRow = Infer<typeof Task>

const props = defineProps<{ task: TaskRow }>()
const store = useStore()
const owner = computed(() => store.rows('user').find((user) => user.id === props.task.owner_id))
</script>

<template>
  <div class="flex items-center gap-3 rounded-[var(--ui-radius)] border border-default p-3">
    <span class="min-w-0 flex-1 truncate font-medium">{{ task.title }}</span>
    <UBadge :color="task.status === 'Published' ? 'success' : 'neutral'" variant="subtle">{{ task.status }}</UBadge>
    <span v-if="task.due_date" class="text-sm text-muted">{{ task.due_date }}</span>
    <span class="text-sm text-muted">{{ owner?.display_name ?? 'Unassigned' }}</span>
  </div>
</template>
```

## The stories

`src/entities/Task/TaskEditor.stories.ts`, one story per state (`Default`, `Empty`, `Saving`, `Error`, `EdgeCases`):

```ts
import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { expect, userEvent, waitFor, within } from 'storybook/test'
import TaskEditor from './TaskEditor.vue'

const meta = {
  title: 'Entities/Task/TaskEditor',
  component: TaskEditor,
  tags: ['autodocs'],
} satisfies Meta<typeof TaskEditor>

export default meta
type Story = StoryObj<typeof meta>

/** An existing task of the populated scenario. */
export const Default: Story = { args: { taskId: 't1' } }

/** A new task, in a project with no data. */
export const Empty: Story = { globals: { scenario: 'empty' } }

/** Saving: the button is busy until the store answers. */
export const Saving: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await userEvent.type(await canvas.findByLabelText(/title/i), 'Water the plants')
    await userEvent.click(canvas.getByRole('button', { name: /save/i }))
    await waitFor(() => expect(canvas.getByRole('button', { name: /save/i })).toBeDisabled())
  },
}

/** A failing write shows the store's message and keeps the form. */
export const Error: Story = {
  globals: { fail: 'on' },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await userEvent.type(await canvas.findByLabelText(/title/i), 'Water the plants')
    await userEvent.click(canvas.getByRole('button', { name: /save/i }))
    await canvas.findByText(/did not answer/i)
  },
}

/** Long values and a missing optional field. */
export const EdgeCases: Story = {
  args: { taskId: 't1' },
  globals: { scenario: 'edge_cases' },
}
```

`src/entities/Task/TaskRow.stories.ts`, a display component with the variants its data allows:

```ts
import type { Meta, StoryObj } from '@storybook/vue3-vite'
import TaskRow from './TaskRow.vue'

const meta = {
  title: 'Entities/Task/TaskRow',
  component: TaskRow,
  tags: ['autodocs'],
} satisfies Meta<typeof TaskRow>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: { task: { id: 't1', title: 'Write the compiler', status: 'Published', due_date: '2026-11-01', owner_id: 'u1' } },
}

export const LongTitle: Story = {
  args: { task: { id: 't2', title: 'An unreasonably long task title '.repeat(4), status: 'Draft', owner_id: 'missing' } },
}
```

## The proposal move

The editor above needs an effort estimate and the model has none. Append one line to `Task` in `model.ts`, after the last field and inside `fields: { … }`, then run `npx tsx gen.ts` in `_concept/10_blueprint/datamodel/`:

```ts
    estimate: f.decimal({ required: false, proposed: { by: 'mockup-storybook', on: '2026-10-23', source: 'TaskEditor needs an effort estimate' } }),
```

`gen.ts` writes the field into `model.json` as `task_estimate` with `"status": "proposed"`, `proposed_by`, `proposed_on` and `source`, which is how `architecture-datamodel` and the owner see it. Then add `<Field v-model:row="draft" name="estimate" type="decimal" label="Estimate" />` to the editor. A field that is not in `model.ts` fails `vue-tsc` at the `Field`; a seed row that misspells a field fails `tsc` at the seed. A whole new entity is appended the same way: an `entity({ … proposed: { … } })` export above `defineModel`, plus its `    <Id>,` line in `entities: { … }`, all marked proposed.
