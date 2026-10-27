// skaile-model 1.0.0
// Generator: runs model.ts and seed.ts, writes model.json, model.dbml and seed.json beside them.
//   npx tsx gen.ts [datamodel-dir]      (default: the directory of this file)
// Copied by architecture-datamodel; never hand-edited. Exit 1 with `file: $.path: message` lines on any violation.
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { basename, dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { snake, type AnyEntity, type Model, type Seed, type SharedEnum, type Target } from './skaile-model'

type Json = null | boolean | number | string | Json[] | { [k: string]: Json }
type Obj = Record<string, any>
const errors: string[] = []
const fail = (file: string, path: string, msg: string) => errors.push(`${file}: ${path}: ${msg}`)
const here = process.argv[2] ? resolve(process.argv[2]) : dirname(resolve(process.argv[1]))
const MODEL_JSON = 'model.json'
const SEED_JSON = 'seed.json'

// ── minimal JSON Schema 2020-12 validator: only the keywords the two schemas use ─────────────────────
const ANNOTATIONS = new Set(['$schema', '$id', '$comment', '$defs', 'title', 'description', 'examples', 'default'])
const KEYWORDS = new Set([
  'type', 'enum', 'const', 'pattern', 'minimum', 'required', 'properties', 'additionalProperties',
  'items', 'propertyNames', '$ref',
])
const isObj = (v: unknown): v is Obj => typeof v === 'object' && v !== null && !Array.isArray(v)
const typeOk = (t: string, v: unknown) =>
  t === 'object' ? isObj(v) : t === 'array' ? Array.isArray(v) : t === 'null' ? v === null
    : t === 'integer' ? Number.isInteger(v) : t === 'number' ? typeof v === 'number' && Number.isFinite(v) : typeof v === t

function validate(root: Obj, schema: Obj | boolean, value: unknown, path: string, sp: string, out: string[]): void {
  if (typeof schema === 'boolean') {
    if (!schema) out.push(`${path}: not allowed (schema ${sp})`)
    return
  }
  for (const k of Object.keys(schema)) {
    if (!KEYWORDS.has(k) && !ANNOTATIONS.has(k) && !k.startsWith('x-')) {
      throw new Error(`gen.ts does not implement schema keyword "${k}" (schema ${sp}); update gen.ts before using it`)
    }
  }
  if (schema.$ref !== undefined) {
    if (typeof schema.$ref !== 'string' || !schema.$ref.startsWith('#/')) throw new Error(`unsupported $ref ${schema.$ref} (schema ${sp})`)
    const target = schema.$ref.slice(2).split('/').reduce<any>((n, seg) => n?.[seg], root)
    if (target === undefined) throw new Error(`unresolved $ref ${schema.$ref} (schema ${sp})`)
    validate(root, target, value, path, `${sp.split('#')[0]}${schema.$ref}`, out)
  }
  if (schema.type !== undefined) {
    const types: string[] = Array.isArray(schema.type) ? schema.type : [schema.type]
    if (!types.some((t) => typeOk(t, value))) return void out.push(`${path}: expected ${types.join(' | ')} (schema ${sp}/type)`)
  }
  if (schema.const !== undefined && JSON.stringify(schema.const) !== JSON.stringify(value)) {
    out.push(`${path}: must be ${JSON.stringify(schema.const)} (schema ${sp}/const)`)
  }
  if (schema.enum !== undefined && !schema.enum.some((e: unknown) => JSON.stringify(e) === JSON.stringify(value))) {
    out.push(`${path}: must be one of ${schema.enum.map((e: unknown) => JSON.stringify(e)).join(', ')} (schema ${sp}/enum)`)
  }
  if (typeof value === 'string' && schema.pattern !== undefined && !new RegExp(schema.pattern, 'u').test(value)) {
    out.push(`${path}: "${value}" does not match ${schema.pattern} (schema ${sp}/pattern)`)
  }
  if (typeof value === 'number' && schema.minimum !== undefined && value < schema.minimum) {
    out.push(`${path}: ${value} is below the minimum ${schema.minimum} (schema ${sp}/minimum)`)
  }
  if (Array.isArray(value) && schema.items !== undefined) {
    value.forEach((item, i) => validate(root, schema.items, item, `${path}[${i}]`, `${sp}/items`, out))
  }
  if (isObj(value)) {
    for (const key of schema.required ?? []) {
      if (!(key in value)) out.push(`${path}: missing required "${key}" (schema ${sp}/required)`)
    }
    const props: Obj = schema.properties ?? {}
    for (const [key, v] of Object.entries(value)) {
      const at = `${path}.${key}`
      if (schema.propertyNames !== undefined) {
        const keyErrors: string[] = []
        validate(root, schema.propertyNames, key, at, `${sp}/propertyNames`, keyErrors)
        out.push(...keyErrors)
      }
      if (key in props) validate(root, props[key], v, at, `${sp}/properties/${key}`, out)
      else if (schema.additionalProperties !== undefined) validate(root, schema.additionalProperties, v, at, `${sp}/additionalProperties`, out)
    }
  }
}

function checkSchema(file: string, schemaFile: string, value: unknown): void {
  const schemaPath = join(here, schemaFile)
  if (!existsSync(schemaPath)) return fail(file, '$', `schema ${schemaFile} is missing next to gen.ts; copy it from the collection's tree/10_blueprint/datamodel/`)
  const root = JSON.parse(readFileSync(schemaPath, 'utf8'))
  const out: string[] = []
  validate(root, root, value, '$', `${schemaFile}#`, out)
  out.forEach((m) => errors.push(`${file}: ${m}`))
}

// ── model.ts → model.json ───────────────────────────────────────────────────────────────────────────
const pascal = (glossary: string) => glossary.split('-').map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join('')
const withProposal = (o: Obj, p?: { by: string; on: string; source: string }): Obj =>
  p ? { ...o, status: 'proposed', proposed_by: p.by, proposed_on: p.on, source: p.source } : o
const FIELD_KEYS = ['required', 'unique', 'primary', 'readonly', 'indexed', 'max_length', 'default', 'placeholder', 'faker'] as const
const DEFAULT_STANDARD = ['id', 'created_at', 'updated_at']

interface Built { json: Obj; dbml: string; index: Map<string, Obj> }

function buildModel(model: Model, file: string): Built {
  const entities = Object.entries(model.entities) as [string, AnyEntity][]
  const ids = new Map<AnyEntity, string>(entities.map(([id, e]) => [e, id]))
  const enumIds = new Map<SharedEnum, string>(Object.entries(model.enums).map(([id, e]) => [e, id]))
  const resolveTarget = (t: Target, at: string): string | undefined => {
    const id = typeof t === 'string' ? t : ids.get(t())
    if (id === undefined || !(id in model.entities)) fail(file, at, `relation target ${typeof t === 'string' ? `"${t}"` : ''} is not an entity listed in defineModel`)
    else return id
  }
  const jsonEntities: Obj[] = []
  const relationships: Obj[] = []
  const referencedEnums = new Set<string>()
  const index = new Map<string, Obj>()

  for (const [id, ent] of entities) {
    const at = `$.entities.${id}`
    const s = ent.spec
    if (!/^[A-Z][A-Za-z0-9]*$/.test(id)) fail(file, at, 'entity id must be PascalCase')
    if (pascal(s.glossary) !== id) fail(file, `${at}.glossary`, `"${s.glossary}" is ${pascal(s.glossary)} in PascalCase, but the entity id is ${id}`)
    const fieldNames = Object.keys(s.fields)
    for (const key of ['label_field', 'key_field'] as const) {
      if (s[key] !== undefined && !fieldNames.includes(s[key])) fail(file, `${at}.${key}`, `"${s[key]}" names no field of ${id}`)
    }
    const prefix = snake(id)
    const fields: Obj[] = []
    for (const [name, d] of Object.entries(s.fields) as [string, any][]) {
      const fat = `${at}.fields.${name}`
      if (d.kind === 'm2m') {
        const to = resolveTarget(d.target, `${fat}.target`)
        const through = resolveTarget(d.opts.through, `${fat}.through`)
        if (to && through) {
          const junction = Object.values(model.entities[through].spec.fields) as any[]
          const reaches = (side: string) => junction.some((jf) => jf.kind === 'm2o' && resolveTarget(jf.target, fat) === side)
          if (!reaches(id) || !reaches(to)) fail(file, `${fat}.through`, `junction ${through} needs an m2o to both ${id} and ${to}`)
          relationships.push({
            id: `${prefix}_${name}`, from: id, from_field: name, to, type: 'm2m',
            ...(d.opts.label !== undefined && { label: d.opts.label }),
            ...(d.opts.inverse !== undefined && { inverse_label: d.opts.inverse }),
          })
        }
        continue
      }
      const type = d.kind === 'scalar' ? d.type : d.kind === 'm2o' ? 'relation' : 'enum'
      const opts: Obj = d.kind === 'm2o' && d.opts.indexed === undefined ? { ...d.opts, indexed: true } : d.opts
      const o: Obj = { id: `${prefix}_${name}`, name, type }
      for (const key of FIELD_KEYS) {
        if (opts[key] !== undefined) o[key] = opts[key]
      }
      if (d.kind === 'enum') o.values = d.values
      else if (d.kind === 'enumRef') {
        const eid = enumIds.get(d.enum)
        if (eid === undefined) fail(file, `${fat}.enum`, 'shared enum is not listed in defineModel({ enums })')
        else {
          o.enum_id = eid
          referencedEnums.add(eid)
        }
      } else if (d.kind === 'm2o') {
        if (!name.endsWith('_id')) fail(file, fat, 'an m2o field name must end in _id')
        const to = resolveTarget(d.target, `${fat}.target`)
        if (to) {
          o.relation_target = to
          relationships.push({
            id: `${prefix}_${name.replace(/_id$/, '')}`, from: id, from_field: name, to, type: 'm2o',
            ...(d.opts.label !== undefined && { label: d.opts.label }),
            ...(d.opts.inverse !== undefined && { inverse_label: d.opts.inverse }),
            ...(d.opts.required === false && { required: false }),
            ...(d.opts.on_delete !== undefined && { on_delete: d.opts.on_delete }),
          })
        }
      }
      if (d.opts.description !== undefined) o.description = d.opts.description
      fields.push(withProposal(o, d.opts.proposed))
    }
    const ordered = withProposal({ id, glossary_id: s.glossary }, s.proposed)
    const entityJson: Obj = {
      ...ordered,
      display_name: s.display,
      ...(s.icon !== undefined && { icon: s.icon }),
      ...(s.color !== undefined && { color: s.color }),
      ...(s.position !== undefined && { position: s.position }),
      ...(s.from_features !== undefined && { from_features: s.from_features }),
      ...(s.label_field !== undefined && { label_field: s.label_field }),
      ...(s.key_field !== undefined && { key_field: s.key_field }),
      standard_fields: s.standard_fields ?? DEFAULT_STANDARD,
      fields,
    }
    jsonEntities.push(entityJson)
    index.set(id, entityJson)
  }
  for (const eid of Object.keys(model.enums)) {
    if (!referencedEnums.has(eid)) fail(file, `$.enums.${eid}`, 'shared enum is referenced by no field')
  }
  const json: Obj = { version: '1.0', entities: jsonEntities, relationships }
  if (enumIds.size) {
    json.enums = [...enumIds.values()].map((eid) => ({
      id: eid,
      values: Object.entries(model.enums[eid].values).map(([value, label]) => ({ value, label })),
    }))
  }
  return { json, dbml: '', index }
}

// ── model.json → model.dbml ─────────────────────────────────────────────────────────────────────────
const note = (s: string) => `'${s.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}'`
const dbmlDefault = (v: unknown) => (typeof v === 'string' ? note(v) : JSON.stringify(v))
const DELETE: Record<string, string> = { cascade: 'cascade', set_null: 'set null', restrict: 'restrict' }

function renderDbml(m: Obj): string {
  const proposed = (x: Obj) => x.status === 'proposed'
  const confirmed = new Set<string>(m.entities.filter((e: Obj) => !proposed(e)).map((e: Obj) => e.id))
  const lines = ['// Generated by gen.ts from model.ts. Do not edit by hand.']
  const skipped = m.entities.flatMap((e: Obj) =>
    proposed(e) ? [e.id] : e.fields.filter(proposed).map((x: Obj) => `${e.id}.${x.name}`))
  if (skipped.length) lines.push(`// Proposed, not confirmed, so not rendered: ${skipped.join(', ')}`)
  const block = (head: string, body: string[]) => [head, ...body, '}'].join('\n')
  const enumBody = (values: [string, string][]) => values.map(([v, d]) => `  ${v} [note: ${note(d)}]`)
  const enums: string[] = []
  for (const e of m.enums ?? []) {
    enums.push(block(`Enum ${e.id} {`, enumBody(e.values.map((v: Obj) => [v.value, v.label]))))
  }
  for (const e of m.entities.filter((x: Obj) => confirmed.has(x.id))) {
    for (const x of e.fields.filter((fl: Obj) => fl.type === 'enum' && !fl.enum_id && !proposed(fl))) {
      enums.push(block(`Enum ${x.id} {`, enumBody(Object.entries<string>(x.values))))
    }
  }
  const tables: string[] = []
  for (const e of m.entities.filter((x: Obj) => confirmed.has(x.id))) {
    const std: string[] = e.standard_fields
    const body: string[] = std.includes('id') ? ['  id uuid [pk]'] : []
    for (const x of e.fields.filter((fl: Obj) => !proposed(fl))) {
      const type = x.type === 'enum' ? (x.enum_id ?? x.id) : x.type === 'relation' ? 'uuid' : x.type
      const settings = [
        ...(x.primary ? ['pk'] : []),
        ...(x.required === false ? ['null'] : ['not null']),
        ...(x.unique ? ['unique'] : []),
        ...(x.default !== undefined ? [`default: ${dbmlDefault(x.default)}`] : []),
        ...(x.description !== undefined ? [`note: ${note(x.description)}`] : []),
      ]
      body.push(`  ${x.name} ${type} [${settings.join(', ')}]`)
    }
    for (const ts of ['created_at', 'updated_at']) if (std.includes(ts)) body.push(`  ${ts} datetime [not null]`)
    tables.push(block(`Table ${e.id} {`, body))
  }
  const refs = m.relationships
    .filter((r: Obj) => r.type === 'm2o' && confirmed.has(r.from) && confirmed.has(r.to)
      && !proposed(m.entities.find((e: Obj) => e.id === r.from).fields.find((x: Obj) => x.name === r.from_field)))
    .map((r: Obj) => `Ref: ${r.from}.${r.from_field} > ${r.to}.id${r.on_delete ? ` [delete: ${DELETE[r.on_delete]}]` : ''}`)
  return [lines.join('\n'), ...enums, ...tables, refs.join('\n')].filter(Boolean).join('\n\n') + '\n'
}

// ── seed.ts → seed.json ─────────────────────────────────────────────────────────────────────────────
const VALUE_TYPE: Record<string, string> = { integer: 'number', float: 'number', decimal: 'number', boolean: 'boolean', json: '' }

function checkSeed(seed: Seed, built: Built, file: string): void {
  const byKey = new Map<string, Obj>([...built.index].map(([id, e]) => [snake(id), e]))
  for (const [name, sc] of Object.entries(seed.scenarios)) {
    const ids = new Map<string, Set<string>>()
    const data = (sc.data ?? {}) as Record<string, Obj[]>
    for (const [key, rows] of Object.entries(data)) ids.set(key, new Set(rows.map((r) => r?.id)))
    for (const [key, rows] of Object.entries(data)) {
      const at = `$.scenarios.${name}.data.${key}`
      const ent = byKey.get(key)
      if (!ent) { fail(file, at, `no entity has the key "${key}" (entity keys are the snake_case of the entity id)`); continue }
      const declared = new Map<string, Obj>(ent.fields.map((x: Obj) => [x.name, x]))
      const seen = new Set<string>()
      rows.forEach((row, i) => {
        const rat = `${at}[${i}]`
        if (typeof row?.id !== 'string' || !row.id) fail(file, `${rat}.id`, 'every row needs a string id')
        else if (seen.has(row.id)) fail(file, `${rat}.id`, `duplicate id "${row.id}"`)
        else seen.add(row.id)
        for (const [k, v] of Object.entries(row ?? {})) {
          const x = declared.get(k)
          if (!x) {
            if (!ent.standard_fields.includes(k)) fail(file, `${rat}.${k}`, `${ent.id} has no field "${k}"`)
            continue
          }
          if (v === null || v === undefined) {
            if (x.required !== false) fail(file, `${rat}.${k}`, 'is required but null')
          } else if (x.type === 'enum') {
            const values = x.enum_id ? built.json.enums.find((e: Obj) => e.id === x.enum_id).values.map((e: Obj) => e.value) : Object.keys(x.values)
            if (!values.includes(v)) fail(file, `${rat}.${k}`, `"${v}" is not one of ${values.join(', ')}`)
          } else if (x.type === 'relation') {
            if (!ids.get(snake(x.relation_target))?.has(v as string)) fail(file, `${rat}.${k}`, `"${v}" is no ${x.relation_target} id in scenario ${name}`)
          } else {
            const want = x.type in VALUE_TYPE ? VALUE_TYPE[x.type] : 'string'
            if (want && typeof v !== want) fail(file, `${rat}.${k}`, `${x.type} expects a ${want}, got ${typeof v}`)
          }
        }
        for (const x of declared.values()) {
          if (x.required !== false && (row?.[x.name] === undefined)) fail(file, `${rat}.${x.name}`, 'is required but missing')
        }
      })
    }
  }
}

// ── run ─────────────────────────────────────────────────────────────────────────────────────────────
const out = (name: string, value: Json) => writeFileSync(join(here, name), JSON.stringify(value, null, 2) + '\n')
const importLocal = async (name: string): Promise<Obj> => import(pathToFileURL(join(here, name)).href)

async function main(): Promise<void> {
  const mod = await importLocal('model.ts')
  if (!mod.model) throw new Error('model.ts must export `model` (export const model = defineModel({ ... }))')
  const built = buildModel(mod.model as Model, 'model.ts')
  const previousPath = join(here, MODEL_JSON)
  const previous = existsSync(previousPath) ? JSON.parse(readFileSync(previousPath, 'utf8')) : {}
  const json: Obj = previous.editor === undefined ? built.json : { version: '1.0', editor: previous.editor, ...built.json }
  checkSchema(MODEL_JSON, 'datamodel-model.schema.json', json)

  let seedJson: Seed | undefined
  if (existsSync(join(here, 'seed.ts'))) {
    const seedMod = await importLocal('seed.ts')
    if (!seedMod.seed) throw new Error('seed.ts must export `seed` (export const seed = scenarios(model, { ... }))')
    seedJson = seedMod.seed as Seed
    checkSchema(SEED_JSON, 'datamodel-seed.schema.json', seedJson)
    checkSeed(seedJson, { ...built, json }, 'seed.ts')
  }
  if (errors.length) throw new Error('')
  out(MODEL_JSON, json)
  writeFileSync(join(here, 'model.dbml'), renderDbml(json))
  if (seedJson) out(SEED_JSON, seedJson as unknown as Json)
  console.log(`gen: wrote ${[MODEL_JSON, 'model.dbml', ...(seedJson ? [SEED_JSON] : [])].map((f) => join(basename(here), f)).join(', ')}`)
}

main().catch((e: Error) => {
  if (e.message) errors.push(`gen: ${e.message}`)
  console.error(errors.join('\n'))
  process.exit(1)
})
