<script setup lang="ts">
import { computed } from 'vue'
import type { NavEntry } from '../components/nav-types'
import NavLink from './NavLink.vue'
import './floorplan.css'

// Shell. Regions: top-bar, work-area (default slot), tab-bar, more-sheet, detail-sheet, palette
// (rulebook/floorplans/shell-mobile-tabs § Regions). One column of at most 480 px, centred on wide. The tab bar shows
// the first destinations (4 when the list is longer than 5) plus More; `more` opens the sheet with the rest,
// `detail` the read-only detail sheet, `palette` the full-screen search.
const props = withDefaults(
  defineProps<{ nav: NavEntry[]; current?: string; title?: string; more?: boolean; detail?: boolean; palette?: boolean }>(),
  { title: 'Title', more: false, detail: false, palette: false },
)
const emit = defineEmits<{ 'toggle-more': [] }>()
const tabs = computed(() => (props.nav.length > 5 ? props.nav.slice(0, 4) : props.nav))
const rest = computed(() => (props.nav.length > 5 ? props.nav.slice(4) : []))
</script>

<template>
  <div class="mt fp-fill" data-floorplan="shell-mobile-tabs">
    <div class="mt-device">
      <header class="mt-top" data-region="top-bar">
        <h1 class="mt-title">{{ title }}</h1>
        <span class="fp-sp" />
        <slot name="top-bar"><span class="fp-ph">top-bar</span></slot>
      </header>
      <main class="mt-work" data-region="work-area">
        <slot><span class="fp-ph">work-area</span></slot>
      </main>
      <aside v-show="detail && !more" class="mt-sheet" data-region="detail-sheet" aria-label="Details">
        <slot name="detail-sheet"><span class="fp-ph">detail-sheet</span></slot>
      </aside>
      <nav v-show="more" class="mt-sheet" data-region="more-sheet" aria-label="More destinations">
        <slot name="more-sheet">
          <NavLink v-for="e in rest" :key="e.to" :entry="e" :current="current" />
          <span v-if="!rest.length" class="fp-ph">more-sheet</span>
        </slot>
      </nav>
      <nav class="mt-tabs" data-region="tab-bar" aria-label="Primary">
        <slot name="tab-bar">
          <NavLink v-for="e in tabs" :key="e.to" :entry="e" :current="current" class="mt-tab">
            <span class="fp-ic">{{ e.label.slice(0, 1) }}</span>{{ e.label }}
          </NavLink>
          <button v-if="rest.length" class="mt-tab mt-tabbtn" type="button" @click="emit('toggle-more')">
            <span class="fp-ic">…</span>More
          </button>
        </slot>
      </nav>
      <div v-show="palette" class="mt-palette" data-region="palette" role="dialog" aria-label="Search and actions">
        <slot name="palette"><span class="fp-ph">palette</span></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mt { align-items: center; overflow: hidden; }
.mt-device { position: relative; width: 100%; max-width: 480px; height: 100%; display: flex; flex-direction: column; background: var(--fp-bg); border-left: 1px solid var(--fp-border); border-right: 1px solid var(--fp-border); overflow: hidden; }
.mt-top { flex: none; display: flex; align-items: center; gap: 8px; height: 56px; padding: 0 12px; background: var(--fp-surface); border-bottom: 1px solid var(--fp-border); }
.mt-top .fp-ph { width: auto; }
.mt-title { margin: 0; font-size: 18px; }
.mt-work { --fp-h: 100%; flex: 1; min-height: 0; overflow: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.mt-tabs { flex: none; display: flex; background: var(--fp-surface); border-top: 1px solid var(--fp-border); padding-bottom: env(safe-area-inset-bottom); }
.mt-tabs :deep(.fp-nav), .mt-tabbtn { flex: 1; flex-direction: column; justify-content: center; gap: 3px; min-height: 56px; padding: 8px 0 7px; font-size: 11px; color: var(--fp-muted); border: 0; border-radius: 0; background: none; }
.mt-tabs :deep(.fp-nav.is-current) { color: var(--fp-fg); background: none; }
.mt-tabbtn { display: flex; align-items: center; }
.mt-sheet { position: absolute; left: 0; right: 0; bottom: 56px; max-height: 60%; overflow: auto; padding: 26px 16px 16px; background: var(--fp-surface); border: 1px solid var(--fp-border); border-radius: 12px 12px 0 0; z-index: 20; }
.mt-sheet::after { content: ''; position: absolute; top: 8px; left: 50%; width: 36px; height: 4px; margin-left: -18px; border-radius: 2px; background: var(--fp-border); }
.mt-palette { position: absolute; inset: 0; z-index: 40; padding: var(--fp-gap); background: var(--fp-surface); overflow: auto; }

@media (max-width: 640px) {
  .mt-device { border: 0; }
}
</style>
