# Data Connect Schema Migration (Completed)

Migration from the original single-field Entry schema to the full data model was completed on 2026-04-12.

## What was done

### Entry table migration
- `entry_date` (single field) → `entry_date_start` + `entry_date_end` (inclusive date interval)
- Added: `event_start_at`, `event_end_at`, `origin_type`, `status`, `current_revision_id`
- Existing rows were migrated: `entry_date` values copied to both `entry_date_start` and `entry_date_end`
- Old `entry_date` column dropped after data migration

### New tables created
- `entry_revision` — canonical historical content with revision numbering
- `tag` — tag identity with optional type and merge support
- `tag_label` — display text, synonyms, normalization for tags
- `entry_revision_tag` / `entry_tag` — canonical and denormalized tag relations
- `asset` — photo, video, audio, link, file references
- `entry_revision_asset` / `entry_asset` — canonical and denormalized asset relations
- `entry_revision_source_link` — provenance tracking

### Not deployed to Data Connect (Room-only, deferred to Phase 5)
- `ai_requests`, `ai_results`, `ai_feedback`
- `user_preferences`, `user_ai_context`, `user_ai_context_versions`
- `ai_context_snapshots`

## Migration approach

1. Made `entry_date_start`/`entry_date_end` nullable in schema, deployed
2. Ran SQL via `firebase dataconnect:sql:shell` to populate from `entry_date`
3. Changed columns to NOT NULL, deployed again
4. Dropped `entry_date` via sql:shell
5. Final clean deploy

## Commands used

```bash
/opt/homebrew/bin/node /opt/homebrew/bin/npx firebase dataconnect:sql:migrate --force
/opt/homebrew/bin/node /opt/homebrew/bin/npx firebase dataconnect:sdk:generate
/opt/homebrew/bin/node /opt/homebrew/bin/npx firebase deploy --only dataconnect --force
```

Note: default system Node.js (v12) is too old for Firebase CLI. Use homebrew Node via `/opt/homebrew/bin/node`.
