<script setup lang="ts">
import { computed } from 'vue'
import type { NavEntry } from '../components/nav-types'
import NavLink from './NavLink.vue'
import './floorplan.css'

// Shell. Regions: sidebar, page-header, work-area (default slot), slideover, bottom-pill, palette
// (rulebook/floorplans/shell-sidebar § Regions). >= 992 px: expanded sidebar, docked slideover. 768-991 px: icon rail,
// overlay slideover. <= 767 px: the sidebar is a drawer (`drawer`), the bottom pill shows the pinned destinations,
// the slideover is a bottom sheet. `slideover` and `palette` open those overlays.
const props = withDefaults(
  defineProps<{ nav: NavEntry[]; current?: string; title?: string; brand?: string; drawer?: boolean; slideover?: boolean; palette?: boolean }>(),
  { title: 'Title', brand: 'App', drawer: false, slideover: false, palette: false },
)
const emit = defineEmits<{ toggle: []; menu: [] }>()

const groups = computed(() => {
  const out: { name: string; items: NavEntry[] }[] = []
  for (const e of props.nav) {
    const name = e.group ?? ''
    let g = out.find((x) => x.name === name)
    if (!g) out.push((g = { name, items: [] }))
    g.items.push(e)
  }
  return out
})
const pinned = computed(() => props.nav.filter((e) => e.pinned))
</script>

<template>
  <div class="ss fp-fill" data-floorplan="shell-sidebar" :class="{ 'drawer-open': drawer, 'slide-open': slideover }">
    <div v-if="drawer" class="fp-scrim ss-scrim" />
    <aside class="ss-sb" data-region="sidebar" aria-label="Primary">
      <slot name="sidebar">
        <div class="ss-brand"><span class="fp-ic">{{ brand.slice(0, 1) }}</span><b class="ss-t">{{ brand }}</b></div>
        <button class="fp-btn ss-find" type="button"><span class="ss-t">Search</span><kbd>⌘K</kbd></button>
        <nav class="ss-nav">
          <section v-for="g in groups" :key="g.name">
            <h2 v-if="g.name" class="ss-group">{{ g.name }}</h2>
            <NavLink v-for="e in g.items" :key="e.to" :entry="e" :current="current" :title="e.label">
              <span class="fp-ic">{{ e.label.slice(0, 1) }}</span><span class="ss-t">{{ e.label }}</span>
            </NavLink>
          </section>
        </nav>
      </slot>
    </aside>

    <div class="ss-panel">
      <header class="ss-hdr" data-region="page-header">
        <button class="fp-ibtn ss-toggle" type="button" aria-label="Menu" @click="emit('toggle')">☰</button>
        <h1 class="ss-title">{{ title }}</h1>
        <span class="fp-sp" />
        <slot name="page-header"><span class="fp-ph">page-header</span></slot>
      </header>
      <div class="ss-row">
        <main class="ss-work" data-region="work-area">
          <slot><span class="fp-ph">work-area</span></slot>
        </main>
        <aside v-show="slideover" class="ss-slide" data-region="slideover" aria-label="Quick view">
          <slot name="slideover"><span class="fp-ph">slideover</span></slot>
        </aside>
      </div>
    </div>

    <nav class="ss-pill" data-region="bottom-pill" aria-label="Pinned">
      <slot name="bottom-pill">
        <NavLink v-for="e in pinned" :key="e.to" :entry="e" :current="current" />
        <button class="fp-btn" type="button" @click="emit('menu')">Menu</button>
      </slot>
    </nav>

    <template v-if="palette">
      <div class="fp-scrim" />
    </template>
    <div v-show="palette" class="fp-card ss-palette" data-region="palette" role="dialog" aria-label="Command palette">
      <slot name="palette"><span class="fp-ph">palette</span></slot>
    </div>
  </div>
</template>

<style scoped>
[data-floorplan].ss { flex-direction: row; overflow: hidden; }
.ss-sb { flex: none; width: 240px; display: flex; flex-direction: column; gap: var(--fp-gap); padding: var(--fp-gap); background: var(--fp-surface); border-right: 1px solid var(--fp-border); overflow: auto; z-index: 30; }
.ss-brand { display: flex; align-items: center; gap: 10px; }
.ss-find { display: flex; justify-content: space-between; align-items: center; color: var(--fp-muted); }
.ss-nav { display: flex; flex-direction: column; gap: 4px; }
.ss-group { margin: 10px 8px 4px; font-size: 11px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: var(--fp-muted); }
.ss-panel { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.ss-hdr { flex: none; display: flex; align-items: center; gap: var(--fp-gap); padding: var(--fp-gap) 18px; background: var(--fp-surface); border-bottom: 1px solid var(--fp-border); }
.ss-hdr .fp-ph { width: auto; }
.ss-title { margin: 0; font-size: 18px; }
.ss-toggle { display: none; }
.ss-row { flex: 1; min-height: 0; display: flex; }
.ss-work { --fp-h: 100%; flex: 1; min-width: 0; min-height: 0; padding: 18px; overflow: auto; display: flex; flex-direction: column; }
.ss-slide { flex: none; width: 300px; padding: var(--fp-gap); background: var(--fp-surface); border-left: 1px solid var(--fp-border); z-index: 20; overflow: auto; }
.ss-pill { display: none; }
.ss-palette { position: absolute; top: 12vh; left: 50%; transform: translateX(-50%); width: min(520px, 92%); z-index: 40; }

@media (min-width: 768px) { .ss-scrim { display: none; } }
@media (max-width: 991px) {
  .ss-sb { width: 60px; align-items: center; padding: var(--fp-gap) 8px; }
  .ss-t, .ss-sb kbd, .ss-group { display: none; }
  .ss-slide { position: absolute; top: 0; right: 0; bottom: 0; box-shadow: 0 0 0 1px var(--fp-border); }
}
@media (max-width: 767px) {
  .ss-sb { position: absolute; top: 0; left: 0; bottom: 0; width: 260px; align-items: stretch; transform: translateX(-100%); transition: transform 0.15s; }
  .drawer-open .ss-sb { transform: none; }
  .drawer-open .ss-t, .drawer-open .ss-group { display: revert; }
  .drawer-open .ss-sb kbd { display: inline; }
  .ss-scrim { z-index: 25; }
  .ss-toggle { display: inline-flex; }
  .ss-work { padding: 12px 12px 84px; }
  .ss-slide { top: auto; left: 0; right: 0; width: auto; max-height: 55vh; border-left: 0; border-top: 1px solid var(--fp-border); }
  .ss-pill {
    display: flex; position: absolute; left: 50%; bottom: 12px; transform: translateX(-50%); z-index: 15; gap: 4px; padding: 4px 6px;
    background: var(--fp-surface); border: 1px solid var(--fp-border); border-radius: 99px; box-shadow: 0 2px 10px var(--fp-border);
  }
}
</style>
