# Confirmed teacher roster, 2026-09-14

`teachers_20260914.json` transcribes the ten names and roles supplied by the client with matching original portraits. The import clears unsupported demo biographies, tenure, awards and quotations. It preserves IDs of matching real teachers, removes only the explicitly named demo teachers, and clears their program references. It also removes unconfirmed team statistics from page blocks. It does not edit leads, news, prices or schedules.

Portraits are deployed separately, outside Git, to `app/static/uploads/teachers/20260914/` using the filenames in the JSON. No image generation or retouching is involved.

From the application root:

```bash
python scripts/update_teachers_20260914.py
# Review the resulting roster, then apply the authorized content update:
python scripts/update_teachers_20260914.py --apply
```

The default is a rolled-back dry run. Applying checks that all portraits exist and creates a timestamped SQLite backup before the transaction. A repeated apply keeps existing IDs. Unknown existing teachers are retained for manual review.

Maintenance preview uses the existing administrator login at `/login?next=/`. Guests continue to see the maintenance screen. Lead submissions remain disabled, and maintenance responses are non-cacheable and excluded from indexing.
