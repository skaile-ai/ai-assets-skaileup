<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { NavEntry } from '../components/nav-types'

// One destination of a shell floorplan's nav. `current` (a `to` value) marks the active entry explicitly;
// without it the router's exact match decides.
defineProps<{ entry: NavEntry; current?: string }>()
</script>

<template>
  <RouterLink
    :to="entry.to"
    class="fp-nav"
    :class="{ 'is-current': current !== undefined && current === entry.to }"
    :exact-active-class="current === undefined ? 'is-current' : 'fp-nav-inactive'"
  >
    <slot>{{ entry.label }}</slot>
  </RouterLink>
</template>
