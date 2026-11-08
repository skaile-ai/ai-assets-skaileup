<script setup lang="ts">
// A shell destination whose screen is not specified yet (`/pending/<item-slug>`): the look
// checkpoint shows the whole frame before any screen exists. When the nav entry names an object,
// the sample rows of that object's `<Entity>Row.vue` show what the destination will hold.
import { computed } from 'vue'
import type { Component } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '../model/store'
import Screen from '../components/Screen.vue'
import { nav } from './nav'
import { labelOf } from './routes'

const SAMPLE_ROWS = 5
const rowComponents = import.meta.glob<{ default: Component }>('../entities/*/*Row.vue', { eager: true })

const route = useRoute()
const store = useStore()
const slug = computed(() => String(route.params.slug ?? ''))
const entry = computed(() => nav.find((item) => item.to === `/pending/${slug.value}`))
const label = computed(() => entry.value?.label ?? labelOf(slug.value))

/** `Task` → entity key `task`, which is also the Row component's prop name. */
const object = computed(() => entry.value?.object)
const entityKey = computed(() => (object.value ? object.value.replace(/^./, (c) => c.toLowerCase()) : ''))
const rowComponent = computed(() =>
  object.value ? rowComponents[`../entities/${object.value}/${object.value}Row.vue`]?.default : undefined,
)
const rows = computed(() => (entityKey.value ? store.rows(entityKey.value).slice(0, SAMPLE_ROWS) : []))
</script>

<template>
  <Screen :id="`pending-${slug}`">
    <div class="flex flex-col gap-4 p-6">
      <div>
        <h1 class="text-lg font-semibold">{{ label }}</h1>
        <p class="text-sm text-muted">Not specified yet: this destination gets its screen in the features stage.</p>
      </div>
      <ul v-if="rowComponent && rows.length > 0" class="flex flex-col gap-2">
        <li v-for="row in rows" :key="row.id">
          <component :is="rowComponent" v-bind="{ [entityKey]: row }" />
        </li>
      </ul>
      <p v-else-if="object" class="text-sm text-muted">{{ object }} has no row story yet.</p>
    </div>
  </Screen>
</template>
