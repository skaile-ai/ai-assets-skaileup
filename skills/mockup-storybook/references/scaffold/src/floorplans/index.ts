import type { Component } from 'vue'
import Board from './board.vue'
import HubAreas from './hub-areas.vue'
import ListReport from './list-report.vue'
import MasterDetail from './master-detail.vue'
import ModeEditor from './mode-editor.vue'
import ObjectPage from './object-page.vue'
import Overview from './overview.vue'
import Reader from './reader.vue'
import Settings from './settings.vue'
import ShellDock from './shell-dock.vue'
import ShellMobileTabs from './shell-mobile-tabs.vue'
import ShellSidebar from './shell-sidebar.vue'
import ShellTopbar from './shell-topbar.vue'
import TabbedTool from './tabbed-tool.vue'
import ThreePane from './three-pane.vue'
import Wizard from './wizard.vue'

/** All 16 floorplans by rulebook id. */
export const floorplans = {
  'board': Board,
  'hub-areas': HubAreas,
  'list-report': ListReport,
  'master-detail': MasterDetail,
  'mode-editor': ModeEditor,
  'object-page': ObjectPage,
  'overview': Overview,
  'reader': Reader,
  'settings': Settings,
  'shell-dock': ShellDock,
  'shell-mobile-tabs': ShellMobileTabs,
  'shell-sidebar': ShellSidebar,
  'shell-topbar': ShellTopbar,
  'tabbed-tool': TabbedTool,
  'three-pane': ThreePane,
  'wizard': Wizard,
} as const satisfies Record<string, Component>

export type FloorplanId = keyof typeof floorplans

/** The four shell floorplans; `Shell.vue` picks one by the id `07_screens/shell.md` names. */
export const shells = {
  'shell-sidebar': ShellSidebar,
  'shell-topbar': ShellTopbar,
  'shell-dock': ShellDock,
  'shell-mobile-tabs': ShellMobileTabs,
} as const satisfies Record<string, Component>

export type ShellId = keyof typeof shells
