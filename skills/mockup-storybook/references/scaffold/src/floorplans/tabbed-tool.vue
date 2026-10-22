<script setup lang="ts">
import './floorplan.css'

// Regions: shell, header, tablist, filter-row, content, detail-overlay, detail-more, filter-drawer
// (rulebook/floorplans/tabbed-tool § Regions). `detailOpen` / `filtersOpen` open the two overlays (right panel on
// wide, bottom sheet and full screen on narrow); `emptyFirst` is the empty-state-first variant: no filter row,
// the content region holds an empty state with "Open filters".
withDefaults(
  defineProps<{ chrome?: boolean; detailOpen?: boolean; filtersOpen?: boolean; emptyFirst?: boolean; tabs?: string[]; filtersApplied?: number }>(),
  { chrome: true, detailOpen: false, filtersOpen: false, emptyFirst: false, tabs: () => ['Projects', 'Tasks', 'Invoices'], filtersApplied: 0 },
)
const emit = defineEmits<{ 'open-filters': []; 'close-detail': []; 'close-filters': [] }>()
</script>

<template>
  <div
    class="tt fp-page"
    data-floorplan="tabbed-tool"
    :class="{ 'detail-open': detailOpen, 'filters-open': filtersOpen, 'empty-first': emptyFirst }"
  >
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="tt-col">
      <header class="fp-card tt-header" data-region="header">
        <slot name="header"><span class="fp-ph">header</span></slot>
      </header>
      <div class="tt-tabrow">
        <div class="tt-tabs" data-region="tablist" role="tablist">
          <slot name="tablist">
            <button v-for="(t, i) in tabs" :key="t" type="button" role="tab" :aria-selected="i === 0">{{ t }}</button>
          </slot>
        </div>
        <button class="fp-btn tt-fopen" type="button" @click="emit('open-filters')">Filters · {{ filtersApplied }}</button>
      </div>
      <div v-show="!emptyFirst" class="fp-card tt-filters" data-region="filter-row">
        <slot name="filter-row"><span class="fp-ph">filter-row</span></slot>
      </div>
      <main class="fp-card tt-content" data-region="content">
        <div v-if="emptyFirst" class="tt-empty">
          <p>Nothing shown yet. Choose what belongs here.</p>
          <button class="fp-btn primary" type="button" @click="emit('open-filters')">Open filters</button>
        </div>
        <slot v-else name="content"><span class="fp-ph">content</span></slot>
      </main>
    </div>

    <div v-if="detailOpen || filtersOpen" class="fp-scrim" />
    <aside class="fp-card tt-sheet tt-detail" data-region="detail-overlay" aria-label="Detail">
      <button class="fp-ibtn tt-x" type="button" aria-label="Close detail" @click="emit('close-detail')">×</button>
      <slot name="detail-overlay"><span class="fp-ph">detail-overlay</span></slot>
      <details class="tt-more">
        <summary>More details</summary>
        <div data-region="detail-more">
          <slot name="detail-more"><span class="fp-ph">detail-more</span></slot>
        </div>
      </details>
    </aside>
    <aside class="fp-card tt-sheet tt-fdrawer" data-region="filter-drawer" aria-label="Filters">
      <button class="fp-ibtn tt-x" type="button" aria-label="Close filters" @click="emit('close-filters')">×</button>
      <slot name="filter-drawer"><span class="fp-ph">filter-drawer</span></slot>
    </aside>
  </div>
</template>

<style scoped>
.tt { overflow: hidden; }
.tt-col { flex: 1; width: 100%; max-width: 880px; margin: 0 auto; padding: var(--fp-gap); }
.tt-tabrow { display: flex; align-items: flex-end; gap: var(--fp-gap); margin-top: var(--fp-gap); border-bottom: 1px solid var(--fp-border); }
.tt-tabs { display: flex; flex: 1; gap: 2px; }
.tt-tabs :deep(button) { padding: 8px 16px; border: 1px solid transparent; border-bottom: 0; border-radius: var(--fp-radius) var(--fp-radius) 0 0; color: var(--fp-muted); }
.tt-tabs :deep(button[aria-selected='true']) { background: var(--fp-surface); border-color: var(--fp-border); color: var(--fp-fg); font-weight: 600; margin-bottom: -1px; box-shadow: inset 0 2px 0 var(--fp-accent); }
.tt-fopen { display: none; margin-bottom: 6px; }
.empty-first .tt-fopen { display: inline-flex; }
.tt-filters { margin-top: var(--fp-gap); }
.tt-content { margin-top: var(--fp-gap); min-height: 240px; }
.tt-empty { text-align: center; padding: 48px 16px; color: var(--fp-muted); }
.tt-sheet { display: none; position: absolute; top: 0; right: 0; bottom: 0; width: min(440px, 100%); z-index: 6; border-radius: 0; border-width: 0 0 0 2px; border-left-color: var(--fp-accent); overflow: auto; }
.detail-open .tt-detail, .filters-open .tt-fdrawer { display: block; }
.tt-x { float: right; margin-bottom: 8px; }
.tt-more { margin-top: var(--fp-gap); color: var(--fp-tier3); }

@media (max-width: 959px) {
  .tt-tabs :deep(button) { padding: 8px 12px; }
}
@media (max-width: 640px) {
  .tt-col { padding: 8px; }
  .tt-fopen { display: inline-flex; }
  .tt-sheet { top: auto; left: 0; width: 100%; border-width: 2px 0 0 0; border-top-color: var(--fp-accent); }
  .tt-detail { top: 0; height: 100%; }
  .tt-fdrawer { height: 70vh; }
}
</style>
