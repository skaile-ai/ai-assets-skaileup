# `specs.json` — the build-time bridge


`specs.json` bridges source artefacts to Astro templates at build time.
Every value a template would otherwise need to resolve — a target's href,
an item's derived id, a screen's rendered spec body — is pre-resolved here
(see the skill body, § What is different about Astro); the template only interpolates.

```json
{
  "app_nav": [
    {
      "label": "login",
      "href": "/screen/00_auth/login",
      "source": "derived"
    }
  ],
  "screens": [
    {
      "screen_id": "01_user_auth/login",
      "screen_path": "07_screens/01_user_auth/login.md",
      "rendered_html": "screen/01_user_auth/login.html",
      "group": "01_user_auth",
      "title": "Login",
      "implements": ["05_features/01_user_auth/login.md"],
      "data_entities": ["User"],
      "layout": "07_screens/shell.md",
      "body_html": "<p>Intro prose…</p><h3>Purpose</h3><p>…</p>",
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading"],
          "provisional": false,
          "source_anchor": "07_screens/01_user_auth/login.md#elements/submit-button"
        },
        {
          "element_id": "go-register",
          "kind": "link",
          "label": "Create an account",
          "states": ["default"],
          "provisional": false,
          "target": "01_user_auth/register",
          "href": "/screen/01_user_auth/register",
          "source_anchor": "07_screens/01_user_auth/login.md#elements/go-register"
        },
        {
          "element_id": "recent-signins",
          "kind": "table",
          "label": "Recent sign-ins",
          "states": ["default"],
          "provisional": false,
          "columns": ["Name", "Email"],
          "sample_rows": [["Lena M.", "lena@example.com"]],
          "row_target": "01_user_auth/verify_email",
          "row_href": "/screen/01_user_auth/verify_email",
          "source_anchor": "07_screens/01_user_auth/login.md#elements/recent-signins"
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
              "target": "01_user_auth/login",
              "href": "/screen/01_user_auth/login",
              "element_id": "see-your-login-screen",
              "provisional": true
            },
            {
              "label": "Get onboarding tips",
              "element_id": "get-onboarding-tips",
              "provisional": true
            }
          ],
          "source_anchor": "07_screens/01_user_auth/login.md#elements/signup-benefits"
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
      "screen_sequence": ["01_user_auth/login", "02_dashboard/home"]
    }
  ],
  "token_vars": {
    "--token-color-primary": "#0ea5e9",
    "--token-spacing-sm": "8px"
  },
  "features": [
    {
      "feature_path": "05_features/01_user_auth/login.md",
      "rendered_screens": ["07_screens/01_user_auth/login.md"]
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

**specs.json → manifest.json projection.** `specs.json` carries
template-convenience fields that MUST NOT be copied to `manifest.json`:
- `screens[].title`, `screens[].group`, `screens[].journeys[]`, `screens[].body_html`
- `screens[].elements[].href`, `screens[].elements[].row_href`
- `screens[].elements[].items[].element_id`, `screens[].elements[].items[].provisional`, `screens[].elements[].items[].href`
- `journeys[].title`, `journeys[].description`
- `app_nav[].href` (manifest's `app_nav[].target` carries the same resolved value, under the pinned field name — see § Manifest schema)

Build `manifest.json` from the in-memory model using the pinned shape
directly (not by serialising `specs.json`) — this also means every
`manifest.json#screens[].elements[].target` / `.row_target` /
`.items[].target` stays the **declared** `screen_id[#fragment]` value (per
`tree/09_mockup/walkthrough/README.md` § Field semantics), never the resolved
`href` — only `specs.json` and the rendered HTML carry the resolved form.

