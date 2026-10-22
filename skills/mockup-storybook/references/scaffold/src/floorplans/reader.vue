<script setup lang="ts">
import { ref } from 'vue'
import './floorplan.css'

// Regions: shell, filters, tree, list, reader, doc-info (rulebook/floorplans/reader § Regions).
// Wide: filters | tree over list | reader. 641-959 px: the reader is an overlay from the right (`readerOpen`).
// Narrow: one column; the filters collapse into a "Filters" disclosure; the reader is a full-width overlay.
withDefaults(defineProps<{ chrome?: boolean; readerOpen?: boolean; filtersApplied?: number }>(), {
  chrome: true,
  readerOpen: false,
  filtersApplied: 2,
})
const emit = defineEmits<{ close: [] }>()
const filtersOpen = ref(false)
</script>

<template>
  <div class="rd fp-page" data-floorplan="reader" :class="{ 'reader-open': readerOpen, 'filters-open': filtersOpen }">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="rd-work">
      <aside class="fp-card rd-filters" data-region="filters">
        <button class="fp-btn rd-ftoggle" type="button" :aria-expanded="filtersOpen" @click="filtersOpen = !filtersOpen">
          Filters · {{ filtersApplied }} applied
        </button>
        <div class="rd-fbody"><slot name="filters"><span class="fp-ph">filters</span></slot></div>
      </aside>
      <div class="rd-mid">
        <nav class="fp-card rd-tree" data-region="tree" aria-label="Hierarchy">
          <slot name="tree"><span class="fp-ph">tree</span></slot>
        </nav>
        <div class="fp-card rd-list" data-region="list">
          <slot name="list"><span class="fp-ph">list</span></slot>
        </div>
      </div>
      <article class="fp-card rd-reader" data-region="reader">
        <div class="rd-rhead">
          <details class="rd-info">
            <summary class="fp-btn">Document info</summary>
            <div class="rd-infobox" data-region="doc-info">
              <slot name="doc-info"><span class="fp-ph">doc-info</span></slot>
            </div>
          </details>
          <span class="fp-sp" />
          <button class="fp-ibtn rd-close" type="button" aria-label="Close reader" @click="emit('close')">×</button>
        </div>
        <slot name="reader"><span class="fp-ph">reader</span></slot>
      </article>
    </div>
  </div>
</template>

<style scoped>
.rd { overflow: hidden; }
.rd-work { flex: 1; display: grid; grid-template-columns: 210px 310px 1fr; gap: var(--fp-gap); padding: var(--fp-gap); min-height: 0; }
.rd-ftoggle { display: none; width: 100%; font-weight: 600; text-align: left; }
.rd-mid { display: flex; flex-direction: column; gap: var(--fp-gap); min-width: 0; }
.rd-tree { flex: none; min-height: 100px; }
.rd-list { flex: 1; min-height: 160px; }
.rd-reader { min-height: 320px; overflow: auto; }
.rd-rhead { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 8px; }
.rd-info { position: relative; }
.rd-info summary { display: inline-block; list-style: none; }
.rd-info summary::-webkit-details-marker { display: none; }
.rd-infobox { position: absolute; left: 0; top: 36px; z-index: 2; width: 250px; padding: 10px; background: var(--fp-surface); border: 1px solid var(--fp-border); border-radius: var(--fp-radius); color: var(--fp-tier3); }
.rd-close { display: none; }

@media (max-width: 959px) {
  .rd-work { grid-template-columns: 210px 1fr; }
  .rd-reader { display: none; position: absolute; top: 0; right: 0; bottom: 0; width: min(560px, 100%); z-index: 5; border-radius: 0; border-width: 0 0 0 2px; border-left-color: var(--fp-accent); }
  .reader-open .rd-reader { display: block; }
  .rd-close { display: inline-flex; }
}
@media (max-width: 640px) {
  .rd-work { grid-template-columns: 1fr; }
  .rd-ftoggle { display: block; }
  .rd-fbody { display: none; margin-top: 10px; }
  .filters-open .rd-fbody { display: block; }
  .rd-reader { width: 100%; border-left-width: 0; }
}
</style>
