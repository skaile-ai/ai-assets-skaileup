// Brand tokens -> `src/styles/tokens.css`.
//
// Reads `_concept/03_brand/brand.tokens.json` (and `brand.dark.tokens.json` when it exists),
// flattens them to `--token-*` custom properties as `tree/03_brand/brand.tokens.md § Flattening
// to CSS` says, and maps them onto the `--ui-*` variables Nuxt UI components read, so the
// prototype wears the brand. Without a token file the output is a comment and Nuxt UI keeps
// its defaults. `vite.config.ts` calls `writeTokens()` on every start; `npm run tokens` is the
// manual form.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const packageDir = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const brandDir = resolve(packageDir, '../../03_brand')
const lightFile = resolve(brandDir, 'brand.tokens.json')
const darkFile = resolve(brandDir, 'brand.dark.tokens.json')
const outFile = resolve(packageDir, 'src/styles/tokens.css')

/** The brand files `writeTokens` reads; the dev server watches them. */
export const brandFiles = [lightFile, darkFile]

type Json = Record<string, unknown>

const isObject = (value: unknown): value is Json =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

const hex2 = (n: number): string => Math.round(n).toString()

function colour(value: unknown): string | undefined {
  if (typeof value === 'string') return value
  if (!isObject(value)) return undefined
  const alpha = typeof value.alpha === 'number' ? value.alpha : 1
  if (alpha < 1 && Array.isArray(value.components)) {
    const [r, g, b] = (value.components as number[]).map((c) => hex2(c * 255))
    return `rgb(${r} ${g} ${b} / ${alpha})`
  }
  return typeof value.hex === 'string' ? value.hex : undefined
}

const dimension = (value: unknown): string | undefined =>
  isObject(value) && typeof value.value === 'number' && typeof value.unit === 'string'
    ? `${value.value}${value.unit}`
    : undefined

function shadow(value: unknown): string | undefined {
  const layers = Array.isArray(value) ? value : [value]
  const css = layers.map((layer) => {
    if (!isObject(layer)) return undefined
    const parts = [dimension(layer.offsetX), dimension(layer.offsetY), dimension(layer.blur), dimension(layer.spread), colour(layer.color)]
    if (parts.some((p) => p === undefined)) return undefined
    return `${layer.inset === true ? 'inset ' : ''}${parts.join(' ')}`
  })
  return css.every((c) => c !== undefined) ? css.join(', ') : undefined
}

function flattenValue(type: unknown, value: unknown): string | undefined {
  if (typeof value === 'string') {
    const alias = /^\{(.+)\}$/.exec(value)
    if (alias) return `var(--token-${alias[1]!.replaceAll('.', '-')})`
  }
  switch (type) {
    case 'color': return colour(value)
    case 'dimension': return dimension(value)
    case 'fontFamily': return Array.isArray(value) ? value.join(', ') : typeof value === 'string' ? value : undefined
    case 'shadow': return shadow(value)
    default: return typeof value === 'string' || typeof value === 'number' ? String(value) : undefined
  }
}

/** Token path (`color-primary`) to CSS value, in file order. */
function flatten(node: unknown, path: string[] = [], out = new Map<string, string>()): Map<string, string> {
  if (!isObject(node)) return out
  if ('$value' in node) {
    const css = flattenValue(node.$type, node.$value)
    if (css !== undefined) out.set(path.join('-'), css)
    else console.warn(`gen-tokens: skipped ${path.join('.')}: unreadable $value`)
    return out
  }
  for (const [key, child] of Object.entries(node)) if (!key.startsWith('$')) flatten(child, [...path, key], out)
  return out
}

/** Nuxt UI semantic variable (or Tailwind theme variable) -> the token that feeds it. */
const BRIDGE: Record<string, string[]> = {
  'color-primary': ['--ui-primary'],
  'color-secondary': ['--ui-secondary'],
  'color-accent': ['--ui-info'],
  'color-success': ['--ui-success'],
  'color-warning': ['--ui-warning'],
  'color-error': ['--ui-error'],
  'color-background': ['--ui-bg', '--ui-text-inverted'],
  'color-surface': ['--ui-bg-muted', '--ui-bg-elevated'],
  'color-text': ['--ui-text', '--ui-text-highlighted', '--ui-text-toned', '--ui-bg-inverted'],
  'color-text-muted': ['--ui-text-muted', '--ui-text-dimmed'],
  'color-border': ['--ui-border', '--ui-border-muted', '--ui-border-accented'],
  'radius-base': ['--ui-radius'],
  'spacing-base': ['--spacing'],
  'font-heading': ['--font-heading'],
  'font-body': ['--font-sans', '--font-body'],
  'font-mono': ['--font-mono'],
  'shadow-sm': ['--shadow-sm'],
  'shadow-md': ['--shadow-md'],
  'shadow-lg': ['--shadow-lg'],
}

function block(selector: string, tokens: Map<string, string>): string {
  const lines = [...tokens].map(([path, css]) => `  --token-${path}: ${css};`)
  for (const path of tokens.keys()) for (const variable of BRIDGE[path] ?? []) lines.push(`  ${variable}: var(--token-${path});`)
  return `${selector} {\n${lines.join('\n')}\n}\n`
}

function read(file: string): Map<string, string> | undefined {
  if (!existsSync(file)) return undefined
  try {
    return flatten(JSON.parse(readFileSync(file, 'utf8')))
  } catch (error) {
    console.warn(`gen-tokens: ${file} is not readable JSON (${(error as Error).message}); Nuxt UI defaults apply`)
    return undefined
  }
}

/** Generate `src/styles/tokens.css`; returns its path. */
export function writeTokens(): string {
  const light = read(lightFile)
  const dark = read(darkFile)
  const parts = ['/* Generated by scripts/gen-tokens.ts from _concept/03_brand/*.tokens.json. Do not edit. */\n']
  if (light?.size) parts.push(block(':root', light))
  else parts.push('/* No _concept/03_brand/brand.tokens.json yet: Nuxt UI defaults apply. */\n')
  if (dark?.size) parts.push(block('.dark', dark))
  mkdirSync(dirname(outFile), { recursive: true })
  const css = parts.join('\n')
  // Skip identical writes: a rewrite would make Vite reload the stylesheet for nothing.
  if (!existsSync(outFile) || readFileSync(outFile, 'utf8') !== css) writeFileSync(outFile, css)
  return outFile
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  console.log(`wrote ${writeTokens()}`)
}
