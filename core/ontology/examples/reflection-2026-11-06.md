---
id: reflection.2026-11-06
date: 2026-11-06
links: [sprint.2026-11-s03, inquiry.idempotency-key-ttl]
next_action: Explain in five sentences why the retry needs the key
---
## What did you build or try?
A retry path for CRM writes, with two tests for idempotency keys.

## What clicked?
The key makes the retry safe, not the retry itself.

## What is still fuzzy?
How long the server should remember a key.
