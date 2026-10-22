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
    status: f.enum({ Draft: 'Initial state', Published: 'Live and visible' }),
    due_date: f.date({ required: false }),
    owner_id: f.m2o(() => User, { on_delete: 'cascade' }),
    estimate: f.decimal({ required: false, proposed: { by: 'mockup-feedback', on: '2026-10-23', source: 'k3m9x2-1' } }),
  },
})

export const Comment = entity({
  glossary: 'comment',
  display: 'Comment',
  label_field: 'body',
  proposed: { by: 'mockup-feedback', on: '2026-10-23', source: 'k3m9x2-4' },
  fields: {
    body: f.text(),
    task_id: f.m2o(() => Task, { on_delete: 'cascade' }),
  },
})

export const model = defineModel({
  entities: {
    User,
    Task,
    Comment,
  },
})
