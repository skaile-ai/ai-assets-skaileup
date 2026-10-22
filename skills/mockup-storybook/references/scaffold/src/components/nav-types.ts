/** One destination of the shell, in the order the navigation shows it. */
export interface NavEntry {
  label: string
  /** Route path of the screen, `/<screen_id>`. */
  to: string
  icon?: string
  group?: string
  /** Kept in the narrow bottom bar. */
  pinned?: boolean
}
