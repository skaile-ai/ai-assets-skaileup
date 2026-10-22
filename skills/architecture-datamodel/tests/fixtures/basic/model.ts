import { defineModel, entity, f, sharedEnum } from './skaile-model'

export const Priority = sharedEnum({
  Low: 'Can wait',
  Normal: 'Default urgency',
  High: 'Needs attention today',
})

export const User = entity({
  glossary: 'user',
  display: 'User',
  label_field: 'display_name',
  key_field: 'email',
  fields: {
    display_name: f.string({ max_length: 80, faker: 'faker.person.fullName' }),
    email: f.email({ unique: true, faker: 'faker.internet.email' }),
    avatar: f.image({ required: false }),
  },
})

export const Task = entity({
  glossary: 'task',
  display: 'Task',
  label_field: 'title',
  fields: {
    title: f.string({ max_length: 120 }),
    status: f.enum({ Draft: 'Initial state, not yet submitted', InReview: 'Awaiting approval', Published: 'Live and visible' }),
    priority: f.enumRef(Priority, { default: 'Normal' }),
    due_date: f.date({ required: false }),
    owner_id: f.m2o(() => User, { on_delete: 'cascade', label: 'Owner', inverse: 'Tasks' }),
    tags: f.m2m(() => Tag, { through: 'TaskTag' }),
    estimate: f.decimal({ required: false, proposed: { by: 'mockup-storybook', on: '2026-07-01', source: 'TaskEditor needs an effort estimate' } }),
  },
})

export const Tag = entity({
  glossary: 'tag',
  display: 'Tag',
  label_field: 'label',
  fields: {
    label: f.string({ max_length: 40, unique: true }),
  },
})

export const TaskTag = entity({
  glossary: 'task-tag',
  display: 'Task tag',
  label_field: 'task_id',
  fields: {
    task_id: f.m2o(() => Task, { on_delete: 'cascade' }),
    tag_id: f.m2o(() => Tag, { on_delete: 'cascade' }),
  },
})

export const model = defineModel({
  entities: {
    User,
    Task,
    Tag,
    TaskTag,
  },
  enums: {
    priority: Priority,
  },
})
