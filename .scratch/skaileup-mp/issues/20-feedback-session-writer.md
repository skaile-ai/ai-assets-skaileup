# 20: Who writes a feedback session — the annotate → triage seam

**Type:** grilling
**Blocked by:** None (14 resolved)
**Status:** ready

## Question

Graduated from ticket 14, which ported the mockup domain and found the seam broken in the
source collection: **nothing writes `_concept/_feedback/sessions/<sid>.json`**, the artifact
the entire feedback half keys on.

Outside forge-concept's iframe, the annotation overlay downloads
`annotations-<hash>.json` to the *reader's* downloads folder, and a human must move and
rename it — the filename stem **becomes** the session id everything downstream keys on.
`index.json` is created and never appended to. Ticket 14 wrote that manual hop into
`mockup-annotate` explicitly rather than paper over it, but the hop is the question.

Decide:

- **Does `-mp` accept the manual hop, or does something write the session?** The obvious
  writer is forge-concept's iframe — but that makes the iframe the *only* supported path,
  which is a real product ruling, not a shrug. The alternative writers are a script shipped
  with `mockup-annotate` or a step in `mockup-feedback` that adopts a downloaded file.
- **Note the map's fence:** making forge-concept write it is a forge-concept edit, which
  this map rules out (see Out of scope, and ticket 09's two forge-concept-gated follow-ons).
  So "the iframe writes it" is a ruling about what `-mp` *depends on*, not work `-mp` does.
  If the answer is "iframe only", say so on the map and note what breaks outside it.
- **Who owns the session id**, given the filename stem currently carries it. If a writer
  lands, does the id stay filename-derived or become explicit in the file?
- **`index.json`** — created and never appended to. Does it survive at all?

Two riders found in the same pass, both cheap and both real:

- **`triage.py` resolves journeys to `experience/journeys/<id>.md`, but journeys live in
  `stories.yaml`.** Every journey annotation therefore lands unresolved.
- **The overlay never emits `specRef.feature`**, although `triage.py` resolves it. So one of
  the three routing keys is dead on the producing side.

## Answer

_(pending)_
