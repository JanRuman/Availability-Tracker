# Praga availability tracker

Scrapes apartment availability calendars from [`praga.at`](https://praga.at/apartmany/) daily and stores snapshots so you can view current and past availability.

## What it does

- Discovers apartment pages from the listing.
- Parses the availability calendar on each apartment page.
- Writes a daily snapshot to `data/snapshots/YYYY-MM-DD.json`.
- Updates `data/latest.json` to match the newest snapshot.

## Quick start (local)

Prerequisite: install **Python 3.11+** (so `python` and `pip` are available in your terminal).

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
set APT_LIMIT=2
python -m scrape.run
```

Outputs:

- `data/latest.json`
- `data/snapshots/<today>.json`

## Publish a viewer (GitHub Pages)

This repo includes a static viewer in `viewer/` that reads:

- `data/latest.json` (default)
- `data/snapshots/<date>.json` (when you choose a historical snapshot)

To publish on GitHub Pages:

1. Push the repository to GitHub.
2. In GitHub repo settings, enable Pages and set the source to the `main` branch and `/viewer` folder (or use Pages from Actions if you prefer).

## Daily scraping (GitHub Actions)

`.github/workflows/scrape.yml` runs daily and commits updated `data/` back to the repo.

Notes:

- The workflow requires `contents: write` permissions (set in the workflow).
- If you want to avoid committing on days with no changes, the workflow checks for changes before committing.
- First-time verification: after pushing to GitHub, run the workflow via **Actions → scrape → Run workflow**, then confirm it created/committed:
  - `data/latest.json`
  - `data/index.json`
  - `data/snapshots/YYYY-MM-DD.json`

## Polite scraping (don’t get blocked)

- Runs **at most once per day** in GitHub Actions.
- Uses a common browser User-Agent, small randomized delays, and retry/backoff on transient errors.
- Do not increase frequency aggressively; that’s the main thing that gets scrapers blocked.

## Interpretation of availability

The calendar typically shows a per-night price like `82 EUR` on *available* days. Days that show only a day number (no `EUR`) are treated as *unavailable/booked*.

If the site changes its markup, you may need to update `scrape/calendar.py`.

