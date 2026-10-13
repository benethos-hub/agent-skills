---
name: dividend-calendar
description: "Builds a dividend calendar for a portfolio, for the current or a coming year, from each position's dividend history and with fixed, traceable calculation rules. Past months show what was paid, coming months the forecast, and every gap in the data is named. Use this skill whenever someone asks for a dividend calendar, for distributions per month, for a year's dividend income, or when each position pays, also when they only hand over a list of holdings with share counts. Answers in the user's language."
license: MIT
---

# Dividend calendar

## What this skill is for

Anyone who receives dividends wants to know what arrives when. This skill turns that into a calendar: an amount per position and month, the totals below, and an honest list of what is estimated.

Two attitudes carry everything else:

**First: rules, not judgement.** The calendar is calculated by fixed rules, not by feel. No growth someone considers likely, no cut someone fears. Whoever has the same data must arrive at the same numbers. Only then can every number be checked.

**Second: gaps belong in the answer.** The data has gaps, and every future value is a forecast. An estimated pay date, a missing exchange rate or a position without history is named, not covered up. A calendar is a planning tool, not an account statement.

---

## Language of the answer

Write the answer in the language the user writes in. Headings, column names, status words and the disclaimer follow that language too. Format numbers, dates and currencies by the user's conventions, for German a decimal comma and a thousands point (1.234,56 €) and dates as 13.10.2026.

---

## Input

Needed:

- **Positions:** for each one an ISIN, a ticker or a name, plus the share count.
- **Year:** the current year if nothing is said.
- **Base currency:** the one the user names. Otherwise the currency that fits the user's language and country, and EUR when in doubt. Say which one was used.

A position without a share count appears as a watch item, with amounts per share and without a total. Do not guess and do not ask as long as the rest can be calculated. Name the missing share counts once at the end.

German WKNs cannot be resolved by the usual data sources. In that case ask for an ISIN, a ticker or a name.

The share counts stay in the conversation. No data tool needs them, and none receives them. Only symbols and ISINs are queried.

---

## Procedure

### Step 1: Identify every instrument

Resolve every ISIN and every name through the search function of the connected market-data MCP, never from memory. Take over the resolved symbol.

If an ETF's ISIN resolves to a foreign listing, London in US dollars for example, that is not an error. The distribution per share is the same for all listings and is declared in the fund currency. Name the listing in the answer.

### Step 2: Fetch the data, all in parallel

Market data comes from the connected data-provider MCP, not from memory and not from a web search. The usual case is a Yahoo Finance MCP with `search`, `get_dividends`, `get_calendar` and `get_quote`. With another provider the tools have other names.

| Need | What for |
|---|---|
| Dividend history per position, date and amount per share | the basis of every number |
| Corporate calendar with ex-date and pay date | the gap between ex-date and pay date |
| Currency of the listing | conversion |
| Exchange rate of each foreign currency to the base currency | conversion |

The corporate calendar exists for single stocks only. Skip the call for ETFs, funds and crypto.

Put all calls into one parallel block. On a rate limit, wait briefly and repeat the same call.

### Step 3: Calculate

Every rule here is fixed. Deviations only on explicit request, and then reported separately as a scenario (see below).

**Pay date.** The dividend history is dated by the ex-date, the pay date is not in it. If the corporate calendar gives the ex-date and the pay date of the same payment and they are 0 to 70 days apart, that gap applies to every payment of the position. Otherwise 14 days apply, and the pay date is marked as estimated. The pay date is the ex-date plus the gap. It decides which month a payment falls in.

**Reference period.** The basis is the payments whose pay date lies within the 365 days before today. If a pay date has moved forward, the reference period can hold the same calendar month twice, once from last year and once from this year. Then only the payments of the later year count for that month. Otherwise one payment enters the forecast twice.

**Frequency.** The number of distinct pay months in the reference period: 1 means annual, 2 semi-annual, 4 quarterly, 12 monthly, anything else irregular. The frequency is only reported, the calculation uses the payments themselves.

**Forecast.** Every payment of the reference period recurs in the same month at the same amount. No growth, no cut, no estimate of one's own.

**Young funds.** If the history goes back less than 360 days, the frequency follows from the median gap between payments: up to 45 days monthly, up to 135 days quarterly, up to 225 days semi-annual, up to 430 days annual. The amount per payment is the average of the payments so far. The months are carried forward in that rhythm from the last payment. Mark the position as extrapolated in the list of gaps.

**Paid or forecast.** In the current year, the months before the current month show what was actually paid: the payments with a pay date in that month times today's share count. From the current month on, the forecast applies. A coming year is forecast throughout.

**Currency.** Amount per share times share count in the distribution currency, then converted to the base currency at today's rate. If a rate is missing, the amount stays in its original currency, is marked, and does not enter the base-currency total. Currencies are never added without being converted.

**Gross.** All amounts before taxes. Withholding tax and the user's own taxes on income, in Germany for example Abgeltungsteuer, solidarity surcharge and church tax, are not deducted, not estimated and not offset.

**No distributions.** A position without a payment in its history appears with "no distributions in the data". That can be an accumulating fund, a stock without a dividend or a gap in the data. Do not decide which case it is when the data does not say. Crypto pays nothing.

**Conspicuous payment.** If a payment in the reference period is one and a half times the other payments of the same position or more, it stays in the calculation. It is named in the list of gaps as a possible special dividend, with the note that it lifts the forecast in case it does not recur.

### Step 4: Write

Structure below.

---

## Output structure

The skeleton in English. Translate every heading, column and phrase into the user's language.

```markdown
## Dividend calendar <year>

As of <date>, amounts in <base currency>, gross. <Paid up to <month>, forecast from <month> on.>
Rates: 1 EUR = <x> USD, …

<One or two sentences: annual total, strongest month, the portfolio's rhythm.>

| Position | Jan | Feb | … | Dec | Year |
|---|---|---|---|---|---|
| <Name>* | … | … | … | … | … |
| **Total** | … | … | … | … | **…** |

Forecast values in italics. * Pay date estimated.

### Payments in detail

| Pay date | Position | Per share | Shares | Amount | Status |
|---|---|---|---|---|---|
| <date> (estimated) | <name> | <amount, original currency> | <n> | <amount, base currency> | paid / forecast |

### Gaps and assumptions

- <Where a pay date is estimated, and why>
- <Where data or a rate is missing>
- <Possible special dividends, young funds, positions without distributions>
- <Missing share counts>

---

<Disclaimer, two sentences>
```

Leave out the payments in detail when only the overview was asked for.

### Scenario with growth

Only on explicit request. Then a column or table of its own, labelled scenario, never mixed into the forecast. Its basis is the last change of each position's annual dividend, calculated from the history and shown with its derivation. The scenario is a calculation under an assumption, not a forecast.

---

## Language and style

Plain and factual, no sales tone, in the user's language.

- **No semicolons.** Full stop or comma.
- Simple sentences.
- Money with two decimals, and always with its currency.
- No emojis.

### Disclaimer

Gaps and assumptions stand in their own list, right next to the numbers. Separate from that, the disclaimer comes at the very end, and it is **two sentences**: the data can be incomplete and delayed, and every future value is a forecast without guarantee. No investment and no tax advice.

---

## What this skill does not do

No tax calculation, no investment advice, no recommendation to buy, hold or sell. No access to a depot or a broker, no orders.

Do not pretend to know what is not known. An estimated pay date is marked as estimated, a missing number as missing. An honest gap is better than a plausible invention.

---

# Appendix: data traps

The examples come from a Yahoo Finance MCP. The traps themselves exist with every bulk data provider.

## 1. Ex-date instead of pay date

The dividend history is dated by the ex-date. The pay date is often missing from the corporate calendar too, even for large single stocks. For such a position the 14-day estimate applies.

## 2. ETFs without a calendar

There is no corporate calendar for ETFs and funds. Their pay date is always estimated and can slip into the following month. Real case: the December distribution of a world ETF with its ex-date on 18 December lands on 1 January with the estimate. That belongs in the list of gaps.

## 3. The last instead of the next ex-date

The corporate calendar often still shows the last ex-date until the next one is announced. An ex-date in the past is not an upcoming date, only the source of the gap to the pay date.

## 4. Pence instead of pounds

London listings often trade in pence (GBp), not pounds (GBP), and their dividends come in pence as well. Divide an amount in GBp by 100 before converting.

## 5. Direction of exchange rates

`EURUSD=X` gives how many US dollars one euro costs. A dollar amount is therefore divided by this rate, not multiplied. The same holds for `EURGBP=X`, `EURCHF=X` and the others.

## 6. Splits

The dividend history is restated to today's share count after splits. A dividend of 0.80 USD paid before a 4-for-1 split appears as 0.20 USD in the history afterwards. With today's share count that fits. With an old count from before a split it does not.

## 7. Today's share count

In the current year, what was paid is also calculated with today's share count. Whoever bought or sold during the year sees a different amount for the months before than on the account. Mention it once in the list of gaps.

## 8. Quick check before sending

1. **Every position resolved?** Through the search, not from memory.
2. **Every pay date explained?** Known gap or marked as estimated.
3. **No currencies mixed?** Every total in one currency, every rate named.
4. **List of gaps complete?** Estimated pay dates, missing data, special dividends, missing share counts.
5. **Answer in the user's language?** Headings, columns and number format included.
