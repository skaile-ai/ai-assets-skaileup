<script setup lang="ts">
// One feature's page, generated from its spec: never hand-edit what it shows, edit the spec.
import { computed } from 'vue'
import { linkTo } from '@storybook/addon-links'
import { featureBySpec } from './concept'

const props = defineProps<{ spec: string }>()
const feature = computed(() => featureBySpec(props.spec))
const framing = computed(() =>
  (feature.value?.framing ?? '').split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean),
)
const roles = computed(() => Object.entries(feature.value?.permissions ?? {}))
</script>

<template>
  <p v-if="!feature">No feature spec <code>{{ spec }}</code> in the concept index.</p>
  <article v-else class="flex max-w-3xl flex-col gap-6">
    <header class="flex flex-col gap-2">
      <p class="text-sm text-muted">{{ feature.featureset }}</p>
      <div class="flex items-center gap-3">
        <h1 class="text-2xl font-semibold">{{ feature.slug }}</h1>
        <UBadge v-if="feature.priority" variant="subtle">{{ feature.priority }}</UBadge>
      </div>
      <p v-if="feature.outcome" class="text-lg">{{ feature.outcome }}</p>
    </header>

    <section v-if="framing.length" class="flex flex-col gap-2">
      <h2 class="text-lg font-semibold">Why</h2>
      <p v-for="(p, i) in framing" :key="i">{{ p }}</p>
    </section>

    <section v-if="feature.featuresetPurpose" class="flex flex-col gap-2">
      <h2 class="text-lg font-semibold">Featureset</h2>
      <p>{{ feature.featuresetPurpose }}</p>
    </section>

    <section v-if="roles.length" class="flex flex-col gap-2">
      <h2 class="text-lg font-semibold">Who may do what</h2>
      <table class="text-left text-sm">
        <tbody>
          <tr v-for="[role, actions] in roles" :key="role" class="border-b border-default">
            <th class="py-1 pr-4 font-medium">{{ role }}</th>
            <td class="py-1">{{ actions.join(', ') }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-if="feature.scope.length" class="flex flex-col gap-2">
      <h2 class="text-lg font-semibold">Scope</h2>
      <ul class="list-disc pl-5">
        <li v-for="(line, i) in feature.scope" :key="i">{{ line }}</li>
      </ul>
    </section>

    <section v-if="feature.criteria.length" class="flex flex-col gap-2">
      <h2 class="text-lg font-semibold">Acceptance criteria</h2>
      <ul class="flex flex-col gap-2">
        <li v-for="c in feature.criteria" :key="c.id">
          <code>{{ c.id }}</code> {{ c.label }}
          <p v-if="c.ears" class="text-sm text-muted">{{ c.ears }}</p>
        </li>
      </ul>
    </section>

    <section v-if="feature.screens.length" class="flex flex-col gap-2">
      <h2 class="text-lg font-semibold">Screens</h2>
      <ul class="list-disc pl-5">
        <li v-for="s in feature.screens" :key="s.id">
          <a v-if="s.story" href="#" class="text-primary underline" @click.prevent="linkTo(s.story.title, s.story.name)()">{{ s.id }}</a>
          <template v-else>{{ s.id }} <span class="text-muted">no story yet</span></template>
          <span v-if="s.title" class="text-muted"> — {{ s.title }}</span>
        </li>
      </ul>
    </section>

    <section v-if="feature.journeys.length" class="flex flex-col gap-2">
      <h2 class="text-lg font-semibold">Journeys</h2>
      <ul class="list-disc pl-5">
        <li v-for="j in feature.journeys" :key="j.id">
          <a v-if="j.story" href="#" class="text-primary underline" @click.prevent="linkTo(j.story.title, j.story.name)()">{{ j.id }}</a>
          <template v-else>{{ j.id }} <span class="text-muted">no story yet</span></template>
          <span v-if="j.title || j.stage" class="text-muted"> — {{ [j.title, j.stage].filter(Boolean).join(', ') }}</span>
        </li>
      </ul>
    </section>

    <footer class="text-sm text-muted">Generated from _concept/{{ spec }}. Change the spec, not this page.</footer>
  </article>
</template>
