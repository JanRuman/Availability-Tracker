# Praga availability tracker — todo

## Checklist

- [ ] Repo scaffold: `requirements.txt`, `README.md`, folder layout
- [ ] Scraper MVP: discover apartments + parse calendar + write snapshots
- [ ] GitHub Actions: daily schedule + commit snapshots
- [ ] Viewer: static UI for latest + historical snapshots
- [ ] Verification: confirm parsing on real pages, document edge cases
- [ ] Polite scraping: rate limiting, stable UA, retries/backoff

## Review notes (fill as you go)

- **Parsing correctness**:
  - Expected: days with `EUR` are available
  - Expected: days without `EUR` are unavailable/booked
  - Verify month/year alignment across the multi-month calendar
- **Operational**:
  - Daily run produces one snapshot per day
  - UI can load any prior snapshot date and render without errors

## How to verify (without local Python)

If you don’t have Python installed locally, use GitHub Actions for verification:

- Push repo to GitHub
- Run workflow manually: Actions → `scrape` → Run workflow
- Confirm `data/latest.json`, `data/index.json`, and a new `data/snapshots/<today>.json` were committed

