<script setup lang="ts">
import './floorplan.css'

// Regions: shell, hub-tiles, area-head, area-body, peek, area-foot, walk-head, walk-step, walk-foot
// (rulebook/floorplans/hub-areas § Regions). Three phone frames: hub, area, walk.
// Wide shows all three side by side (they wrap two per row from 641 px); narrow shows only `frame`.
withDefaults(defineProps<{ chrome?: boolean; frame?: 'hub' | 'area' | 'walk'; peek?: boolean }>(), {
  chrome: true,
  frame: 'hub',
  peek: false,
})
</script>

<template>
  <div class="ha fp-page" data-floorplan="hub-areas" :data-frame="frame">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="ha-stage">
      <section class="ha-col ha-hub">
        <p class="ha-cap">Hub</p>
        <div class="ha-phone">
          <div class="ha-scroll" data-region="hub-tiles">
            <slot name="hub-tiles"><span class="fp-ph">hub-tiles</span></slot>
          </div>
        </div>
      </section>
      <section class="ha-col ha-area">
        <p class="ha-cap">Area</p>
        <div class="ha-phone">
          <div class="ha-head" data-region="area-head">
            <slot name="area-head"><span class="fp-ph">area-head</span></slot>
          </div>
          <div class="ha-scroll" data-region="area-body">
            <slot name="area-body"><span class="fp-ph">area-body</span></slot>
          </div>
          <div v-show="peek" class="ha-peek" data-region="peek">
            <slot name="peek"><span class="fp-ph">peek</span></slot>
          </div>
          <div class="ha-foot" data-region="area-foot">
            <slot name="area-foot"><span class="fp-ph">area-foot</span></slot>
          </div>
        </div>
      </section>
      <section class="ha-col ha-walk">
        <p class="ha-cap">Walk</p>
        <div class="ha-phone">
          <div class="ha-head" data-region="walk-head">
            <slot name="walk-head"><span class="fp-ph">walk-head</span></slot>
          </div>
          <div class="ha-scroll" data-region="walk-step">
            <slot name="walk-step"><span class="fp-ph">walk-step</span></slot>
          </div>
          <div class="ha-foot" data-region="walk-foot">
            <slot name="walk-foot"><span class="fp-ph">walk-foot</span></slot>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.ha-stage { flex: 1; display: flex; flex-wrap: wrap; justify-content: center; align-content: flex-start; gap: 24px; padding: 20px var(--fp-gap); }
.ha-col { width: 340px; max-width: 100%; }
.ha-cap { margin: 0 0 8px; font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase; color: var(--fp-muted); }
.ha-phone { display: flex; flex-direction: column; height: 580px; background: var(--fp-surface); border: 1px solid var(--fp-border); border-radius: 22px; overflow: hidden; }
.ha-head { flex: none; padding: 14px 16px; border-bottom: 1px solid var(--fp-border); background: var(--fp-surface); }
.ha-scroll { flex: 1; min-height: 0; overflow: auto; padding: 16px; }
.ha-peek { flex: none; margin: 0 16px 6px; padding: 10px 12px; background: var(--fp-surface); border: 1px solid var(--fp-border); border-radius: var(--fp-radius); color: var(--fp-tier3); }
.ha-foot { flex: none; padding: 12px 16px; border-top: 1px solid var(--fp-border); background: var(--fp-surface); }

@media (max-width: 640px) {
  .ha-stage { gap: 20px; padding: 12px; }
  .ha-col { width: 100%; }
  .ha-phone { height: auto; min-height: 540px; border-radius: var(--fp-radius); }
  .ha[data-frame='hub'] .ha-area, .ha[data-frame='hub'] .ha-walk,
  .ha[data-frame='area'] .ha-hub, .ha[data-frame='area'] .ha-walk,
  .ha[data-frame='walk'] .ha-hub, .ha[data-frame='walk'] .ha-area { display: none; }
}
</style>
