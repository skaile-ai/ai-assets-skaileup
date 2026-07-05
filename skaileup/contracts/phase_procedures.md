# Phase Procedures

Shared PROCEDUREs for handoff-writing skills. Invoke from a STEP as
`DO shared:<name>` with indented `key: value` parameter lines
(skill_grammar.md § PROCEDURE). A skill using one MUST list this file in
REFERENCES.

PROCEDURE read_predecessor
  in: predecessor_path, predecessor_skill
  - Open <predecessor_path>; if missing, refuse:
    > "[<skill>] required file <predecessor_path> not found.
    >  Run <predecessor_skill> first."   (iron_laws § 7)
  - Parse frontmatter; copy slice_id, feature_title (+ feature_path on the
    impl side) VERBATIM — never re-derive (slice_loop.md § Handoff frontmatter)
  - Cache the body sections the current phase consumes

PROCEDURE draft_checkpoint_write
  in: artifact_path, checkpoint_id
  - Compose the full artifact in memory: frontmatter per slice_loop.md
    § Handoff frontmatter + the skill's pinned body sections
  - Show the complete draft to the user
  - CHECKPOINT <checkpoint_id>
    > "Approve to write to <artifact_path>, or tell me what to change."
    NEVER write before approval.
  - Write <artifact_path>; verify the file exists and its frontmatter parses
  - If the skill directory has a validator.py:
    $ python3 <skill_dir>/validator.py <artifact_path>
    On non-zero exit: report the validator errors and STOP.

PROCEDURE emit_lifecycle
  in: skill_name, kv_pairs
  - EMIT [<skill_name>] completed <kv_pairs>
  - Walk the skill's CHECKLIST; report any unchecked item instead of
    claiming success
