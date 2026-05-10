# Debug Handoff — auth-oauth-redirect-loop

> Paste this entire file into a fresh chat. It is self-contained: no prior context required.

## Bug Description

After completing the OAuth flow with our identity provider, the browser enters an infinite redirect
loop between `/api/auth/callback` and `/login`. The session cookie is set on the response from
`/callback`, but the next request to `/login` does not present it, so the middleware redirects back
to `/callback` for a fresh round-trip. The bug reproduces in production for ~95% of users on Safari
17 and ~10% on Chrome 124+. It does not reproduce on localhost. Impact: new sign-ups are blocked
on Safari; existing sessions are unaffected.

## Repro Steps

1. Open a private/incognito window in Safari 17 (production env, not localhost).
2. Navigate to `https://app.skaile.ai/login`.
3. Click "Sign in with Google".
4. Complete the Google OAuth flow.
5. Observe the URL bar: it bounces between `/api/auth/callback?code=...` and `/login` indefinitely.

Frequency: deterministic on Safari 17 in production; intermittent (~10%) on Chrome 124+ in production.

## Environment

- OS / runtime: macOS 14.4 (Sonoma) + Safari 17.4; Node 20.11 LTS on the server
- Branch / commit: `feat/oauth-callback-cookie-fix` @ `a9f3c2e1`
- Relevant env vars: `<env:OAUTH_CLIENT_SECRET>`, `<env:OAUTH_REDIRECT_URI>`, `<env:COOKIE_DOMAIN>`, `<env:SESSION_SECRET>`
- Last working commit (if known): `7b1d04f9` — known-good, just before the cookie middleware refactor on 2026-04-22
- Redacted: `<env:OAUTH_CLIENT_SECRET>`, `<env:SESSION_SECRET>` (originally hardcoded in a debug log)

## Attempts So Far

| # | What was tried | Outcome | Why ruled out |
|---|----------------|---------|---------------|
| 1 | Added `Secure; HttpOnly; SameSite=Lax` to the session cookie set by `/api/auth/callback` | Loop persists on Safari; Chrome unchanged | Cookie attributes alone do not fix it. Inspector confirms the cookie is set in the response header but missing from subsequent request headers on Safari. |
| 2 | Reordered middleware so the session reader runs before the auth-redirect guard | No change | Middleware order is correct in v3 of the framework. Verified by adding a `console.log` — guard sees the request without the cookie. |
| 3 | Set `Domain=.skaile.ai` explicitly on the cookie (was previously implicit) | No change on Safari; Chrome dropped to ~5% loop rate | Domain attribute is part of the picture but not the whole picture. Safari is rejecting the cookie for a different reason. |

## Current Hypothesis

The cookie's `SameSite=Lax` attribute, combined with the cross-site redirect from Google's OAuth
endpoint back to our `/api/auth/callback`, triggers Safari's Intelligent Tracking Prevention to drop
the cookie. Confidence: low — this is the most plausible candidate based on Safari's known stricter
ITP rules vs. Chrome, but we have not yet captured a network log proving it.

## Suggested Next Steps

1. Capture a full network log in Safari 17 with the Develop > Show Web Inspector > Network tab, then
   filter the response from `/api/auth/callback` and inspect the exact `Set-Cookie` header. Compare
   with the request headers on the very next navigation. Rationale: this confirms or refutes the ITP
   hypothesis directly.
2. If the cookie IS in the response but NOT in the next request, try `SameSite=None; Secure;
   Partitioned` (note: `Partitioned` is the CHIPS attribute, supported on Safari 16.4+). Rationale:
   CHIPS is the modern fix for cross-site cookie drops under ITP.
3. If both fail, escalate by asking the user to reach out to the OAuth provider's support: their
   recent changelog mentions a redirect-URI handling change on 2026-04-15 that lines up with our
   regression date (2026-04-22).

## Files & Paths Involved

- `src/server/auth/callback.ts` — OAuth callback handler that sets the session cookie
- `src/server/middleware/session.ts` — reads the cookie, attaches `req.user`
- `src/server/middleware/auth-guard.ts` — redirects to `/login` if `req.user` is missing
- `src/config/cookie.ts` — central cookie attribute config (Domain, SameSite, Secure)
- `package.json` — see `dependencies."@skaile/auth"` version `^2.3.0`

## Open Questions for the Next Agent

- Has the OAuth provider's `state` parameter handling changed recently? Worth checking their
  changelog for 2026-04-15 onwards.
- Is the `<env:COOKIE_DOMAIN>` value in production identical to the apex domain users hit (i.e.
  `.skaile.ai` vs. `app.skaile.ai`)? A mismatch here would cause the same symptom.
- Does Safari's "Prevent cross-site tracking" toggle being on (default) vs. off change the repro
  rate? If the loop disappears with the toggle off, ITP is confirmed.

## Out-of-Scope (do NOT do these)

- Switching OAuth providers — already evaluated, business reasons rule it out for this release.
- Disabling `SameSite` entirely (i.e. setting `SameSite=None` without `Secure`) — security review
  blocked this in attempt 1.
- Implementing a custom session-id query parameter as a cookie fallback — adds attack surface, the
  team agreed not to pursue this.
- Modifying `_concept/` or any architecture-level decision — this is a runtime bug, not a design
  problem.
