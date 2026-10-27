---
shell_frame: shell-topbar
organization: object-led
primary_surface: topbar
navigation: decided
elements:
  - id: app-nav
    kind: nav
    label: "Main navigation"
    states: [default]
    region: destinations
    items:
      - { id: nav-polls, label: "Polls", target: polls }
      - { id: nav-places, label: "Places", target: places }
last_updated: 2026-10-25
approved: 2026-10-25
---

# Shell

## Navigation
- `polls` - group main, badge: count of open polls, primary
- `places` - group main, no badge, primary

## Layout Areas
- `top-bar`: the brand mark, the destinations, the palette trigger, the "Open poll" action (NAV-1, BTN-1) and the account menu.
- `page-header`: the title of the current screen and its one primary action.
- `work-area`: the screen floorplan, full width; the page scrolls.
- `peek`: a popover anchored to a Poll row (SURF-1).

## Responsive Behaviour
The frame's own breakpoints apply: below 960 px the destinations fold into a menu panel under the bar. The app moves none.

## Shared Patterns
Page-header composition: title left, one primary action right. A breadcrumb appears only below a Poll. The top bar persists while the work area shows a loading skeleton (FBK-1). Empty, error and message patterns are MSG-1 and MSG-2; dialogs are MOD-1 and EDIT-1.
