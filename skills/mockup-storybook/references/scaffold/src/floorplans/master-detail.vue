<script setup lang="ts">
import './floorplan.css'

// Regions: shell, toolbar, list, activity-strip, detail (rulebook/floorplans/master-detail § Regions).
// Narrow: the list and the detail are separate views; `detail` picks the one shown.
withDefaults(defineProps<{ chrome?: boolean; detail?: boolean }>(), { chrome: true, detail: false })
const emit = defineEmits<{ back: [] }>()
</script>

<template>
  <div class="md fp-fill" data-floorplan="master-detail" :class="{ 'show-detail': detail }">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="md-work">
      <div class="fp-card md-toolbar" data-region="toolbar">
        <slot name="toolbar"><span class="fp-ph">toolbar</span></slot>
      </div>
      <div class="md-split">
        <div class="md-left">
          <div class="fp-card md-list" data-region="list">
            <slot name="list"><span class="fp-ph">list</span></slot>
          </div>
          <div class="md-strip" data-region="activity-strip">
            <slot name="activity-strip"><span class="fp-ph">activity-strip</span></slot>
          </div>
        </div>
        <aside class="fp-card md-detail" data-region="detail">
          <button class="fp-btn md-back" type="button" @click="emit('back')">‹ Back to list</button>
          <slot name="detail"><span class="fp-ph">detail</span></slot>
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped>
.md-work { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--fp-gap); padding: var(--fp-gap); }
.md-toolbar { flex: none; }
.md-split { flex: 1; min-height: 0; display: grid; grid-template-columns: 1fr 360px; gap: var(--fp-gap); }
.md-left { min-height: 0; display: flex; flex-direction: column; gap: var(--fp-gap); }
.md-list { flex: 1; min-height: 0; overflow: auto; }
.md-strip { flex: none; }
.md-detail { min-height: 0; overflow: auto; }
.md-back { display: none; margin-bottom: 8px; }

@media (max-width: 640px) {
  [data-floorplan].md { height: auto; min-height: var(--fp-h, 100vh); }
  .md-work { padding: 8px; }
  .md-split { display: block; }
  .md-detail { display: none; }
  .md-strip { display: none; }
  .show-detail .md-left { display: none; }
  .show-detail .md-detail { display: block; }
  .md-back { display: inline-block; }
}
</style>
