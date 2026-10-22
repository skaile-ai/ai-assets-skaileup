<script setup lang="ts">
// Root of every screen. `data-screen` is the one attribute the package emits: journey play
// functions assert navigation on it.
defineProps<{ id: string }>()
</script>

<template>
  <section :data-screen="id" class="min-h-full">
    <slot />
  </section>
</template>
