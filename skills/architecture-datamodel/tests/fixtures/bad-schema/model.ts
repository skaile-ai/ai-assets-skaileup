import { defineModel, entity, f } from './skaile-model'

export const User = entity({
  glossary: 'user',
  display: 'User',
  label_field: 'displayName',
  fields: {
    displayName: f.string({ max_length: 80 }),
  },
})

export const model = defineModel({
  entities: {
    User,
  },
})
