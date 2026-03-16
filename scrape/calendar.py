from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from bs4 import BeautifulSoup

MONTHS_SK = {
    "január": 1,
    "február": 2,
    "marec": 3,
    "apríl": 4,
    "máj": 5,
    "jún": 6,
    "júl": 7,
    "august": 8,
    "september": 9,
    "október": 10,
    "november": 11,
    "december": 12,
}


@dataclass(frozen=True)
class DayAvailability:
    date: str  # YYYY-MM-DD
    status: str  # available|unavailable
    price_eur: int | None


def _normalize_space(s: str) -> str:
    return " ".join(s.split())


def _find_month_headers(text: str) -> list[tuple[int, int]]:
    """
    Returns list of (month, year) in the order they appear in the calendar text.
    Example: "Marec 2026", "Apríl 2026", ...
    """
    # Match Slovak month names + 4-digit year
    pattern = re.compile(
        r"\b("
        + "|".join(re.escape(m.capitalize()) for m in MONTHS_SK.keys())
        + r")\s+(\d{4})\b"
    )

    months: list[tuple[int, int]] = []
    for m, y in pattern.findall(text):
        month_num = MONTHS_SK[m.lower()]
        months.append((month_num, int(y)))
    return months


def _iter_tokens_for_month_block(text: str, month_name_cap: str, year: int, next_header: str | None) -> str:
    start = text.find(f"{month_name_cap} {year}")
    if start < 0:
        return ""
    if next_header:
        end = text.find(next_header, start + 1)
        if end > start:
            return text[start:end]
    return text[start:]


def parse_calendar_days(html: str) -> list[DayAvailability]:
    """
    Parses the calendar into per-day availability.

    Primary heuristic:
    - if a day cell shows a price like '82 EUR' then status=available
    - if it shows only a day number (no EUR) then status=unavailable

    This is implemented using the page's extracted text as a stable fallback.
    """
    soup = BeautifulSoup(html, "html.parser")
    full_text = _normalize_space(soup.get_text(" ", strip=True))

    month_headers = _find_month_headers(full_text)
    if not month_headers:
        return []

    # Reconstruct header strings in the same capitalization as site text (first letter uppercase).
    header_strings: list[str] = []
    for month_num, year in month_headers:
        month_name_cap = next(k.capitalize() for k, v in MONTHS_SK.items() if v == month_num)
        header_strings.append(f"{month_name_cap} {year}")

    results: list[DayAvailability] = []

    # For each month block: scan sequentially for either "<day><price> EUR" or standalone "<day>".
    # We treat standalone day numbers as unavailable *only if* that day didn't already appear with a price.
    for idx, ((month_num, year), header) in enumerate(zip(month_headers, header_strings)):
        next_header = header_strings[idx + 1] if idx + 1 < len(header_strings) else None
        block = _iter_tokens_for_month_block(full_text, header.split()[0], year, next_header)
        if not block:
            continue

        # Remove weekday headings that may contain short tokens that confuse parsing.
        # (Pon Uto Str Štv Pia Sob Ned)
        block = re.sub(r"\b(Pon|Uto|Str|Štv|Stv|Pia|Sob|Ned)\b", " ", block)
        block = _normalize_space(block)

        # Extract sequences: either "DD 82 EUR" or "DD"
        # Note: some leading/trailing calendar layout numbers can appear; we filter by valid day range.
        priced = {}
        for m in re.finditer(r"\b(\d{1,2})\s+(\d{1,4})\s+EUR\b", block):
            day = int(m.group(1))
            price = int(m.group(2))
            if 1 <= day <= 31:
                priced[day] = price

        # Standalone days: day numbers not followed by EUR within a short window.
        standalone_days: set[int] = set()
        for m in re.finditer(r"\b(\d{1,2})\b", block):
            day = int(m.group(1))
            if not (1 <= day <= 31):
                continue
            standalone_days.add(day)

        for day in sorted(standalone_days):
            d = date(year, month_num, day)
            if day in priced:
                results.append(
                    DayAvailability(
                        date=d.isoformat(),
                        status="available",
                        price_eur=priced[day],
                    )
                )
            else:
                results.append(
                    DayAvailability(
                        date=d.isoformat(),
                        status="unavailable",
                        price_eur=None,
                    )
                )

    # Deduplicate (in case the text contains repeated blocks); keep last occurrence.
    by_date: dict[str, DayAvailability] = {}
    for r in results:
        by_date[r.date] = r
    return [by_date[k] for k in sorted(by_date.keys())]

