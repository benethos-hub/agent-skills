"""The calculation script of the skill dividend-calendar, rule by rule."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import SKILLS, load_module

SCRIPT = SKILLS / "finance" / "dividend-calendar" / "scripts" / "dividend_calendar.py"
calc = load_module(SCRIPT)

TODAY = "2026-10-20"


def run(
    *positions: dict,
    year: int | None = None,
    rates: dict | None = None,
    today: str = TODAY,
) -> dict:
    document = {
        "today": today,
        "base_currency": "EUR",
        "rates": {"USD": "1.25"} if rates is None else rates,
        "positions": list(positions),
    }
    if year is not None:
        document["year"] = year
    return calc.build(document)


def position(*dividends: tuple[str, str], **fields) -> dict:
    entry = {"name": "Example", "shares": 10, "currency": "USD"}
    entry.update(fields)
    entry["dividends"] = [{"ex_date": d, "amount": a} for d, a in dividends]
    return entry


# A quarterly payer with more than a year of history.
QUARTERLY = (
    ("2025-08-10", "0.50"),
    ("2025-11-10", "0.50"),
    ("2026-02-10", "0.50"),
    ("2026-05-10", "0.50"),
    ("2026-08-10", "0.50"),
)


def kinds(result: dict) -> list[str]:
    return [gap["kind"] for gap in result["gaps"]]


class PayDateTest(unittest.TestCase):
    def test_known_gap_applies_to_every_payment(self):
        calendar = {"ex_date": "2026-08-10", "pay_date": "2026-08-30"}
        result = run(position(*QUARTERLY, calendar=calendar))
        dates = [p["pay_date"] for p in result["payments"]]
        self.assertEqual(dates[0], "2026-03-02")
        self.assertFalse(result["positions"][0]["pay_date_estimated"])
        self.assertNotIn("pay_date_estimated", kinds(result))

    def test_without_calendar_14_days_estimated(self):
        result = run(position(*QUARTERLY))
        self.assertEqual(result["positions"][0]["pay_gap_days"], 14)
        self.assertIn("pay_date_estimated", kinds(result))

    def test_gap_above_70_days_is_not_trusted(self):
        calendar = {"ex_date": "2026-01-10", "pay_date": "2026-04-10"}
        result = run(position(*QUARTERLY, calendar=calendar))
        self.assertEqual(result["positions"][0]["pay_gap_days"], 14)

    def test_december_ex_date_moves_into_january(self):
        result = run(position(("2025-06-12", "0.40"), ("2025-12-18", "0.35")))
        first = result["payments"][0]
        self.assertEqual(first["pay_date"], "2026-01-01")
        self.assertEqual(first["status"], "paid")


class ForecastTest(unittest.TestCase):
    def test_paid_before_the_current_month_forecast_from_it(self):
        result = run(position(*QUARTERLY))
        self.assertEqual(result["paid_months"], list(range(1, 10)))
        status = {p["pay_date"][:7]: p["status"] for p in result["payments"]}
        self.assertEqual(status["2026-08"], "paid")
        self.assertEqual(status["2026-11"], "forecast")

    def test_coming_year_is_forecast_throughout(self):
        result = run(position(*QUARTERLY), year=2027)
        self.assertEqual(result["paid_months"], [])
        self.assertEqual({p["status"] for p in result["payments"]}, {"forecast"})
        self.assertEqual(
            sorted(result["positions"][0]["months"]), ["11", "2", "5", "8"]
        )
        self.assertEqual(result["positions"][0]["frequency"], "quarterly")

    def test_no_growth_and_no_cut(self):
        dividends = (*QUARTERLY[:-1], ("2026-08-10", "0.60"))
        result = run(position(*dividends), year=2027)
        amounts = {p["pay_date"][5:7]: p["per_share"] for p in result["payments"]}
        self.assertEqual(amounts, {"02": "0.5", "05": "0.5", "08": "0.6", "11": "0.5"})

    def test_a_month_twice_counts_only_the_later_year(self):
        # The October payment moved from late to early October.
        dividends = (
            ("2025-04-10", "0.40"),
            ("2025-10-14", "0.40"),
            ("2026-04-10", "0.40"),
            ("2026-10-01", "0.45"),
        )
        result = run(position(*dividends), year=2027)
        october = [p for p in result["payments"] if p["pay_date"][5:7] == "10"]
        self.assertEqual(len(october), 1)
        self.assertEqual(october[0]["per_share"], "0.45")

    def test_payment_falls_out_of_the_reference_period(self):
        result = run(position(("2024-03-01", "1.00"), ("2025-03-01", "1.00")))
        self.assertIn("no_payment_in_reference_period", kinds(result))
        self.assertEqual(result["positions"][0]["months"], {})
        self.assertIsNone(result["positions"][0]["frequency"])

    def test_per_share_shows_six_decimals(self):
        dividends = (
            ("2026-07-02", "0.1"),
            ("2026-08-03", "0.1"),
            ("2026-09-02", "0.2"),
        )
        result = run(position(*dividends))
        gap = next(g for g in result["gaps"] if g["kind"] == "young_fund")
        self.assertEqual(gap["average_per_share"], "0.133333")

    def test_29_february_becomes_28_february(self):
        # Paid on 29 February 2028, the next year has no such day.
        dividends = (("2027-02-15", "1.00"), ("2028-02-15", "1.00"))
        result = run(position(*dividends), year=2029, today="2028-10-20")
        self.assertEqual(result["payments"][0]["pay_date"], "2029-02-28")

    def test_young_fund_runs_on_in_its_rhythm(self):
        dividends = (
            ("2026-06-02", "0.05"),
            ("2026-07-02", "0.07"),
            ("2026-08-03", "0.05"),
            ("2026-09-02", "0.07"),
        )
        result = run(position(*dividends))
        forecast = [p for p in result["payments"] if p["status"] == "forecast"]
        self.assertEqual([p["pay_date"] for p in forecast][0][:7], "2026-10")
        self.assertEqual(len(forecast), 3)
        self.assertEqual({p["per_share"] for p in forecast}, {"0.06"})
        gap = next(g for g in result["gaps"] if g["kind"] == "young_fund")
        self.assertEqual(gap["frequency"], "monthly")

    def test_young_fund_with_one_payment_uses_the_payment(self):
        result = run(position(("2026-05-02", "0.30")), year=2027)
        self.assertNotIn("young_fund", kinds(result))
        self.assertEqual(len(result["payments"]), 1)

    def test_special_dividend_stays_and_is_named(self):
        dividends = (*QUARTERLY[:-1], ("2026-08-10", "1.50"))
        result = run(position(*dividends), year=2027)
        gap = next(
            g for g in result["gaps"] if g["kind"] == "possible_special_dividend"
        )
        self.assertEqual(gap["per_share"], "1.5")
        self.assertIn("1.5", [p["per_share"] for p in result["payments"]])


class CurrencyTest(unittest.TestCase):
    def test_foreign_amount_is_divided_by_the_rate(self):
        result = run(position(*QUARTERLY), year=2027)
        # 0.50 USD x 10 shares / 1.25 = 4.00 EUR per payment.
        self.assertEqual(result["positions"][0]["year"], "16.00")
        self.assertEqual(result["total"]["year"], "16.00")

    def test_pence_are_divided_by_100(self):
        entry = position(*QUARTERLY, currency="GBp")
        result = run(entry, year=2027, rates={"GBP": "0.80"})
        self.assertEqual(result["positions"][0]["currency"], "GBP")
        self.assertEqual(result["payments"][0]["per_share"], "0.005")
        self.assertEqual(result["payments"][0]["amount"], "0.06")

    def test_missing_rate_keeps_the_original_currency(self):
        entry = position(*QUARTERLY, currency="CHF")
        result = run(entry, year=2027)
        self.assertEqual(result["positions"][0]["status"], "unconverted")
        self.assertEqual(result["total"]["year"], "0.00")
        self.assertEqual(result["unconverted"]["CHF"]["year"], "20.00")
        self.assertIn({"kind": "rate_missing", "currency": "CHF"}, result["gaps"])

    def test_base_currency_needs_no_rate(self):
        result = run(position(*QUARTERLY, currency="EUR"), year=2027)
        self.assertEqual(result["total"]["year"], "20.00")
        self.assertNotIn("rate_missing", kinds(result))

    def test_totals_add_up_the_rounded_payments(self):
        # 1/3 USD x 1 share / 1.25 is 0.2666..., rounded 0.27 per payment.
        entry = position(*QUARTERLY[1:], shares=1)
        for d in entry["dividends"]:
            d["amount"] = "0.3333333"
        result = run(entry, year=2027)
        self.assertEqual(result["total"]["year"], "1.08")


class PositionTest(unittest.TestCase):
    def test_without_shares_a_watch_item(self):
        entry = position(*QUARTERLY)
        del entry["shares"]
        result = run(entry, year=2027)
        row = result["positions"][0]
        self.assertEqual((row["status"], row["unit"]), ("watch", "per_share"))
        self.assertEqual(row["year"], "2")
        self.assertEqual(result["total"]["year"], "0.00")
        self.assertIn(
            {"kind": "shares_missing", "positions": ["Example"]}, result["gaps"]
        )

    def test_without_distributions(self):
        result = run(position())
        self.assertEqual(result["positions"][0]["status"], "no_distributions")
        self.assertIn("no_distributions", kinds(result))

    def test_todays_share_count_is_named_once(self):
        result = run(position(*QUARTERLY), position(*QUARTERLY, name="Other"))
        self.assertEqual(kinds(result).count("todays_share_count"), 1)

    def test_coming_year_does_not_name_the_share_count(self):
        result = run(position(*QUARTERLY), year=2027)
        self.assertNotIn("todays_share_count", kinds(result))


class InputTest(unittest.TestCase):
    def test_broken_input_is_rejected(self):
        broken = [
            {"positions": []},
            {"base_currency": "EUR", "rates": {"USD": "0"}},
            {"base_currency": "EUR", "rates": {"USD": "x"}},
            {"base_currency": "EUR", "positions": [{"name": "A"}]},
            {"base_currency": "EUR", "positions": [position(("10.08.2026", "1"))]},
        ]
        for document in broken:
            with self.subTest(document=document):
                with self.assertRaises(calc.InputError):
                    calc.build(document)

    def test_command_line_reads_a_file(self):
        document = {"today": TODAY, "base_currency": "EUR", "positions": []}
        path = Path(tempfile.mkdtemp()) / "input.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        out = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        with mock.patch.object(sys, "argv", ["x", str(path)]):
            with contextlib.redirect_stdout(out):
                calc.main()
        out.seek(0)
        self.assertEqual(json.loads(out.read())["year"], 2026)

    def test_command_line_exits_on_broken_input(self):
        with (
            mock.patch.object(sys, "argv", ["x"]),
            mock.patch.object(sys, "stdin", io.StringIO("{}")),
            contextlib.redirect_stderr(io.StringIO()) as err,
        ):
            with self.assertRaises(SystemExit) as stop:
                calc.main()
        self.assertEqual(stop.exception.code, 2)
        self.assertIn("base_currency", err.getvalue())


if __name__ == "__main__":
    unittest.main()
