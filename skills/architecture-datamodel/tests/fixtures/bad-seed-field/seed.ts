import { scenarios } from './skaile-model'
import { model } from './model'

export const seed = scenarios(model, {
  empty: {
    description: 'App with no user data yet — tests empty states',
    data: { user: [], task: [], tag: [], task_tag: [] },
  },
  single_user: {
    description: 'One user, no tasks — tests first-use experience',
    data: {
      user: [
        { id: 'u1', display_name: 'Maria Schmidt', email: 'maria.schmidt@example.com', created_at: '2026-03-01T10:00:00Z', updated_at: '2026-03-01T10:00:00Z' },
      ],
      task: [],
      tag: [],
      task_tag: [],
    },
  },
  populated: {
    description: 'Realistic usage — several users, mixed statuses and priorities',
    data: {
      user: [
        { id: 'u1', display_name: 'Maria Schmidt', email: 'maria.schmidt@example.com', created_at: '2026-03-01T10:00:00Z', updated_at: '2026-03-10T08:00:00Z' },
        { id: 'u2', display_name: 'Jean-Pierre Dubois', email: 'jean-pierre.dubois@example.com', avatar: 'avatars/jp.png', created_at: '2026-03-02T14:00:00Z', updated_at: '2026-03-09T16:00:00Z' },
      ],
      task: [
        { id: 't1', title: 'Design landing page', status: 'Published', priority: 'High', due_date: '2026-04-01', owner_id: 'u1', created_at: '2026-03-01T10:30:00Z', updated_at: '2026-03-07T15:00:00Z' },
        { id: 't2', title: 'Write user documentation', status: 'Draft', priority: 'Low', owner_id: 'u2', created_at: '2026-03-05T14:00:00Z', updated_at: '2026-03-05T14:00:00Z' },
        { id: 't3', title: 'Review pricing', status: 'InReview', priority: 'Normal', due_date: null, owner_id: 'u1', created_at: '2026-03-06T09:00:00Z', updated_at: '2026-03-06T09:00:00Z' },
      ],
      tag: [
        { id: 'g1', label: 'design', created_at: '2026-03-01T10:00:00Z', updated_at: '2026-03-01T10:00:00Z' },
        { id: 'g2', label: 'docs', created_at: '2026-03-01T10:00:00Z', updated_at: '2026-03-01T10:00:00Z' },
      ],
      task_tag: [
        { id: 'tt1', task_id: 't1', tag_id: 'g1', created_at: '2026-03-01T10:31:00Z', updated_at: '2026-03-01T10:31:00Z' },
        { id: 'tt2', task_id: 't2', tag_id: 'g2', created_at: '2026-03-05T14:01:00Z', updated_at: '2026-03-05T14:01:00Z' },
      ],
    },
  },
  edge_cases: {
    description: 'Stress-tests for layout, validation and i18n',
    data: {
      user: [
        { id: 'u10', display_name: 'María José Fernández-García de la Cruz', email: 'maría-josé.fernández-garcía-de-la-cruz@subdomain.example.co.uk' },
        { id: 'u11', display_name: 'X', email: 'a@b.co' },
      ],
      task: [
        { id: 't10', titel: 'A', status: 'Draft', priority: 'Low', due_date: null, owner_id: 'u11' },
      ],
      tag: [],
      task_tag: [],
    },
  },
})
