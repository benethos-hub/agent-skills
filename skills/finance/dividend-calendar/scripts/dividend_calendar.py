# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Calculate a dividend calendar by the fixed rules of the skill.

The agent fetches the data, this script does the arithmetic, and the agent
writes the answer in the user's language. The script reads one JSON document
from the file named as its argument, or from stdin, and writes the calendar
as JSON to stdout. Standard library only, Python 3.11 or newer.

Input:

    {
      "today": "2026-10-20",          optional, the system date otherwise
      "year": 2026,                   optional, the year of today otherwise
      "base_currency": "EUR",
      "rates": {"USD": 1.16},         units of a currency per 1 base unit,
                                      as EURUSD=X gives them
      "positions": [
        {
          "name": "Example Corp",
          "symbol": "EXM",
          "shares": 25,               optional, without it a watch item
          "currency": "USD",          currency of the distributions, GBp too
          "dividends": [{"ex_date": "2026-08-10", "amount": 0.26}],
          "calendar": {"ex_date": "2026-08-10", "pay_date": "2026-08-28"}
        }
      ]
    }

"calendar" is optional and exists for single stocks only. Amounts are taken
as given, so pass them as strings or numbers exactly as the data source
reports them.

Output: the paid and the forecast months, per position its months and year in
the base currency ("unit"), every payment with its status "paid" or
"forecast", the total in the base currency, amounts without a rate under
"unconverted", and the gaps. A position's status is "ok", "watch" (no share
count, amounts per share), "unconverted" (no rate) or "no_distributions".
Each gap has a "kind":

    pay_date_estimated              ex-date plus 14 days
    young_fund                      less than 360 days of history, extrapolated
    possible_special_dividend       1.5 times the other payments or more
    no_distributions                no payment in the history
    no_payment_in_reference_period  payments, but none in the last 365 days
    rate_missing                    amounts stay in their own currency
    shares_missing                  watch items without a total
    todays_share_count              paid months use today's share count

Amounts carry two decimals, amounts per share up to six.
"""

from __future__ import annotations

import calendar
import json
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from statistics import median
from typing import Any

DEFAULT_GAP_DAYS = 14
MAX_GAP_DAYS = 70
WINDOW_DAYS = 365
YOUNG_FUND_DAYS = 360
SPECIAL_FACTOR = Decimal("1.5")
CENT = Decimal("0.01")
PER_SHARE = Decimal("0.000001")

# Median gap between payments in days, and the payments per year it means.
RHYTHMS = ((45, 12), (135, 4), (225, 2), (430, 1))
FREQUENCIES = {1: "annual", 2: "semi-annual", 4: "quarterly", 12: "monthly"}
# Listings that quote in a minor unit: the major currency and the divisor.
MINOR_UNITS = {
    "GBp": ("GBP", 100),
    "GBX": ("GBP", 100),
    "ZAc": ("ZAR", 100),
    "ILA": ("ILS", 100),
}


class InputError(ValueError):
    """The input does not hold what the calculation needs."""


@dataclass(frozen=True)
class Payment:
    pay_date: date
    per_share: Decimal


def parse_date(value: Any, what: str) -> date:
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        raise InputError(f"{what}: {value!r} is not a date") from None


def parse_number(value: Any, what: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise InputError(f"{what}: {value!r} is not a number") from None
    if not number.is_finite():
        raise InputError(f"{what}: {value!r} is not a number")
    return number


def plain(value: Decimal) -> str:
    """A number with up to six decimals, without exponent or trailing zeros."""
    return f"{value.quantize(PER_SHARE, ROUND_HALF_UP).normalize():f}"


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, ROUND_HALF_UP)


def plain_money(value: Decimal, shares: Decimal | None) -> str:
    """Amounts with two decimals, amounts per share as they are."""
    return plain(value) if shares is None else str(cents(value))


def average(payments: list[Payment]) -> Decimal:
    """The average amount per share, unrounded."""
    return sum((p.per_share for p in payments), Decimal(0)) / len(payments)


def in_year(day: date, year: int) -> date:
    """The same day in another year, 29 February becomes 28 February."""
    last = calendar.monthrange(year, day.month)[1]
    return date(year, day.month, min(day.day, last))


def add_months(day: date, months: int) -> date:
    year, month = divmod(day.year * 12 + day.month - 1 + months, 12)
    last = calendar.monthrange(year, month + 1)[1]
    return date(year, month + 1, min(day.day, last))


def pay_gap(position: dict[str, Any]) -> tuple[int, bool]:
    """Days from ex-date to pay date, and whether they are estimated."""
    entry = position.get("calendar") or {}
    if entry.get("ex_date") and entry.get("pay_date"):
        days = (
            parse_date(entry["pay_date"], "calendar pay_date")
            - parse_date(entry["ex_date"], "calendar ex_date")
        ).days
        if 0 <= days <= MAX_GAP_DAYS:
            return days, False
    return DEFAULT_GAP_DAYS, True


def reference_period(payments: list[Payment], today: date) -> list[Payment]:
    """The payments of the 365 days before today, one year per calendar month."""
    start = today - timedelta(days=WINDOW_DAYS)
    recent = [p for p in payments if start < p.pay_date <= today]
    latest: dict[int, int] = {}
    for p in recent:
        latest[p.pay_date.month] = max(latest.get(p.pay_date.month, 0), p.pay_date.year)
    return [p for p in recent if p.pay_date.year == latest[p.pay_date.month]]


def young_rhythm(payments: list[Payment], today: date) -> int | None:
    """Payments per year of a fund with less than 360 days of history."""
    if not payments or (today - payments[0].pay_date).days >= YOUNG_FUND_DAYS:
        return None
    gaps = [
        (b.pay_date - a.pay_date).days
        for a, b in zip(payments, payments[1:], strict=False)
        if b.pay_date > a.pay_date
    ]
    if not gaps:
        return None
    middle = median(gaps)
    for limit, per_year in RHYTHMS:
        if middle <= limit:
            return per_year
    return None


def forecast(
    payments: list[Payment],
    reference: list[Payment],
    rhythm: int | None,
    year: int,
) -> list[Payment]:
    """The payments of the year if everything recurs as it is."""
    if rhythm is None:
        return [Payment(in_year(p.pay_date, year), p.per_share) for p in reference]
    per_share = average(payments)
    last = payments[-1].pay_date
    step = 12 // rhythm
    months_away = (year - last.year) * 12
    first = (months_away - 12) // step
    dates = (add_months(last, k * step) for k in range(first, first + 3 * rhythm))
    return [Payment(d, per_share) for d in dates if d.year == year]


def is_special(payment: Payment, reference: list[Payment]) -> bool:
    others = [p.per_share for p in reference if p is not payment]
    return bool(others) and payment.per_share >= SPECIAL_FACTOR * median(others)


def build(document: dict[str, Any]) -> dict[str, Any]:
    today = (
        parse_date(document["today"], "today")
        if document.get("today")
        else date.today()
    )
    year = int(document.get("year") or today.year)
    base = document.get("base_currency")
    if not base:
        raise InputError("base_currency is missing")
    rates = {
        str(k): parse_number(v, f"rate {k}")
        for k, v in (document.get("rates") or {}).items()
    }
    rates[base] = Decimal(1)
    if any(rate <= 0 for rate in rates.values()):
        raise InputError("every rate must be above zero")

    paid_months = [m for m in range(1, 13) if (year, m) < (today.year, today.month)]
    forecast_months = [m for m in range(1, 13) if m not in paid_months]

    positions_out: list[dict[str, Any]] = []
    payments_out: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    totals: dict[int, Decimal] = {}
    unconverted: dict[str, dict[int, Decimal]] = {}
    missing_rates: set[str] = set()
    missing_shares: list[str] = []
    anything_paid = False

    for index, position in enumerate(document.get("positions") or []):
        name = str(position.get("name") or position.get("symbol") or f"#{index + 1}")
        listing_currency = position.get("currency")
        if not listing_currency:
            raise InputError(f"{name}: currency is missing")
        currency, divisor = MINOR_UNITS.get(listing_currency, (listing_currency, 1))
        shares = (
            parse_number(position["shares"], f"{name}: shares")
            if position.get("shares") is not None
            else None
        )
        gap_days, estimated = pay_gap(position)

        payments = sorted(
            (
                Payment(
                    parse_date(d.get("ex_date"), f"{name}: ex_date")
                    + timedelta(days=gap_days),
                    parse_number(d.get("amount"), f"{name}: amount") / divisor,
                )
                for d in position.get("dividends") or []
            ),
            key=lambda p: p.pay_date,
        )
        payments = [p for p in payments if p.per_share > 0]

        entry: dict[str, Any] = {
            "name": name,
            "symbol": position.get("symbol"),
            "shares": plain(shares) if shares is not None else None,
            "currency": currency,
            "listing_currency": listing_currency,
            "pay_gap_days": gap_days,
            "pay_date_estimated": estimated,
        }
        positions_out.append(entry)
        if shares is None:
            missing_shares.append(name)

        if not payments:
            entry.update(
                status="no_distributions", frequency=None, months={}, year=None
            )
            gaps.append({"kind": "no_distributions", "position": name})
            continue

        reference = reference_period(payments, today)
        rhythm = young_rhythm(payments, today)
        frequency: str | None
        if rhythm is not None:
            frequency = FREQUENCIES[rhythm]
            gaps.append(
                {
                    "kind": "young_fund",
                    "position": name,
                    "frequency": frequency,
                    "average_per_share": plain(average(payments)),
                    "currency": currency,
                }
            )
        else:
            months_paid = len({p.pay_date.month for p in reference})
            frequency = FREQUENCIES.get(months_paid, "irregular") if reference else None
            if not reference:
                gaps.append(
                    {
                        "kind": "no_payment_in_reference_period",
                        "position": name,
                        "last_pay_date": payments[-1].pay_date.isoformat(),
                    }
                )
        for p in reference:
            if is_special(p, reference):
                gaps.append(
                    {
                        "kind": "possible_special_dividend",
                        "position": name,
                        "pay_date": p.pay_date.isoformat(),
                        "per_share": plain(p.per_share),
                        "currency": currency,
                    }
                )
        if estimated:
            gaps.append({"kind": "pay_date_estimated", "position": name})

        rows = [
            (p, "paid")
            for p in payments
            if p.pay_date.year == year and p.pay_date.month in paid_months
        ] + [
            (p, "forecast")
            for p in forecast(payments, reference, rhythm, year)
            if p.pay_date.month in forecast_months
        ]
        rows.sort(key=lambda row: row[0].pay_date)

        rate = rates.get(currency)
        if rate is None and shares is not None and rows:
            missing_rates.add(currency)
        months: dict[int, Decimal] = {}
        for p, status in rows:
            amount = None if shares is None else p.per_share * shares
            if amount is not None and rate is not None:
                amount = cents(amount / rate)
            elif amount is not None:
                amount = cents(amount)
            if status == "paid" and amount:
                anything_paid = True
            months[p.pay_date.month] = months.get(p.pay_date.month, Decimal(0)) + (
                amount if amount is not None else p.per_share
            )
            payments_out.append(
                {
                    "pay_date": p.pay_date.isoformat(),
                    "pay_date_estimated": estimated,
                    "position": name,
                    "per_share": plain(p.per_share),
                    "currency": currency,
                    "shares": entry["shares"],
                    "amount": str(amount) if amount is not None else None,
                    "amount_currency": (
                        None
                        if amount is None
                        else base
                        if rate is not None
                        else currency
                    ),
                    "status": status,
                }
            )

        if shares is None:
            status_word = "watch"
            unit = "per_share"
        elif rate is None:
            status_word = "unconverted"
            unit = currency
            bucket = unconverted.setdefault(currency, {})
            for m, v in months.items():
                bucket[m] = bucket.get(m, Decimal(0)) + v
        else:
            status_word = "ok"
            unit = base
            for m, v in months.items():
                totals[m] = totals.get(m, Decimal(0)) + v
        entry.update(
            status=status_word,
            frequency=frequency,
            unit=unit,
            months={str(m): plain_money(v, shares) for m, v in sorted(months.items())},
            year=plain_money(sum(months.values(), Decimal(0)), shares),
        )

    for currency in sorted(missing_rates):
        gaps.append({"kind": "rate_missing", "currency": currency})
    if missing_shares:
        gaps.append({"kind": "shares_missing", "positions": missing_shares})
    if anything_paid:
        gaps.append({"kind": "todays_share_count"})

    payments_out.sort(key=lambda p: (p["pay_date"], p["position"]))
    return {
        "today": today.isoformat(),
        "year": year,
        "base_currency": base,
        "rates": {k: plain(v) for k, v in sorted(rates.items()) if k != base},
        "paid_months": paid_months,
        "forecast_months": forecast_months,
        "positions": positions_out,
        "total": {
            "months": {str(m): str(v) for m, v in sorted(totals.items())},
            "year": str(sum(totals.values(), Decimal("0.00"))),
        },
        "unconverted": {
            currency: {
                "months": {str(m): str(v) for m, v in sorted(months.items())},
                "year": str(sum(months.values(), Decimal("0.00"))),
            }
            for currency, months in sorted(unconverted.items())
        },
        "payments": payments_out,
        "gaps": gaps,
    }


def main() -> None:
    try:
        if len(sys.argv) > 1:
            text = Path(sys.argv[1]).read_text(encoding="utf-8")
        else:
            text = sys.stdin.read()
        result = build(json.loads(text))
    except (OSError, json.JSONDecodeError, InputError) as error:
        print(f"dividend_calendar: {error}", file=sys.stderr)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
