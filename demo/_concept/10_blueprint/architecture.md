---
apps: [web]
custom_services: []
custom_modules: [poll-closer]
protocols: [http]
external_integrations: [mail-delivery]
last_updated: 2026-10-24
---

# Architecture

### System context
Members use the web app in a phone browser. The app talks to one outside system.

#### External Integrations
- **mail-delivery**: an SMTP relay sends magic-link mails; the payload is the member's email address and a one-time link. A failed send is retried twice, then the member sees "mail not sent, try again". The SMTP credentials live in the server's environment, never in the repository.

### Containers
One container, `web`: the Nuxt app and its Nitro routes, connected to PostgreSQL. Endpoints are plain JSON over HTTP; errors answer a status code and a one-line message the screen shows.

### Components
- **poll-closer**: closes every open poll whose deadline has passed and applies the pick rule; asked for by `draw-pick`. It runs on a one-minute timer inside the Nitro process and depends on the data model's Poll, Vote and Place.

### Deployment
One container on the team's own server, behind a reverse proxy with HTTPS.

### Risks and technical debt
- The timer lives in the web process: a restart can delay a closing by a minute. Touches `draw-pick`.
- Magic links rely on the mail relay; no second channel exists. Touches `mail-delivery`.
