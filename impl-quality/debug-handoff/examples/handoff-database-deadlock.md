# Debug Handoff — postgres-deadlock-under-load

> Paste this entire file into a fresh chat. It is self-contained: no prior context required.

## Bug Description

Under sustained load (~200 RPS sustained for 5+ minutes), our Postgres 15 instance logs intermittent
`deadlock detected` errors in the application logs, and the affected requests return HTTP 500. The
deadlocks correlate with bursts of concurrent writes to two tables — `orders` and `inventory` — that
are touched in the same transaction by two different code paths that take the locks in opposite
order. Impact: ~0.3% of orders during peak hours fail and require manual retry. The bug does not
reproduce in staging because staging traffic patterns are not concurrent enough.

## Repro Steps

1. Spin up the prod-mirror staging environment with the production traffic replay tool.
2. Replay the 2026-05-01 14:00–14:30 prod traffic at 1.5x speed.
3. Tail the application log for `40P01` (Postgres deadlock SQLSTATE).
4. Observe: 4-8 deadlock errors during the 30-minute replay window.

Frequency: ~0.3% of orders under peak load (~200 RPS); zero under nominal load (~30 RPS). The bug
needs concurrency to manifest.

## Environment

- OS / runtime: Ubuntu 22.04 LTS, Postgres 15.5, Node 20.11 LTS, application runs in 4-pod
  Kubernetes deployment on AWS EKS
- Branch / commit: `main` @ `c4e8a7d2` (production HEAD as of 2026-05-08)
- Relevant env vars: `<env:DATABASE_URL>`, `<env:DB_POOL_SIZE>`, `<env:LOG_LEVEL>`
- Last working commit (if known): unknown — the deadlock predates structured logging; no historic
  baseline. The earliest log we have showing this error is 2026-03-18.
- Redacted: `<env:DATABASE_URL>` (contained the production password in the `?password=` query string)

## Attempts So Far

| # | What was tried | Outcome | Why ruled out |
|---|----------------|---------|---------------|
| 1 | Increased `<env:DB_POOL_SIZE>` from 10 to 25 per pod | No change in deadlock rate | More connections do not change lock ordering; this only addresses connection-pool starvation, which was not the bottleneck. |
| 2 | Added `SELECT ... FOR UPDATE` on `inventory` row before the `UPDATE orders` in the order-fulfillment path | Deadlock rate dropped from 0.3% to 0.18% | Partial fix. Still see deadlocks because the inventory-restock path takes locks in opposite order without the explicit `FOR UPDATE`. |
| 3 | Set `default_transaction_isolation = 'read committed'` (was previously `repeatable read`) on the database | No change | The deadlock is a row-level lock cycle, not a phantom-read or serialization conflict. Isolation level does not affect it. |
| 4 | Reduced batch size in the inventory-restock cron from 500 rows to 50 rows per transaction | Deadlock rate dropped from 0.18% to 0.09% | Smaller transactions hold locks for less time, which reduces collision probability but does not eliminate it. Still seeing 1-3 errors per peak hour. |

## Current Hypothesis

The two transactions that deadlock — order-fulfillment and inventory-restock — acquire row locks on
`orders` and `inventory` in opposite order. Order-fulfillment locks `orders.<order_id>` first then
`inventory.<sku>`; inventory-restock locks `inventory.<sku>` first then `orders.<order_id>` (to write the
restock-impact audit row). Standardizing the lock-acquisition order across BOTH paths to always lock
`inventory` first should eliminate the cycle entirely. Confidence: medium — we have the lock graph
from `pg_stat_activity` snapshots during a deadlock, and it matches this story; we have not yet
shipped the fix to verify.

## Suggested Next Steps

1. Enable `log_lock_waits = on` and `deadlock_timeout = 1s` on the staging mirror, then re-run the
   traffic replay. Capture the `pg_stat_activity` snapshot at the moment of the next deadlock.
   Rationale: confirms the lock cycle hypothesis with direct evidence rather than circumstantial.
2. If the lock cycle is confirmed, refactor the inventory-restock path to acquire the `inventory`
   row lock FIRST and the `orders` audit row lock SECOND. Verify with the same traffic replay.
   Rationale: directly fixes the cycle. Standardize as a code-review rule afterwards.
3. As a backstop independent of the cause, wrap both code paths in a retry-on-`40P01` decorator
   that retries up to 2 times with exponential backoff. Rationale: even after the fix, transient
   deadlocks can occur from new code paths added later — the retry is cheap insurance.

## Files & Paths Involved

- `src/server/orders/fulfill.ts` — order-fulfillment transaction (locks `orders` then `inventory`)
- `src/server/inventory/restock.ts` — inventory-restock transaction (locks `inventory` then `orders`)
- `src/server/db/transaction.ts` — central transaction helper that should host the retry decorator
- `migrations/2026-04-12_add_restock_audit.sql` — added the `orders` audit-write that introduced
  the cross-table lock in the restock path; this migration date matches the regression onset
- `_concept/blueprint/datamodel/model.json` — entity definitions for `orders` and `inventory`

## Open Questions for the Next Agent

- Is the inventory-restock cron's batch size of 50 still appropriate, or should it drop further to
  10? Trade-off: smaller batches → less collision, but more cron iterations and more total Postgres
  round-trips.
- Should the retry-on-`40P01` decorator be applied repo-wide via `db.transaction()`, or only on the
  two known-affected paths? Repo-wide is safer but masks other bugs.
- Are there other code paths that touch both `orders` and `inventory` in the same transaction?
  `git grep -lE "BEGIN|transaction" src/` shows 14 candidate files — worth a quick audit.

## Out-of-Scope (do NOT do these)

- Schema changes — too risky pre-release. The CTO has explicitly ruled out adding columns or
  indexes during the next 14 days.
- Switching to a different database (e.g. CockroachDB for built-in retry) — multi-quarter effort,
  not aligned with current roadmap.
- Disabling the `orders` audit row in the restock path — compliance requires it.
- Increasing the application-level connection pool beyond 25 per pod — already verified no benefit
  in attempt 1, and risks overwhelming the database CPU under load.
