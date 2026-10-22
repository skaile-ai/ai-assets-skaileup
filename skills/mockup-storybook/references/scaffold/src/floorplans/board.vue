<script setup lang="ts">
import './floorplan.css'

// Regions: shell, view-switch, filter-bar, items, card-drawer (rulebook/floorplans/board § Regions).
// `drawer` shows the card drawer: a docked column on wide, a bottom sheet on narrow.
withDefaults(defineProps<{ chrome?: boolean; drawer?: boolean }>(), { chrome: true, drawer: true })
</script>

<template>
  <div class="bd fp-page" data-floorplan="board">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="bd-frame">
      <div class="bd-switch" data-region="view-switch">
        <slot name="view-switch"><span class="fp-ph">view-switch</span></slot>
      </div>
      <div class="fp-card bd-filters" data-region="filter-bar">
        <slot name="filter-bar"><span class="fp-ph">filter-bar</span></slot>
      </div>
      <div class="bd-work">
        <div class="fp-card bd-items" data-region="items">
          <slot name="items"><span class="fp-ph">items</span></slot>
        </div>
        <aside v-show="drawer" class="fp-card bd-drawer" data-region="card-drawer">
          <slot name="card-drawer"><span class="fp-ph">card-drawer</span></slot>
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bd-frame { flex: 1; width: 100%; max-width: 1240px; margin: 0 auto; padding: var(--fp-gap); display: flex; flex-direction: column; gap: var(--fp-gap); }
.bd-switch { padding: 6px 0; }
.bd-work { flex: 1; display: flex; gap: var(--fp-gap); align-items: stretch; min-height: 0; }
.bd-items { flex: 1; min-width: 0; min-height: 320px; overflow-x: auto; }
.bd-drawer { flex: 0 0 320px; }

@media (max-width: 960px) {
  .bd-drawer { flex-basis: 280px; }
}
@media (max-width: 640px) {
  .bd-frame { padding: 8px; gap: 8px; }
  .bd-work { display: block; }
  .bd-drawer {
    position: sticky; bottom: 0; z-index: 5; max-height: 68vh; overflow: auto;
    border-radius: 12px 12px 0 0; box-shadow: 0 -4px 0 var(--fp-border);
  }
}
</style>
