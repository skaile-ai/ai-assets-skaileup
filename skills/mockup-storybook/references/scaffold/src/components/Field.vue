<script setup lang="ts" generic="Row extends Record<string, unknown>, K extends keyof Row & string">
// One form field of an entity row: a Nuxt UI `UFormField` around the input that fits the
// field's semantic type. `name` is checked against the row type, so a field the data model
// does not have fails `vue-tsc` here instead of rendering an empty input.
import { computed } from 'vue'
import { useStore } from '../model/store'
import type { FieldType } from './field-types'

const props = defineProps<{
  name: K
  label?: string
  type?: FieldType
  required?: boolean
  help?: string
  hint?: string
  /** Enum values for `type="enum"`. */
  options?: readonly string[]
  /** For `type="m2o"`: the data key of the related entity (`user` for `User`). */
  relation?: string
  /** For `type="m2o"`: the related row's field shown as its label (default `id`). */
  labelField?: string
}>()

const row = defineModel<Row>('row', { required: true })
const store = useStore()

const type = computed<FieldType>(() => props.type ?? 'string')
const label = computed(() => props.label ?? props.name.replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase()))

// Every input reads and writes through one accessor: the row is replaced, never mutated.
const value = computed({
  get: () => row.value[props.name] as never,
  set: (next: unknown) => {
    row.value = { ...row.value, [props.name]: next }
  },
})

const items = computed(() => {
  if (type.value === 'enum') return (props.options ?? []).map((option) => ({ label: option, value: option }))
  if (type.value === 'm2o' && props.relation) {
    return store.rows(props.relation).map((related) => ({
      label: String(related[props.labelField ?? 'id'] ?? related.id),
      value: related.id,
    }))
  }
  return []
})

const inputType = computed(
  () =>
    ({ email: 'email', url: 'url', password: 'password', date: 'date', datetime: 'datetime-local', image: 'file', file: 'file' })[
      type.value as string
    ] ?? 'text',
)

const jsonText = computed({
  get: () => (typeof value.value === 'string' ? (value.value as string) : JSON.stringify(value.value ?? null, null, 2)),
  set: (text: string) => {
    try {
      value.value = JSON.parse(text) as never
    } catch {
      value.value = text as never
    }
  },
})
</script>

<template>
  <UFormField :name="name" :label="label" :required="required" :help="help" :hint="hint">
    <UTextarea v-if="type === 'text' || type === 'richtext'" v-model="value" class="w-full" />
    <UTextarea v-else-if="type === 'json'" v-model="jsonText" class="w-full font-mono" />
    <UInputNumber v-else-if="type === 'integer' || type === 'float' || type === 'decimal'" v-model="value" class="w-full" />
    <USwitch v-else-if="type === 'boolean'" v-model="value" />
    <USelect v-else-if="type === 'enum' || type === 'm2o'" v-model="value" :items="items" class="w-full" />
    <UInput v-else v-model="value" :type="inputType" class="w-full" />
  </UFormField>
</template>
