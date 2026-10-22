<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { shells } from '../floorplans'
import { provideInShell } from '../components/shell-context'
import { labelOf, screenIds } from './routes'
import { nav, shell } from './nav'

provideInShell()
const route = useRoute()
const frame = shells[shell]
const entries = computed(() => (nav.length > 0 ? nav : screenIds.map((id) => ({ label: labelOf(id), to: `/${id}` }))))
</script>

<template>
  <component :is="frame" :nav="entries" :current="route.path" :title="labelOf(String(route.name ?? ''))">
    <RouterView />
  </component>
</template>
