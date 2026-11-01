---
id: evidence.crm-sync-retries
claim: I can make writes to an external API safe to retry.
supports: [capability.api-integration]
artifacts:
  - {repo: me/crm-sync, ref: 4f2c1a9, path: src/sync/writer.py}
level: 2
assistance: pair
---
## What it shows
The retry logic is mine and I can explain it.

## What it doesn't show yet
I haven't tested it against a real timeout.
