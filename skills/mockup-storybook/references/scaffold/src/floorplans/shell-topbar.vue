<script setup lang="ts">
import type { NavEntry } from '../components/nav-types'
import NavLink from './NavLink.vue'
import './floorplan.css'

// Shell. Regions: top-bar, destinations, page-header, work-area (default slot), peek, palette
// (rulebook/floorplans/shell-topbar § Regions). >= 960 px: destinations inline in the bar. Below: the bar folds to
// brand · menu · search · create and `menu` opens the destination panel under it; the peek is a bottom sheet.
withDefaults(
  defineProps<{ nav: NavEntry[]; current?: string; title?: string; brand?: string; menu?: boolean; peek?: boolean; palette?: boolean }>(),
  { title: 'Title', brand: 'App', menu: false, peek: false, palette: false },
)
const emit = defineEmits<{ 'toggle-menu': [] }>()
</script>

<template>
  <div class="tb fp-page" data-floorplan="shell-topbar" :class="{ 'menu-open': menu }">
    <header class="tb-top" data-region="top-bar">
      <b class="tb-brand"><span class="fp-ic">{{ brand.slice(0, 1) }}</span> {{ brand }}</b>
      <nav class="tb-dest" data-region="destinations" aria-label="Primary">
        <slot name="destinations">
          <NavLink v-for="e in nav" :key="e.to" :entry="e" :current="current" />
        </slot>
      </nav>
      <span class="fp-sp" />
      <slot name="top-bar"><span class="tb-find">Search <kbd>⌘K</kbd></span></slot>
      <button class="fp-ibtn tb-menu" type="button" aria-label="Menu" :aria-expanded="menu" @click="emit('toggle-menu')">☰</button>
    </header>
    <div class="tb-page">
      <div class="tb-hdr" data-region="page-header">
        <h1 class="tb-title">{{ title }}</h1>
        <span class="fp-sp" />
        <slot name="page-header"><span class="fp-ph">page-header</span></slot>
      </div>
      <main class="tb-work" data-region="work-area">
        <slot><span class="fp-ph">work-area</span></slot>
      </main>
    </div>
    <aside v-show="peek" class="fp-card tb-peek" data-region="peek" aria-label="Peek">
      <slot name="peek"><span class="fp-ph">peek</span></slot>
    </aside>
    <div v-if="palette" class="fp-scrim" />
    <div v-show="palette" class="fp-card tb-palette" data-region="palette" role="dialog" aria-label="Command palette">
      <slot name="palette"><span class="fp-ph">palette</span></slot>
    </div>
  </div>
</template>

<style scoped>
.tb-top { position: sticky; top: 0; z-index: 30; display: flex; align-items: center; gap: 10px; height: 56px; padding: 0 20px; background: var(--fp-surface); border-bottom: 1px solid var(--fp-border); }
.tb-brand { display: inline-flex; align-items: center; gap: 8px; }
.tb-dest { display: flex; align-self: stretch; }
.tb-dest :deep(.fp-nav) { border-radius: 0; padding: 0 10px; border-bottom: 2px solid transparent; color: var(--fp-muted); }
.tb-dest :deep(.fp-nav.is-current) { background: none; color: var(--fp-fg); border-bottom-color: var(--fp-accent); }
.tb-find { color: var(--fp-muted); display: inline-flex; gap: 8px; align-items: center; }
.tb-menu { display: none; }
.tb-page { flex: 1; width: 100%; max-width: 1080px; margin: 0 auto; padding: 0 20px 40px; }
.tb-hdr { display: flex; align-items: center; gap: var(--fp-gap); padding: 20px 0 12px; }
.tb-hdr .fp-ph { width: auto; }
.tb-title { margin: 0; font-size: 22px; }
.tb-work { --fp-h: calc(100vh - 56px); position: relative; min-height: 320px; }
.tb-peek { position: absolute; top: 140px; right: 150px; width: 270px; z-index: 10; border-color: var(--fp-accent); }
.tb-palette { position: absolute; top: 12vh; left: 50%; transform: translateX(-50%); width: min(520px, 92%); z-index: 40; }

@media (max-width: 959px) {
  .tb-menu { display: inline-flex; }
  .tb-dest { display: none; position: absolute; top: 100%; left: 0; right: 0; flex-direction: column; background: var(--fp-surface); border-bottom: 1px solid var(--fp-border); padding: 6px 12px 10px; }
  .menu-open .tb-dest { display: flex; }
  .tb-dest :deep(.fp-nav) { padding: 12px 8px; border-bottom: 1px solid var(--fp-surface-2); }
  .tb-dest :deep(.fp-nav.is-current) { border-left: 3px solid var(--fp-accent); padding-left: 10px; }
  .tb-peek { position: fixed; top: auto; left: 0; right: 0; bottom: 0; width: auto; border-radius: var(--fp-radius) var(--fp-radius) 0 0; }
}
@media (max-width: 640px) {
  .tb-page { padding: 0 0 40px; }
  .tb-hdr { padding: 16px 12px 8px; }
}
</style>
