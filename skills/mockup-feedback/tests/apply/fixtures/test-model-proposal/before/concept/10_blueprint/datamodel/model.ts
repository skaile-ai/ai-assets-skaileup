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
  },
})

export const model = defineModel({
  entities: {
    User,
    Task,
  },
})
