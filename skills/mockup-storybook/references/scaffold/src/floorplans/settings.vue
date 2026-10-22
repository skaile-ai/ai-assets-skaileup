<script setup lang="ts">
import './floorplan.css'

// Regions: shell, section-nav, section-header, section-body, save-bar (rulebook/floorplans/settings § Regions).
// Wide: nav column at the left, header, body and save bar to its right. Narrow: nav becomes a tab strip above
// the header, one column, the save bar sticks to the bottom edge.
withDefaults(defineProps<{ chrome?: boolean }>(), { chrome: true })
</script>

<template>
  <div class="st fp-page" data-floorplan="settings">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="st-frame">
      <div class="st-layout">
        <nav class="fp-card st-nav" data-region="section-nav" aria-label="Sections">
          <slot name="section-nav"><span class="fp-ph">section-nav</span></slot>
        </nav>
        <header class="fp-card st-head" data-region="section-header">
          <slot name="section-header"><span class="fp-ph">section-header</span></slot>
        </header>
        <section class="fp-card st-body" data-region="section-body">
          <slot name="section-body"><span class="fp-ph">section-body</span></slot>
        </section>
        <div class="fp-card st-save" data-region="save-bar">
          <slot name="save-bar"><span class="fp-ph">save-bar</span></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.st-frame { flex: 1; width: 100%; max-width: 1040px; margin: 0 auto; padding: var(--fp-gap); }
.st-layout {
  display: grid; grid-template-columns: 200px minmax(0, 1fr);
  grid-template-areas: 'nav head' 'nav body' 'nav save';
  grid-template-rows: auto 1fr auto; gap: var(--fp-gap); align-items: start;
}
.st-nav { grid-area: nav; }
.st-head { grid-area: head; }
.st-body { grid-area: body; min-height: 280px; align-self: stretch; }
.st-save { grid-area: save; }

@media (max-width: 960px) {
  .st-layout { grid-template-columns: 160px minmax(0, 1fr); }
}
@media (max-width: 640px) {
  .st-frame { padding: 8px; }
  .st-layout { grid-template-columns: 1fr; grid-template-areas: 'nav' 'head' 'body' 'save'; grid-template-rows: none; gap: 8px; }
  .st-nav { overflow-x: auto; white-space: nowrap; }
  .st-body { min-height: 0; }
  .st-save { position: sticky; bottom: 0; z-index: 2; }
}
</style>
