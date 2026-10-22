<script setup lang="ts">
// The whole app in one story. `start` is the route the app opens at, so a journey story starts at the
// journey's first screen; the router is shared between stories, so it is reset on every mount.
import { onBeforeMount, ref } from 'vue'
import { useRouter } from 'vue-router'
import Shell from './Shell.vue'

const props = withDefaults(defineProps<{ start?: string }>(), { start: '/' })
const router = useRouter()
const ready = ref(false)

onBeforeMount(async () => {
  await router.replace(props.start)
  ready.value = true
})
</script>

<template>
  <Shell v-if="ready" />
</template>
