import { scenarios } from './skaile-model'
import { model } from './model'

const t0 = '2026-10-19T08:00:00Z'

export const seed = scenarios(model, {
  empty: { description: 'Nobody has created a poll yet - tests the empty states', data: { member: [], place: [], poll: [], vote: [] } },
  single_user: {
    description: 'One member with a short place list and no poll - tests the first poll',
    data: {
      member: [{ id: 'm1', display_name: 'Maria Schmidt', email: 'maria.schmidt@example.com', diet: 'Any', created_at: t0, updated_at: t0 }],
      place: [
        { id: 'p1', name: 'Trattoria da Enzo', cuisine: 'Italian', walking_minutes: 4, created_at: t0, updated_at: t0 },
        { id: 'p2', name: 'Noodle Bar Kita', cuisine: 'Asian', walking_minutes: 7, created_at: t0, updated_at: t0 },
      ],
      poll: [],
      vote: [],
    },
  },
  populated: {
    description: 'A team of five, six places, one open and one closed poll with votes',
    data: {
      member: [
        { id: 'm1', display_name: 'Maria Schmidt', email: 'maria.schmidt@example.com', diet: 'Any', created_at: t0, updated_at: t0 },
        { id: 'm2', display_name: 'Jean-Luc Moreau', email: 'jl.moreau@studio.example.fr', diet: 'Vegetarian', created_at: t0, updated_at: t0 },
        { id: 'm3', display_name: 'Aiko Tanaka', email: 'aiko.tanaka@example.co.jp', diet: 'Any', created_at: t0, updated_at: t0 },
        { id: 'm4', display_name: 'Carlos Ruiz', email: 'carlos@mail.example.es', diet: 'Vegan', created_at: t0, updated_at: t0 },
        { id: 'm5', display_name: 'Lena Fischer', email: 'lena.fischer@example.com', diet: 'Any', created_at: t0, updated_at: t0 },
      ],
      place: [
        { id: 'p1', name: 'Trattoria da Enzo', cuisine: 'Italian', walking_minutes: 4, website: 'https://enzo.example.com', created_at: t0, updated_at: t0 },
        { id: 'p2', name: 'Noodle Bar Kita', cuisine: 'Asian', walking_minutes: 7, created_at: t0, updated_at: t0 },
        { id: 'p3', name: 'Mezze Garden', cuisine: 'Mediterranean', walking_minutes: 9, website: 'https://mezze-garden.example.org', created_at: t0, updated_at: t0 },
        { id: 'p4', name: 'Zum Löwen', cuisine: 'Local', walking_minutes: 3, created_at: t0, updated_at: t0 },
        { id: 'p5', name: 'Green Fork', cuisine: 'Vegetarian', walking_minutes: 11, price_level: 2, created_at: t0, updated_at: t0 },
        { id: 'p6', name: 'Pho 24', cuisine: 'Asian', walking_minutes: 6, created_at: t0, updated_at: t0 },
      ],
      poll: [
        { id: 'q1', title: 'Friday lunch', status: 'Open', closes_at: '2026-10-23T10:30:00Z', organizer_id: 'm1', created_at: '2026-10-22T09:00:00Z', updated_at: '2026-10-22T09:00:00Z' },
        { id: 'q2', title: 'Team lunch after the release', status: 'Closed', closes_at: '2026-10-16T10:30:00Z', organizer_id: 'm3', pick_id: 'p3', created_at: '2026-10-15T09:00:00Z', updated_at: '2026-10-16T10:30:00Z' },
      ],
      vote: [
        { id: 'v1', poll_id: 'q1', place_id: 'p1', member_id: 'm1', created_at: '2026-10-22T09:10:00Z', updated_at: '2026-10-22T09:10:00Z' },
        { id: 'v2', poll_id: 'q1', place_id: 'p5', member_id: 'm2', created_at: '2026-10-22T09:12:00Z', updated_at: '2026-10-22T09:12:00Z' },
        { id: 'v3', poll_id: 'q1', place_id: 'p1', member_id: 'm3', created_at: '2026-10-22T09:20:00Z', updated_at: '2026-10-22T09:20:00Z' },
        { id: 'v4', poll_id: 'q2', place_id: 'p3', member_id: 'm1', created_at: '2026-10-15T09:30:00Z', updated_at: '2026-10-15T09:30:00Z' },
        { id: 'v5', poll_id: 'q2', place_id: 'p3', member_id: 'm2', created_at: '2026-10-15T09:31:00Z', updated_at: '2026-10-15T09:31:00Z' },
        { id: 'v6', poll_id: 'q2', place_id: 'p6', member_id: 'm4', created_at: '2026-10-15T09:40:00Z', updated_at: '2026-10-15T09:40:00Z' },
        { id: 'v7', poll_id: 'q2', place_id: 'p3', member_id: 'm5', created_at: '2026-10-15T09:55:00Z', updated_at: '2026-10-15T09:55:00Z' },
      ],
    },
  },
  edge_cases: {
    description: 'Long names, umlauts, missing optionals and a poll nobody voted in',
    data: {
      member: [
        { id: 'm1', display_name: 'Maximiliane Alexandra von Hohenlohe-Schillingsfürst-Wartenberg zu Löwenstein-Wertheim-Freudenberg', email: 'm.hohenlohe@sub.example.co.uk', diet: 'Vegan', created_at: t0, updated_at: t0 },
        { id: 'm2', display_name: 'X', email: 'x+lunch@example.com', diet: 'Any', created_at: t0, updated_at: t0 },
      ],
      place: [
        { id: 'p1', name: 'Café Zur Goldenen Gans & Brauerei "Alte Schmiede" am Marktplatz Nr. 1 – Bio, Regional, Saisonal, seit 1887', cuisine: 'Local', walking_minutes: 0, website: null, price_level: null, created_at: t0, updated_at: t0 },
        { id: 'p2', name: 'Çiğ Köfte & Ayran', cuisine: 'Vegetarian', walking_minutes: 45, created_at: t0, updated_at: t0 },
      ],
      poll: [
        { id: 'q1', title: 'Wohin gehen wir heute? Bitte bis 11:00 abstimmen, danach wird ausgewürfelt', status: 'Open', closes_at: '2026-10-23T11:00:00Z', organizer_id: 'm2', pick_id: null, created_at: t0, updated_at: t0 },
      ],
      vote: [],
    },
  },
})
