import { defineModel, entity, f, sharedEnum } from './skaile-model'

export const Cuisine = sharedEnum({
  Italian: 'Pasta, pizza, risotto',
  Asian: 'Noodles, curry, sushi',
  Mediterranean: 'Mezze, grilled dishes, salads',
  Local: 'Regional home cooking',
  Vegetarian: 'Meat-free kitchen',
})

export const Member = entity({
  glossary: 'member',
  display: 'Member',
  label_field: 'display_name',
  fields: {
    display_name: f.string({ max_length: 80 }),
    email: f.email({ unique: true }),
    diet: f.enum({ Any: 'Eats everything', Vegetarian: 'No meat or fish', Vegan: 'No animal products' }),
  },
})

export const Place = entity({
  glossary: 'place',
  display: 'Place',
  label_field: 'name',
  fields: {
    name: f.string({ max_length: 100 }),
    cuisine: f.enumRef(Cuisine),
    walking_minutes: f.integer({ description: 'Minutes on foot from the office door' }),
    website: f.url({ required: false }),
    price_level: f.integer({ required: false, proposed: { by: 'mockup-storybook', on: '2026-10-22', source: 'PlaceCard needs a price hint next to the walking time' } }),
  },
})

export const Poll = entity({
  glossary: 'poll',
  display: 'Poll',
  label_field: 'title',
  fields: {
    title: f.string({ max_length: 120 }),
    status: f.enum({ Open: 'Members can still vote', Closed: 'Voting is over, a pick is made' }),
    closes_at: f.datetime(),
    organizer_id: f.m2o(() => Member, { on_delete: 'restrict' }),
    pick_id: f.m2o(() => Place, { required: false, on_delete: 'set_null', label: 'Pick' }),
  },
})

export const Vote = entity({
  glossary: 'vote',
  display: 'Vote',
  label_field: 'reason',
  fields: {
    reason: f.string({ max_length: 140, required: false }),
    poll_id: f.m2o(() => Poll, { on_delete: 'cascade' }),
    place_id: f.m2o(() => Place, { on_delete: 'cascade' }),
    member_id: f.m2o(() => Member, { on_delete: 'cascade' }),
  },
})

export const model = defineModel({
  entities: {
    Member,
    Place,
    Poll,
    Vote,
  },
  enums: {
    cuisine: Cuisine,
  },
})
