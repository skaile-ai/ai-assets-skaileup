# Journey stories — a worked example

One journey, `create-task`, from `04_journeys/stories.yaml` as a story. The file ran green under `npm run check` in a smoke project: the play function drives the real navigation of the `App` story in Chromium. The step is `tree/09_mockup/storybook/README.md § Writing it` step 6.

`src/journeys/create-task.stories.ts`:

```ts
import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { expect, userEvent, waitFor, within } from 'storybook/test'
import App from '../app/App.vue'

// Journey `create-task` (_concept/04_journeys/stories.yaml): from the inbox, add a task and see it listed.
const meta = {
  title: 'Journeys/create-task',
  component: App,
  parameters: { layout: 'fullscreen' },
  args: { start: '/inbox' },
} satisfies Meta<typeof App>

export default meta
type Story = StoryObj<typeof meta>

const onScreen = (canvasElement: HTMLElement, id: string) =>
  waitFor(() => expect(canvasElement.querySelector(`[data-screen="${id}"]`)).not.toBeNull())

export const Default: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await onScreen(canvasElement, 'inbox')
    await userEvent.click(await canvas.findByRole('link', { name: /new task/i }))
    await onScreen(canvasElement, 'task-new')
    await userEvent.type(await canvas.findByLabelText(/title/i), 'Water the plants')
    await userEvent.click(canvas.getByRole('button', { name: /save/i }))
    await onScreen(canvasElement, 'inbox')
    await canvas.findByText('Water the plants')
  },
}
```

What each part answers:

- `title: 'Journeys/<journey_id>'` is the journey's `id` from the story map verbatim, and the story id Storybook derives (`journeys-create-task--default`) is what triage reads to route a note on this story to `04_journeys/stories.yaml`.
- `args: { start: '/inbox' }` is the route of the journey's first screen, `/<screen_id>`; `App.vue` replaces the in-memory router's location with it before it renders.
- Every step of `steps[]` becomes one `userEvent` on a real control, found by role or label, and one `onScreen(canvasElement, '<screen_id>')` for the screen the step's `system_response` shows. A journey the shell's own navigation cannot walk fails here, which is the point of the story.
- `[data-screen="<screen_id>"]` is the one attribute the package emits, set by `Screen.vue` on every screen root.
- The last line asserts the effect of the journey on the data, here the new task in the list; a journey whose last step shows nothing new asserts the final screen only.
- A `backlog` journey gets no story; a journey whose `candidate_screens` name a screen without a `src/screens/<screen_id>.vue` waits for that screen (`tree/09_mockup/storybook/README.md § Writing it` step 4) and the completion summary says so.
