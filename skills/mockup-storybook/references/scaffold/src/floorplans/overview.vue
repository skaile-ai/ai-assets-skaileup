<script setup lang="ts">
import './floorplan.css'

// Regions: shell, header, attention, recent, row-peek (rulebook/floorplans/overview § Regions).
// Wide: attention blocks in two columns, `recent` to the right (below from 960 px down);
// narrow: one column in the same order, the row-peek an inline expansion.
withDefaults(defineProps<{ chrome?: boolean; peek?: boolean }>(), { chrome: true, peek: false })
</script>

<template>
  <div class="ov fp-page" data-floorplan="overview">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="ov-frame">
      <div class="fp-card ov-header" data-region="header">
        <slot name="header"><span class="fp-ph">header</span></slot>
      </div>
      <div class="ov-cols">
        <div class="ov-left">
          <div class="ov-attention" data-region="attention">
            <slot name="attention">
              <span v-for="n in 4" :key="n" class="fp-ph ov-block">attention · block {{ n }}</span>
            </slot>
          </div>
          <div v-show="peek" class="fp-card ov-peek" data-region="row-peek">
            <slot name="row-peek"><span class="fp-ph">row-peek</span></slot>
          </div>
        </div>
        <aside class="ov-recent" data-region="recent">
          <slot name="recent"><span class="fp-ph">recent</span></slot>
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ov-frame { flex: 1; width: 100%; max-width: 1120px; margin: 0 auto; padding: var(--fp-gap); display: flex; flex-direction: column; gap: var(--fp-gap); }
.ov-cols { display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 1fr); gap: var(--fp-gap); align-items: start; }
.ov-left { position: relative; display: flex; flex-direction: column; gap: var(--fp-gap); }
.ov-attention { display: grid; grid-template-columns: 1fr 1fr; gap: var(--fp-gap); }
.ov-block { min-height: 140px; }
.ov-recent { min-height: 140px; }
.ov-peek { position: absolute; left: var(--fp-gap); right: var(--fp-gap); top: 60px; z-index: 2; border-color: var(--fp-tier3); box-shadow: 0 6px 20px var(--fp-border); }

@media (max-width: 960px) {
  .ov-cols { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .ov-frame { padding: 8px; }
  .ov-attention { grid-template-columns: 1fr; }
  .ov-peek { position: static; }
}
</style>
