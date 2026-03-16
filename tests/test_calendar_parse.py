from __future__ import annotations

from scrape.calendar import parse_calendar_days


def test_parse_calendar_days_basic_availability():
    html = """
    <html>
      <body>
        <h2>Dostupnosť online - Apartmán - štúdio 2</h2>
        <div>
          <h3>Marec 2026</h3>
          <div>Pon Uto Str Štv Pia Sob Ned</div>
          <div>
            1 120 EUR 2 120 EUR 3 120 EUR 4 120 EUR 5 120 EUR 6 120 EUR 7 120 EUR 8 120 EUR
            9 120 EUR 10 120 EUR 11 12 120 EUR 13 120 EUR 14 120 EUR 15
          </div>
        </div>
      </body>
    </html>
    """
    days = parse_calendar_days(html)
    by_date = {d.date: d for d in days}

    assert by_date["2026-03-01"].status == "available"
    assert by_date["2026-03-01"].price_eur == 120

    # Days without an EUR price are treated as unavailable
    assert by_date["2026-03-11"].status == "unavailable"
    assert by_date["2026-03-11"].price_eur is None

    assert by_date["2026-03-15"].status == "unavailable"
    assert by_date["2026-03-15"].price_eur is None

