import { createMemoryHistory, createRouter } from 'vue-router'
import { routes } from './routes'

// In-memory: the whole app runs inside one story and never touches the iframe's address.
export const router = createRouter({ history: createMemoryHistory(), routes })
