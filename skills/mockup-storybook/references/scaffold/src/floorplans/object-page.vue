<script setup lang="ts">
import './floorplan.css'

// Regions: shell, header, facts, section-nav, sections, child-collections, history
// (rulebook/floorplans/object-page § Regions). `history` is tier 3: it sits behind a named disclosure.
withDefaults(defineProps<{ chrome?: boolean; historyOpen?: boolean }>(), { chrome: true, historyOpen: false })
</script>

<template>
  <div class="op fp-page" data-floorplan="object-page">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="op-work">
      <header class="fp-card op-header" data-region="header">
        <slot name="header"><span class="fp-ph">header</span></slot>
      </header>
      <dl class="fp-card op-facts" data-region="facts" aria-label="Key facts">
        <slot name="facts">
          <span v-for="n in 4" :key="n" class="fp-ph">fact {{ n }}</span>
        </slot>
      </dl>
      <nav class="op-secnav" data-region="section-nav" aria-label="Sections">
        <slot name="section-nav"><span class="fp-ph">section-nav</span></slot>
      </nav>
      <section class="fp-card op-sections" data-region="sections">
        <slot name="sections">
          <span v-for="n in 2" :key="n" class="fp-ph">sections · group {{ n }}</span>
        </slot>
      </section>
      <div class="op-colls" data-region="child-collections">
        <slot name="child-collections"><span class="fp-ph">child-collections</span></slot>
      </div>
      <details class="fp-card op-history" data-region="history" :open="historyOpen">
        <summary>History</summary>
        <slot name="history"><span class="fp-ph">history</span></slot>
      </details>
    </div>
  </div>
</template>

<style scoped>
.op-work { flex: 1; width: 100%; max-width: 1000px; margin: 0 auto; padding: var(--fp-gap); display: flex; flex-direction: column; gap: var(--fp-gap); }
.op-facts { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--fp-gap); margin: 0; }
.op-secnav { position: sticky; top: 0; z-index: 1; display: flex; gap: 4px; overflow-x: auto; background: var(--fp-bg); border-bottom: 1px solid var(--fp-border); }
.op-sections { display: grid; grid-template-columns: 1fr 1fr; gap: var(--fp-gap); }
.op-colls { min-height: 120px; }
.op-history summary { cursor: pointer; font-weight: 600; color: var(--fp-tier3); }

@media (max-width: 640px) {
  .op-work { padding: 8px; }
  .op-facts { grid-template-columns: 1fr 1fr; }
  .op-sections { grid-template-columns: 1fr; }
}
</style>
