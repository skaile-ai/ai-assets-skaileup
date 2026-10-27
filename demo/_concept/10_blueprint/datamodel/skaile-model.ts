// skaile-model 1.0.0
// Authoring DSL for the project's data model. Copied by architecture-datamodel; never hand-edited.
// Zero dependencies, no Node APIs: model.ts and seed.ts import it in the browser (mockup) and in gen.ts.

export type Proposed = { by: string; on: string; source: string }
export type OnDelete = 'cascade' | 'set_null' | 'restrict'
export type StandardField = 'id' | 'created_at' | 'updated_at'
export type ScalarType =
  | 'string' | 'text' | 'richtext' | 'integer' | 'float' | 'decimal' | 'boolean' | 'date' | 'datetime'
  | 'json' | 'uuid' | 'slug' | 'email' | 'url' | 'password' | 'image' | 'file'

/** Options every field takes; each maps to the key of the same name in model.json. */
export interface FieldOpts {
  required?: boolean
  unique?: boolean
  primary?: boolean
  readonly?: boolean
  indexed?: boolean
  max_length?: number
  default?: unknown
  placeholder?: string
  faker?: string
  description?: string
  /** Marks the field as proposed: status "proposed", proposed_by, proposed_on, source in model.json. */
  proposed?: Proposed
}
/** Options of an m2o field. `inverse` is the relationship's inverse_label. */
export interface RelationOpts extends FieldOpts { on_delete?: OnDelete; label?: string; inverse?: string }
export interface ManyToManyOpts { through: Target; label?: string; inverse?: string }

/** A relation target: the entity itself (lazily, so order does not matter) or its id as a string, which is
 *  the form for a self-reference (`f.m2o('Task')` inside Task) because TypeScript cannot type a cycle. */
export type Target = (() => AnyEntity) | string

export interface SharedEnum<V extends Record<string, string> = Record<string, string>> {
  readonly kind: 'enum'
  readonly values: V
}

type Def =
  | { kind: 'scalar'; type: ScalarType; opts: FieldOpts }
  | { kind: 'enum'; values: Record<string, string>; opts: FieldOpts }
  | { kind: 'enumRef'; enum: SharedEnum; opts: FieldOpts }
  | { kind: 'm2o'; target: Target; opts: RelationOpts }
  | { kind: 'm2m'; target: Target; opts: ManyToManyOpts }

/** One field. `_ts`, `_req` and `_virtual` exist for the type system only. */
export type FieldDef<T = unknown, R extends boolean = boolean, V extends boolean = false> = Def & {
  readonly _ts: T
  readonly _req: R
  readonly _virtual: V
}
export type Fields = Record<string, FieldDef<any, boolean, boolean>>

type Req<O> = O extends { required: false } ? false : true
const def = <T, R extends boolean, V extends boolean = false>(d: Def) => d as unknown as FieldDef<T, R, V>
const scalar = <T>(type: ScalarType) =>
  <const O extends FieldOpts = {}>(opts?: O) => def<T, Req<O>>({ kind: 'scalar', type, opts: opts ?? {} })

/** The field vocabulary: one builder per semantic type of model.md, plus enum and relations. */
export const f = {
  string: scalar<string>('string'),
  text: scalar<string>('text'),
  richtext: scalar<string>('richtext'),
  integer: scalar<number>('integer'),
  float: scalar<number>('float'),
  decimal: scalar<number>('decimal'),
  boolean: scalar<boolean>('boolean'),
  date: scalar<string>('date'),
  datetime: scalar<string>('datetime'),
  json: scalar<unknown>('json'),
  uuid: scalar<string>('uuid'),
  slug: scalar<string>('slug'),
  email: scalar<string>('email'),
  url: scalar<string>('url'),
  password: scalar<string>('password'),
  image: scalar<string>('image'),
  file: scalar<string>('file'),
  /** Inline enum: PascalCase value → description. */
  enum: <const V extends Record<string, string>, const O extends FieldOpts = {}>(values: V, opts?: O) =>
    def<keyof V & string, Req<O>>({ kind: 'enum', values, opts: opts ?? {} }),
  /** Reference to an enum declared with `sharedEnum` and listed in `defineModel({ enums })`. */
  enumRef: <V extends Record<string, string>, const O extends FieldOpts = {}>(e: SharedEnum<V>, opts?: O) =>
    def<keyof V & string, Req<O>>({ kind: 'enumRef', enum: e, opts: opts ?? {} }),
  /** Many-to-one, owning side; the field name ends in `_id`. */
  m2o: <const O extends RelationOpts = {}>(target: Target, opts?: O) =>
    def<string, Req<O>>({ kind: 'm2o', target, opts: opts ?? {} }),
  /** Many-to-many through an explicit junction entity (two m2o). Holds no column, so a row has no such key. */
  m2m: (target: Target, opts: ManyToManyOpts) => def<never, true, true>({ kind: 'm2m', target, opts }),
}

export const sharedEnum = <const V extends Record<string, string>>(values: V): SharedEnum<V> =>
  ({ kind: 'enum', values })

export interface EntitySpec<F extends Fields = Fields> {
  /** Id of the glossary term this entity models (kebab-case); the entity id is its PascalCase form. */
  glossary: string
  display: string
  icon?: string
  color?: string
  position?: { x: number; y: number }
  from_features?: string[]
  standard_fields?: StandardField[]
  label_field?: Extract<keyof F, string>
  key_field?: Extract<keyof F, string>
  /** Marks the entity as proposed; see FieldOpts.proposed. */
  proposed?: Proposed
  fields: F
}
export interface Entity<F extends Fields = Fields> { readonly kind: 'entity'; readonly spec: EntitySpec<F> }
export type AnyEntity = Entity<any>

export const entity = <F extends Fields>(spec: EntitySpec<F>): Entity<F> => ({ kind: 'entity', spec })

export interface Model<
  E extends Record<string, AnyEntity> = Record<string, AnyEntity>,
  N extends Record<string, SharedEnum<any>> = Record<string, SharedEnum<any>>,
> {
  readonly version: '1.0'
  /** Keyed by entity id (PascalCase). */
  readonly entities: E
  /** Keyed by shared-enum id (snake_case). */
  readonly enums: N
}

export const defineModel = <E extends Record<string, AnyEntity>, N extends Record<string, SharedEnum<any>> = {}>(
  spec: { entities: E; enums?: N },
): Model<E, N> => ({ version: '1.0', entities: spec.entities, enums: (spec.enums ?? {}) as N })

type Simplify<T> = { [K in keyof T]: T[K] } & {}
type StoredKeys<F> = { [K in keyof F]: F[K] extends { _virtual: true } ? never : K }[keyof F]
type RequiredKeys<F> = { [K in StoredKeys<F>]: F[K] extends { _req: true } ? K : never }[StoredKeys<F>]
type OptionalKeys<F> = Exclude<StoredKeys<F>, RequiredKeys<F>>

/** A row of an entity: `id`, the declared fields (optional ones `T | null` and may be omitted) and the timestamps. */
export type Infer<E> = E extends Entity<infer F>
  ? Simplify<
      { id: string; created_at?: string; updated_at?: string }
      & { [K in RequiredKeys<F> & string]: F[K] extends { _ts: infer T } ? T : never }
      & { [K in OptionalKeys<F> & string]?: (F[K] extends { _ts: infer T } ? T : never) | null }
    >
  : never

/** `ProjectMember` → `project_member`: the seed's entity key and the prefix of a field id. */
export type Snake<S extends string, Acc extends string = ''> = S extends `${infer H}${infer T}`
  ? Snake<T, `${Acc}${H extends Lowercase<H> ? H : Acc extends '' ? Lowercase<H> : `_${Lowercase<H>}`}`>
  : Acc
export const snake = (s: string): string => s.replace(/[A-Z]/g, (c, i) => (i ? '_' : '') + c.toLowerCase())

export type SeedData<M> = M extends Model<infer E, any> ? { [K in keyof E & string as Snake<K>]?: Infer<E[K]>[] } : never
export interface Scenario<M> { description: string; data: SeedData<M> }
export type StandardScenario = 'empty' | 'single_user' | 'populated' | 'edge_cases'
/** The shape of seed.json: also the runtime value `scenarios()` returns. */
export interface Seed<M = Model> { version: '1.0'; scenarios: Record<StandardScenario, Scenario<M>> & Record<string, Scenario<M>> }

/** Seed scenarios typed against the model: a row with an unknown or misspelled field fails `tsc`. */
export const scenarios = <M extends Model>(
  _model: M,
  s: Record<StandardScenario, Scenario<M>> & Record<string, Scenario<M>>,
): Seed<M> => ({ version: '1.0', scenarios: s })
