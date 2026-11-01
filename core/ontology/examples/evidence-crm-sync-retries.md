---
id: evidence.crm-sync-retries
claim: I can make writes to an external API safe to retry.
supports: [capability.api-integration]
artifacts:
  - repo: me/crm-sync
    ref: 4f2c1a9          # commit
    path: src/sync/writer.py
level: 2                  # explained
assistance: pair
reviewed_in: review.2026-11-08-crm-sync
---
What it shows, what it doesn't: the retry logic is mine and I can explain it;
I haven't yet tested it against a real timeout.
