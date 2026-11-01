---
id: brief.crm-sync-retries
title: Make CRM sync retries safe under timeouts
user: The ops lead who reconciles duplicate CRM records by hand each Monday
outcome: A timed-out write can be retried without creating a duplicate record
practises: [capability.api-integration]
constraints: [The CRM API allows 10 writes per second]
non_goals: [Rewriting the sync scheduler, Handling deletes]
done_when: A test that times out the first write and retries it leaves exactly one record
---
Why now: duplicates cost the ops lead about an hour every week.
