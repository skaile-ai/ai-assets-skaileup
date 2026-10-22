import { scenarios } from './skaile-model'
import { model } from './model'

export const seed = scenarios(model, {
  empty: { description: 'No data yet', data: { user: [], task: [] } },
  single_user: {
    description: 'One user, no tasks',
    data: {
      user: [{ id: 'u1', display_name: 'Maria Schmidt', email: 'maria.schmidt@example.com' }],
      task: [],
    },
  },
  populated: {
    description: 'Two users, tasks in both statuses',
    data: {
      user: [
        { id: 'u1', display_name: 'Maria Schmidt', email: 'maria.schmidt@example.com' },
        { id: 'u2', display_name: 'Jean-Pierre Dubois', email: 'jean-pierre.dubois@example.com' },
      ],
      task: [
        { id: 't1', title: 'Design landing page', status: 'Published', due_date: '2026-04-01', owner_id: 'u1' },
        { id: 't2', title: 'Write user documentation', status: 'Draft', owner_id: 'u2' },
      ],
    },
  },
  edge_cases: {
    description: 'Long and minimal values',
    data: {
      user: [{ id: 'u10', display_name: 'María José Fernández-García de la Cruz', email: 'a@b.co' }],
      task: [{ id: 't10', title: 'A', status: 'Draft', due_date: null, owner_id: 'u10' }],
    },
  },
})
