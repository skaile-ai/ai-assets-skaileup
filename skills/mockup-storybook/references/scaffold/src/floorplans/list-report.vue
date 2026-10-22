<script setup lang="ts">
import './floorplan.css'

// Regions: shell, page-header, saved-views, overview-strip, filter-bar, results, bulk-bar, peek
// (rulebook/floorplans/list-report § Regions). All regions stack on wide; narrow turns the bulk bar and
// the peek into bottom bars and the overview strip into two columns.
withDefaults(defineProps<{ chrome?: boolean; bulk?: boolean; peek?: boolean }>(), {
  chrome: true,
  bulk: true,
  peek: false,
})
</script>

<template>
  <div class="lr fp-page" data-floorplan="list-report">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="lr-work">
      <header class="fp-card lr-header" data-region="page-header">
        <slot name="page-header"><span class="fp-ph">page-header</span></slot>
      </header>
      <nav class="lr-views" data-region="saved-views" aria-label="Saved views">
        <slot name="saved-views"><span class="fp-ph">saved-views</span></slot>
      </nav>
      <section class="fp-card lr-overview" data-region="overview-strip">
        <slot name="overview-strip">
          <span v-for="n in 4" :key="n" class="fp-ph">overview-strip tile {{ n }}</span>
        </slot>
      </section>
      <section class="fp-card lr-filters" data-region="filter-bar">
        <slot name="filter-bar"><span class="fp-ph">filter-bar</span></slot>
      </section>
      <section class="fp-card lr-results" data-region="results">
        <slot name="results"><span class="fp-ph">results</span></slot>
      </section>
      <div v-show="bulk" class="lr-bulk" data-region="bulk-bar" role="toolbar" aria-label="Bulk actions">
        <slot name="bulk-bar"><span class="fp-ph">bulk-bar</span></slot>
      </div>
    </div>
    <aside v-show="peek" class="fp-card lr-peek" data-region="peek">
      <slot name="peek"><span class="fp-ph">peek</span></slot>
    </aside>
  </div>
</template>

<style scoped>
.lr-work { flex: 1; width: 100%; max-width: 1120px; margin: 0 auto; padding: var(--fp-gap); display: flex; flex-direction: column; gap: var(--fp-gap); }
.lr-overview { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--fp-gap); }
.lr-views { border-bottom: 1px solid var(--fp-border); padding: 0 4px; overflow-x: auto; }
.lr-results { flex: 1; min-height: 240px; }
.lr-bulk { padding: var(--fp-gap); background: var(--ui-bg-inverted); border-radius: var(--fp-radius); }
.lr-bulk .fp-ph { color: var(--ui-bg); border-color: var(--ui-text-dimmed); }
.lr-peek { position: absolute; right: 24px; top: 230px; width: 260px; z-index: 3; box-shadow: 0 6px 20px var(--fp-border); }

@media (max-width: 640px) {
  .lr-work { padding: 8px; }
  .lr-overview { grid-template-columns: 1fr 1fr; }
  .lr-bulk { position: sticky; bottom: 8px; z-index: 2; }
  .lr-peek { position: sticky; left: 8px; right: 8px; top: auto; bottom: 8px; width: auto; margin: 0 8px 8px; z-index: 3; }
}
</style>
