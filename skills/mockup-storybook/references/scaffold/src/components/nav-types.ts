/** One destination of the shell, in the order the navigation shows it. */
export interface NavEntry {
  label: string
  /** Route path of the screen, `/<screen_id>`; `/pending/<item-slug>` while the screen is not specified. */
  to: string
  /** The object a pending destination lists (`Task`): its `TaskRow` shows sample rows there. */
  object?: string
  icon?: string
  group?: string
  /** Kept in the narrow bottom bar. */
  pinned?: boolean
}
