// One route per screen component, built from `src/screens/*.vue`: adding a screen needs no edit here.
import type { Component } from 'vue'
import type { RouteRecordRaw } from 'vue-router'

const screens = import.meta.glob<{ default: Component }>('../screens/*.vue')

/** Screen ids (the file names), alphabetical; `nav.ts` decides the order the shell shows. */
export const screenIds = Object.keys(screens)
  .map((path) => path.replace(/^.*\/(.+)\.vue$/, '$1'))
  .sort()

export const labelOf = (id: string): string => id.replace(/[-_]+/g, ' ').replace(/^./, (c) => c.toUpperCase())

const first = screenIds[0]

export const routes: RouteRecordRaw[] = [
  ...screenIds.map((id): RouteRecordRaw => ({
    path: `/${id}`,
    name: id,
    component: screens[`../screens/${id}.vue`]!,
    meta: { screen: id },
  })),
  first
    ? { path: '/', redirect: `/${first}` }
    : { path: '/:pathMatch(.*)*', component: { render: () => 'No screens yet: add src/screens/<screen_id>.vue.' } },
]
