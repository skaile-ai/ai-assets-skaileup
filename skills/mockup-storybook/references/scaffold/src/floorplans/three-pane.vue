<script setup lang="ts">
import './floorplan.css'

// Regions: shell, source-rail, editor-toolbar, work-area, management-drawer, status-line
// (rulebook/floorplans/three-pane § Regions). Wide: rail | work area | drawer; `rail="collapsed"` shrinks the rail
// to a 52 px strip and `drawer=false` closes the drawer. Narrow: the work area alone; `overlay` opens the rail
// from the left or the drawer as a bottom sheet.
withDefaults(
  defineProps<{
    chrome?: boolean
    rail?: 'expanded' | 'collapsed'
    drawer?: boolean
    overlay?: 'rail' | 'drawer' | null
  }>(),
  { chrome: true, rail: 'expanded', drawer: true, overlay: null },
)
</script>

<template>
  <div
    class="tp fp-fill"
    data-floorplan="three-pane"
    :class="{ 'rail-off': rail === 'collapsed', 'drawer-off': !drawer, 'ov-rail': overlay === 'rail', 'ov-drawer': overlay === 'drawer' }"
  >
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="tp-panes">
      <nav class="fp-card tp-rail" data-region="source-rail" aria-label="Sources">
        <slot name="source-rail"><span class="fp-ph">source-rail</span></slot>
      </nav>
      <div class="tp-mid">
        <section class="fp-card tp-toolbar" data-region="editor-toolbar">
          <slot name="editor-toolbar"><span class="fp-ph">editor-toolbar</span></slot>
        </section>
        <section class="fp-card tp-work" data-region="work-area">
          <slot name="work-area"><span class="fp-ph">work-area</span></slot>
        </section>
        <div class="tp-status" data-region="status-line">
          <slot name="status-line"><span class="fp-ph">status-line</span></slot>
        </div>
      </div>
      <aside class="fp-card tp-drawer" data-region="management-drawer">
        <slot name="management-drawer"><span class="fp-ph">management-drawer</span></slot>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.tp { overflow: hidden; }
.tp-panes { flex: 1; min-height: 0; display: grid; grid-template-columns: 230px 1fr 300px; gap: var(--fp-gap); padding: var(--fp-gap); }
.tp-rail, .tp-drawer { min-height: 0; overflow: auto; }
.tp-mid { min-height: 0; min-width: 0; display: flex; flex-direction: column; gap: var(--fp-gap); }
.tp-toolbar { flex: none; }
.tp-work { flex: 1; min-height: 0; overflow: auto; }
.tp-status { flex: none; min-height: 26px; padding: 0 var(--fp-gap); display: flex; align-items: center; background: var(--fp-surface-2); border: 1px solid var(--fp-border); border-radius: var(--fp-radius); color: var(--fp-muted); font-size: 12px; }
.tp-status :deep(.fp-ph) { border: 0; min-height: 0; padding: 0; }

@media (min-width: 641px) {
  .rail-off .tp-panes { grid-template-columns: 52px 1fr 300px; }
  .drawer-off .tp-panes { grid-template-columns: 230px 1fr; }
  .drawer-off.rail-off .tp-panes { grid-template-columns: 52px 1fr; }
  .drawer-off .tp-drawer { display: none; }
}
@media (max-width: 640px) {
  [data-floorplan].tp { height: auto; min-height: var(--fp-h, 100vh); }
  .tp-panes { display: block; }
  .tp-mid { min-height: 60vh; }
  .tp-rail, .tp-drawer { display: none; position: absolute; z-index: 5; box-shadow: 0 8px 24px var(--fp-border); }
  .tp-rail { top: 36px; left: 0; bottom: 0; width: 80%; border-radius: 0; }
  .tp-drawer { left: 0; right: 0; bottom: 0; max-height: 70vh; border-radius: var(--fp-radius) var(--fp-radius) 0 0; }
  .ov-rail .tp-rail, .ov-drawer .tp-drawer { display: block; }
  .tp-status { position: sticky; bottom: 8px; margin-top: var(--fp-gap); }
}
</style>
