<script setup lang="ts">
import './floorplan.css'

// Regions: shell, header, mode-menu, tree, content, results, studio-drawer
// (rulebook/floorplans/mode-editor § Regions). Below 960 px the tree is an overlay from the left
// (`treeOpen`); the studio drawer is an overlay from the right, a bottom sheet on narrow (`studioOpen`).
withDefaults(defineProps<{ chrome?: boolean; treeOpen?: boolean; studioOpen?: boolean }>(), {
  chrome: true,
  treeOpen: false,
  studioOpen: false,
})
const emit = defineEmits<{ 'toggle-tree': [] }>()
</script>

<template>
  <div class="me fp-page" data-floorplan="mode-editor" :class="{ 'tree-open': treeOpen, 'studio-open': studioOpen }">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <header class="me-header" data-region="header">
      <button class="fp-ibtn me-toggle" type="button" aria-label="Outline" @click="emit('toggle-tree')">☰</button>
      <div class="me-title"><slot name="header"><span class="fp-ph">header</span></slot></div>
      <div class="me-modes" data-region="mode-menu" role="group" aria-label="Mode">
        <slot name="mode-menu"><span class="fp-ph">mode-menu</span></slot>
      </div>
    </header>
    <div class="me-body">
      <nav class="fp-card me-tree" data-region="tree" aria-label="Outline">
        <slot name="tree"><span class="fp-ph">tree</span></slot>
      </nav>
      <main class="fp-card me-content" data-region="content">
        <slot name="content"><span class="fp-ph">content</span></slot>
      </main>
      <aside class="fp-card me-results" data-region="results">
        <slot name="results"><span class="fp-ph">results</span></slot>
      </aside>
    </div>
    <aside class="fp-card me-drawer" data-region="studio-drawer">
      <slot name="studio-drawer"><span class="fp-ph">studio-drawer</span></slot>
    </aside>
  </div>
</template>

<style scoped>
.me { overflow: hidden; }
.me-header { flex: none; display: flex; align-items: center; gap: var(--fp-gap); flex-wrap: wrap; padding: 8px var(--fp-gap); background: var(--fp-surface); border-bottom: 1px solid var(--fp-border); }
.me-toggle { display: none; }
.me-title { flex: 1; min-width: 0; }
.me-body { flex: 1; display: grid; grid-template-columns: 230px 1fr 280px; gap: var(--fp-gap); padding: var(--fp-gap); min-height: 0; }
.me-content { min-height: 240px; }
.me-drawer { display: none; position: absolute; top: 0; right: 0; bottom: 0; width: 340px; z-index: 8; border-radius: 0; border-width: 0 0 0 2px; border-left-color: var(--fp-accent); overflow: auto; }
.studio-open .me-drawer { display: block; }

@media (max-width: 959px) {
  .me-toggle { display: inline-flex; }
  .me-body { grid-template-columns: 1fr; }
  .me-tree { display: none; position: absolute; top: 0; left: 0; bottom: 0; width: min(300px, 86vw); z-index: 7; border-radius: 0; border-width: 0 2px 0 0; border-right-color: var(--fp-accent); overflow: auto; }
  .tree-open .me-tree { display: block; }
}
@media (max-width: 640px) {
  .me-modes { order: 5; width: 100%; }
  .me-drawer { top: auto; left: 0; width: 100%; height: 75vh; border-width: 2px 0 0 0; border-top-color: var(--fp-accent); }
}
</style>
