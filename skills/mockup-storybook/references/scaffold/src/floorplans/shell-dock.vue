<script setup lang="ts">
import type { NavEntry } from '../components/nav-types'
import NavLink from './NavLink.vue'
import './floorplan.css'

// Shell. Regions: title-bar, toolbar, nav-pane, list-pane (default slot), detail-pane, more-details, status-bar, palette
// (rulebook/floorplans/shell-dock § Regions). >= 992 px: three docked panes with splitters. 768-991 px: the panes keep
// their minimum widths. <= 767 px: one pane at a time, chosen with the Navigate · List · Detail control (`pane`).
withDefaults(
  defineProps<{ nav: NavEntry[]; current?: string; title?: string; brand?: string; palette?: boolean }>(),
  { title: 'Title', brand: 'App', palette: false },
)
const pane = defineModel<'nav' | 'list' | 'detail'>('pane', { default: 'list' })
const panes = [
  { id: 'nav', label: 'Navigate' },
  { id: 'list', label: 'List' },
  { id: 'detail', label: 'Detail' },
] as const
</script>

<template>
  <div class="dk fp-fill" data-floorplan="shell-dock" :data-pane="pane">
    <header class="dk-title" data-region="title-bar">
      <b>{{ brand }}</b>
      <span class="fp-sp dk-t">{{ title }}</span>
      <slot name="title-bar" />
    </header>
    <div class="dk-tool" data-region="toolbar">
      <slot name="toolbar"><span class="fp-ph">toolbar</span></slot>
    </div>
    <div class="dk-panesw">
      <div class="dk-seg" role="group" aria-label="Pane">
        <button v-for="p in panes" :key="p.id" type="button" :aria-pressed="pane === p.id" @click="pane = p.id">{{ p.label }}</button>
      </div>
    </div>
    <div class="dk-panes">
      <nav class="dk-pane dk-nav" data-region="nav-pane" aria-label="Primary">
        <NavLink v-for="e in nav" :key="e.to" :entry="e" :current="current" />
        <slot name="nav-pane"><span class="fp-ph">nav-pane</span></slot>
      </nav>
      <i class="dk-split" />
      <main class="dk-pane dk-list" data-region="list-pane">
        <slot><span class="fp-ph">list-pane</span></slot>
      </main>
      <i class="dk-split" />
      <aside class="dk-pane dk-detail" data-region="detail-pane" aria-label="Detail">
        <slot name="detail-pane"><span class="fp-ph">detail-pane</span></slot>
        <details class="dk-more" data-region="more-details">
          <summary>More details</summary>
          <slot name="more-details"><span class="fp-ph">more-details</span></slot>
        </details>
      </aside>
    </div>
    <footer class="dk-status" data-region="status-bar">
      <slot name="status-bar"><span class="fp-ph">status-bar</span></slot>
    </footer>
    <div v-if="palette" class="fp-scrim" />
    <div v-show="palette" class="fp-card dk-palette" data-region="palette" role="dialog" aria-label="Command palette">
      <slot name="palette"><span class="fp-ph">palette</span></slot>
    </div>
  </div>
</template>

<style scoped>
[data-floorplan].dk { display: grid; grid-template-rows: auto auto auto 1fr auto; font-size: 13px; overflow: hidden; }
.dk-title { display: flex; align-items: center; gap: 10px; height: 30px; padding: 0 10px; background: var(--fp-surface-2); border-bottom: 1px solid var(--fp-border); }
.dk-t { text-align: center; color: var(--fp-muted); }
.dk-tool { display: flex; align-items: center; gap: 6px; min-height: 36px; padding: 0 10px; background: var(--fp-surface); border-bottom: 1px solid var(--fp-border); }
.dk-tool .fp-ph { min-height: 24px; }
.dk-panesw { display: none; padding: 6px 10px; background: var(--fp-surface); border-bottom: 1px solid var(--fp-border); }
.dk-seg { display: flex; width: 100%; }
.dk-seg button { flex: 1; padding: 3px 10px; border: 1px solid var(--fp-border); background: var(--fp-surface); margin-left: -1px; }
.dk-seg button:first-child { margin-left: 0; border-radius: var(--fp-radius) 0 0 var(--fp-radius); }
.dk-seg button:last-child { border-radius: 0 var(--fp-radius) var(--fp-radius) 0; }
.dk-seg button[aria-pressed='true'] { background: var(--fp-surface-2); border-color: var(--fp-accent); }
.dk-panes { display: flex; min-height: 0; }
.dk-pane { overflow: auto; min-width: 0; background: var(--fp-surface); padding: 8px; }
.dk-nav { width: 240px; flex: none; display: flex; flex-direction: column; gap: 2px; background: var(--fp-bg); }
.dk-nav :deep(.fp-nav) { padding: 4px 8px; }
.dk-split { width: 5px; flex: none; background: var(--fp-border); cursor: col-resize; }
.dk-list { flex: 1; --fp-h: 100%; }
.dk-detail { width: 300px; flex: none; display: flex; flex-direction: column; gap: 8px; }
.dk-more { border-top: 1px dashed var(--fp-border); padding-top: 8px; color: var(--fp-tier3); }
.dk-status { display: flex; align-items: center; gap: 16px; min-height: 24px; padding: 0 10px; background: var(--fp-surface-2); border-top: 1px solid var(--fp-border); color: var(--fp-muted); font-size: 12px; }
.dk-status .fp-ph { border: 0; min-height: 0; padding: 0; }
.dk-palette { position: absolute; top: 12vh; left: 50%; transform: translateX(-50%); width: min(520px, 92%); z-index: 40; }

@media (max-width: 991px) {
  .dk-nav { width: 200px; }
  .dk-detail { width: 260px; }
}
@media (max-width: 767px) {
  .dk-split { display: none; }
  .dk-panesw { display: block; }
  .dk-nav, .dk-detail { display: none; width: auto; flex: 1; }
  [data-pane='nav'] .dk-nav, [data-pane='detail'] .dk-detail { display: flex; }
  [data-pane='nav'] .dk-list, [data-pane='detail'] .dk-list { display: none; }
}
</style>
