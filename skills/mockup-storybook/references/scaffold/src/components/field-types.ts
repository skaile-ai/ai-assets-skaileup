/** The semantic types of the data model (`datamodel-model.schema.json`) plus the two relation kinds. */
export type FieldType =
  | 'string' | 'text' | 'richtext' | 'integer' | 'float' | 'decimal' | 'boolean'
  | 'date' | 'datetime' | 'json' | 'uuid' | 'slug' | 'email' | 'url' | 'password'
  | 'image' | 'file' | 'enum' | 'm2o'
