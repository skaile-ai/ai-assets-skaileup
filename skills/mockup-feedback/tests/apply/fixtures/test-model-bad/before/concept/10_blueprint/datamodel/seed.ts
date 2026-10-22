import { scenarios } from './skaile-model'
import { model } from './model'

export const seed = scenarios(model, {
  empty: {
    description: 'No data yet',
    data: { user: [], task: [] },
  },
  single_user: {
    description: 'One user, no tasks',
    data: {
      user: [{ id: 'u1', display_name: 'Maria Schmidt', email: 'maria@example.com' }],
      task: [],
    },
  },
  populated: {
    description: 'Several tasks in mixed states',
    data: {
      user: [{ id: 'u1', display_name: 'Maria Schmidt', email: 'maria@example.com' }],
      task: [
        { id: 't1', title: 'Design landing page', status: 'Published', due_date: '2026-04-01', owner_id: 'u1' },
        { id: 't2', title: 'Write documentation', status: 'Draft', owner_id: 'u1' },
      ],
    },
  },
  edge_cases: {
    description: 'Long and short values',
    data: {
      user: [{ id: 'u1', display_name: 'X', email: 'a@b.co' }],
      task: [{ id: 't1', title: 'A', status: 'Draft', owner_id: 'u1' }],
    },
  },
})
