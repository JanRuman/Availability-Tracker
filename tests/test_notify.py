from __future__ import annotations

from scrape.notify import find_newly_blocked_dates


def test_finds_date_that_flipped_from_available_to_unavailable():
    old_days = {"2026-08-01": "available", "2026-08-02": "unavailable"}
    new_days = [
        {"date": "2026-08-01", "status": "unavailable"},
        {"date": "2026-08-02", "status": "unavailable"},
    ]
    result = find_newly_blocked_dates(old_days, new_days)
    assert [d["date"] for d in result] == ["2026-08-01"]


def test_ignores_dates_still_available():
    old_days = {"2026-08-01": "available"}
    new_days = [{"date": "2026-08-01", "status": "available"}]
    assert find_newly_blocked_dates(old_days, new_days) == []


def test_ignores_dates_already_blocked_before():
    old_days = {"2026-08-01": "unavailable"}
    new_days = [{"date": "2026-08-01", "status": "unavailable"}]
    assert find_newly_blocked_dates(old_days, new_days) == []


def test_flags_brand_new_date_not_seen_before_as_blocked():
    old_days: dict[str, str] = {}
    new_days = [{"date": "2026-09-01", "status": "unavailable"}]
    result = find_newly_blocked_dates(old_days, new_days)
    assert [d["date"] for d in result] == ["2026-09-01"]
