<script setup lang="ts">
import { computed } from 'vue'
import './floorplan.css'

// Regions: shell, step-list, step-body, step-help, footer (rulebook/floorplans/wizard § Regions).
// Wide: step list at the left, body in the centre, help at the right, footer under the body.
// Narrow: the step list folds into "Step n of m · Name" with a progress bar, help moves under the body,
// the footer sticks to the bottom edge. `steps` and `current` (0-based) feed the default step list.
const props = withDefaults(defineProps<{ chrome?: boolean; steps?: string[]; current?: number }>(), {
  chrome: true,
  steps: () => ['Basics', 'Team', 'Review'],
  current: 0,
})
const progress = computed(() => `${((props.current + 1) / props.steps.length) * 100}%`)
</script>

<template>
  <div class="wz fp-page" data-floorplan="wizard">
    <div v-if="chrome" class="fp-shell" data-region="shell">
      <slot name="shell"><span class="fp-ph">shell</span></slot>
    </div>
    <div class="wz-frame">
      <div class="wz-layout">
        <nav class="fp-card wz-steplist" data-region="step-list" aria-label="Steps">
          <slot name="step-list">
            <ol class="wz-steps">
              <li v-for="(s, i) in steps" :key="s" :aria-current="i === current ? 'step' : undefined" :data-state="i < current ? 'done' : i === current ? 'current' : 'todo'">
                <span class="wz-n">{{ i + 1 }}</span>{{ s }}
              </li>
            </ol>
            <div class="wz-stepline">
              Step {{ current + 1 }} of {{ steps.length }} · {{ steps[current] }}
              <div class="wz-bar"><i :style="{ width: progress }" /></div>
            </div>
          </slot>
        </nav>
        <section class="fp-card wz-body" data-region="step-body">
          <slot name="step-body"><span class="fp-ph">step-body</span></slot>
        </section>
        <aside class="fp-card wz-help" data-region="step-help">
          <slot name="step-help"><span class="fp-ph">step-help</span></slot>
        </aside>
        <div class="fp-card wz-footer" data-region="footer">
          <slot name="footer">
            <div class="wz-footrow">
              <button class="fp-btn" type="button">Back</button>
              <span class="fp-sp" />
              <button class="fp-btn" type="button">Cancel</button>
              <button class="fp-btn primary" type="button">Next</button>
            </div>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wz-frame { flex: 1; width: 100%; max-width: 1040px; margin: 0 auto; padding: var(--fp-gap); }
.wz-layout {
  display: grid; grid-template-columns: 200px minmax(0, 1fr) 220px;
  grid-template-areas: 'list body help' 'list foot help'; grid-template-rows: 1fr auto; gap: var(--fp-gap); align-items: start;
}
.wz-steplist { grid-area: list; }
.wz-body { grid-area: body; min-height: 340px; align-self: stretch; }
.wz-help { grid-area: help; background: var(--fp-surface-2); color: var(--fp-muted); }
.wz-footer { grid-area: foot; }
.wz-steps { list-style: none; margin: 0; padding: 0; }
.wz-steps li { display: flex; align-items: center; gap: 10px; padding: 10px 8px; color: var(--fp-muted); }
.wz-steps li[aria-current='step'] { color: var(--fp-fg); font-weight: 600; }
.wz-n { display: inline-grid; place-items: center; width: 24px; height: 24px; border: 1px solid var(--fp-border); border-radius: 99px; font-size: 12px; background: var(--fp-surface); }
[aria-current='step'] .wz-n, [data-state='done'] .wz-n { border-color: var(--fp-accent); color: var(--fp-accent); }
.wz-stepline { display: none; }
.wz-footrow { display: flex; align-items: center; gap: 8px; }

@media (max-width: 960px) {
  .wz-layout { grid-template-columns: 180px minmax(0, 1fr); grid-template-areas: 'list body' 'list help' 'list foot'; grid-template-rows: none; }
}
@media (max-width: 640px) {
  .wz-frame { padding: 8px; }
  .wz-layout { grid-template-columns: 1fr; grid-template-areas: 'list' 'body' 'help' 'foot'; gap: 8px; }
  .wz-steps { display: none; }
  .wz-stepline { display: block; font-weight: 600; }
  .wz-bar { height: 6px; margin-top: 8px; background: var(--fp-surface-2); border-radius: 99px; overflow: hidden; }
  .wz-bar i { display: block; height: 100%; background: var(--fp-accent); }
  .wz-body { min-height: 0; }
  .wz-footer { position: sticky; bottom: 0; z-index: 2; }
  .wz-footrow { flex-wrap: wrap; }
  .wz-footrow .primary { order: -1; flex-basis: 100%; }
  .wz-footrow .fp-sp { display: none; }
}
</style>
