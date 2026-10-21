# `specs.json` — the build-time bridge


`specs.json` bridges source artefacts to Astro templates at build time.
Every value a template would otherwise need to resolve — a target's href,
an item's derived id, a screen's rendered spec body — is pre-resolved here
(see the skill body, § What is different about Astro); the template only interpolates.

```json
{
  "app_nav_id": "app-nav",
  "app_nav": [
    {
      "label": "Login",
      "href": "/screen/login",
      "element_id": "app-nav-1",
      "source": "derived"
    }
  ],
  "screens": [
    {
      "screen_id": "login",
      "screen_path": "07_screens/login.md",
      "rendered_html": "screen/login.html",
      "title": "Login",
      "implements": ["05_features/auth/login.md"],
      "floorplan": "wizard",
      "posture": "transient",
      "density": "comfortable",
      "regions": { "step-body": { "shows": "user", "representation": "page" } },
      "floorplan_html": "floorplan/login.html",
      "floorplan_frame_html": "<!DOCTYPE html><html>…the filled frame document…</html>",
      "floorplan_notice": null,
      "body_html": "<p>Intro prose…</p><h3>Purpose</h3><p>…</p>",
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading"],
          "provisional": false,
          "region": "footer",
          "source_anchor": "07_screens/login.md#elements/submit-button"
        },
        {
          "element_id": "go-register",
          "kind": "link",
          "label": "Create an account",
          "states": ["default"],
          "provisional": false,
          "target": "register",
          "href": "/screen/register",
          "source_anchor": "07_screens/login.md#elements/go-register"
        },
        {
          "element_id": "recent-signins",
          "kind": "table",
          "label": "Recent sign-ins",
          "states": ["default"],
          "provisional": false,
          "columns": ["Name", "Email"],
          "sample_rows": [["Lena M.", "lena@example.com"]],
          "row_target": "verify-email",
          "row_href": "/screen/verify-email",
          "source_anchor": "07_screens/login.md#elements/recent-signins"
        },
        {
          "element_id": "signup-benefits",
          "kind": "list",
          "label": "Why join",
          "states": ["default"],
          "provisional": false,
          "items": [
            {
              "label": "See your login screen",
              "target": "login",
              "href": "/screen/login",
              "element_id": "see-your-login-screen",
              "provisional": true
            },
            {
              "label": "Get onboarding tips",
              "element_id": "get-onboarding-tips",
              "provisional": true
            }
          ],
          "source_anchor": "07_screens/login.md#elements/signup-benefits"
        }
      ],
      "journeys": ["user-signs-in"]
    }
  ],
  "journeys": [
    {
      "journey_id": "user-signs-in",
      "title": "User signs in",
      "description": "First-time user authenticates.",
      "rendered_html": "journey/user-signs-in.html",
      "source": "04_journeys/stories.yaml#user-signs-in",
      "screen_sequence": ["login", "home"]
    }
  ],
  "token_vars": {
    "--token-color-primary": "#0ea5e9",
    "--token-spacing-sm": "8px"
  },
  "features": [
    {
      "feature_path": "05_features/auth/login.md",
      "rendered_screens": ["07_screens/login.md"]
    }
  ]
}
```

Every `items[]` entry (whether the schema's bare-string shorthand or the
`{label, target?}` dict form) is normalised in `specs.json` to always carry
its own resolved `element_id` and `provisional` — this is the § Auto-slug
fallback "items[] id derivation" rule (see STEP 2 below) executed once at
generation time so the template never has to re-derive it. `href` is
present on an item only when the item declares a `target`.

A screen with a usable floorplan carries `floorplan_html` (the frame's site path) and
`floorplan_frame_html` (the whole filled frame document, built per
`tree/09_mockup/walkthrough/README.md § Floorplan frame`), and `floorplan_notice: null`; the
template writes `floorplan/<screen_id>.html` from the one and the two iframes from the other. A
screen without one carries `floorplan_html: null`, no `floorplan_frame_html`, and the reason in
`floorplan_notice`, which the template prints in the `.floorplan-notice` paragraph.

**specs.json → manifest.json projection.** `specs.json` carries
template-convenience fields that MUST NOT be copied to `manifest.json`:
- `screens[].title`, `screens[].journeys[]`, `screens[].body_html`, `screens[].floorplan_frame_html`, `screens[].floorplan_notice`
- `app_nav_id`, `app_nav[].element_id`
- `screens[].elements[].href`, `screens[].elements[].row_href`
- `screens[].elements[].items[].element_id`, `screens[].elements[].items[].provisional`, `screens[].elements[].items[].href`
- `journeys[].title`, `journeys[].description`
- `app_nav[].href` (manifest's `app_nav[].target` carries the same resolved value, under the pinned field name — see § Manifest schema)

Build `manifest.json` from the in-memory model using the pinned shape
directly (not by serialising `specs.json`) — this also means every
`manifest.json#screens[].elements[].target` / `.row_target` /
`.items[].target` stays the **declared** `<screen>[#fragment]` value (per
`tree/09_mockup/walkthrough/README.md` § Field semantics), never the resolved
`href` — only `specs.json` and the rendered HTML carry the resolved form.

