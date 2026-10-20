---
name: asset-analysis
description: "Writes a structured analysis of a single security from current price, fundamental and news data, with an assessment for the short, medium and long term. Use this skill whenever an ISIN, a ticker or a security's name comes up, or when someone asks about a stock, an ETF, a cryptocurrency, a price target, quarterly figures, analyst opinions, a valuation or a comparison of several securities, also when they only ask in passing what is going on with a security, even when the word analysis is never used. Not for a dividend calendar or a portfolio's distributions per month. Answers in the user's language."
license: MIT
---

# Asset analysis

## What this skill is for

Anyone can look up prices and ratios. An analysis earns its value where someone calculates the number that is **not** in the data set, and says what the numbers mean and what they do not mean.

So this skill does not copy data. It puts it in context, for an experienced private investor who makes their own decisions and needs clean facts plus an honest assessment.

Two attitudes carry everything else:

**First: distrust your own data source.** Most serious errors in a security analysis come from a number that meant something other than assumed, not from wrong reasoning. A stale share count, a negative P/E read as a multiple, an ISIN that belongs to another company than expected.

**Second: narrative is not evidence.** Companies announce pipelines, letters of intent and partnerships. The accounts show revenue and cash outflow. Where the two drift apart, that gap is the analysis.

## Language of the answer

Write the answer in the language the user writes in, headings and disclaimer included. Format numbers, dates and currencies by the user's conventions, for German a decimal comma and a thousands point.

## Procedure

### Step 1: Identify the instrument

Never assign an ISIN from memory. ISINs of different issuers can differ in only a few characters, and a mix-up is expensive.

Always resolve the ISIN or the name through the search function of the connected market-data MCP first and take over the result. If the resolved name could surprise, because it resembles a better-known company, put that at the very top of the answer.

German WKNs cannot be resolved by the usual data sources. In that case ask for an ISIN, a ticker or a name.

### Step 2: Fetch the data, all in parallel

**Current beats convenient.** Prices, ratios and dates change daily. None of them may come from memory. When two sources disagree, the one with the later date wins, and the date goes into the text.

Market data comes from the connected data-provider MCP. The usual case is a Yahoo Finance MCP with `search`, `get_quote`, `get_company_info`, `get_recommendations`, `get_calendar`, `get_news`, `get_financials`, `get_shares`, `get_estimates`, `get_history`, `get_options` and `get_fund_data`. With another provider the tools have other names. So the table describes the need, not the call, and everything goes into **one** parallel block:

| Need | What for |
|---|---|
| Price, previous close, day range, 52-week range, moving averages, market cap | facts and price level |
| Company profile with sector, valuation ratios, beta, dividend yield | character and first valuation |
| Analyst ratings and price targets with mean, median and range | analyst picture and distance calculation |
| Calendar with the next report and dividend dates | short term |
| Headlines | entry into the news, never enough on its own |
| Revenue and earnings over several years | multi-year view |
| Share count over time | dilution and check of the market cap |

Depending on the case also: consensus estimates, price history (required after a conspicuous move), the option chain before quarterly figures, fund data for ETFs.

**Do not fetch blindly.** For an ETF, ratings, calendar and quarterly figures come back empty. For crypto only price and history remain. The full set pays off for single stocks.

**Then search the web, if the agent can.** The provider's headlines regularly lag and miss exactly the news that moves the price. After a conspicuous move, fetch one month of price history, find the day of the break and search for that date. A price jump without a named trigger is a gap in the analysis. Without a web search, say so in the answer.

If no market-data MCP is connected, say so openly and build the analysis from a web search, with a sentence at the top that these numbers are harder to check and often older.

On a rate limit, wait briefly and repeat the same call.

### Step 3: Calculate yourself

This step separates an analysis from a data copy. At least two or three of these belong in every full analysis, each with its derivation shown:

| Calculation | When | How |
|---|---|---|
| Distance to analyst targets | always | price against the mean **and** against the highest and lowest target |
| Price to sales | when there is no meaningful P/E | market cap divided by annualised quarterly revenue |
| Share count check | always | market cap divided by price, against the latest reported count |
| Cash runway | loss-making companies | cash divided by operating cash outflow per quarter, capital spending deducted separately |
| Valuation expansion or compression | when price and earnings diverge | price change against earnings change over the same period |
| Net asset value per share | holdings and treasury vehicles | assets minus senior claims, against the market cap |
| Implied move | before quarterly figures | at-the-money straddle from the option chain, divided by the price |

### The basis of every ratio

A P/E is not one number. There are at least three: on the last four reported quarters, on the current fiscal year and on next year's consensus. For a growth stock they can lie far apart. Four rules belong together:

- **Always name the basis.** Not "P/E 38" but "P/E 38 on the consensus for next year".
- **Do not mix bases within one calculation.** A change in valuation over time needs the same basis at both ends, or it measures the switch of basis.
- **One source per ratio.** Numerator and denominator from different providers give a number that exists nowhere.
- **Your own calculation beats the ready-made field.** A provider's ratio has an undocumented time window. Where your calculation from reported quarters differs, use your own, name the difference and both bases.

The same holds for price to sales, enterprise value to sales and dividend yield.

### Always: the multi-year view

One quarter says little. Two short series cost almost nothing and put everything else in context, each as a compact table:

- **Revenue and earnings over three to four years.** Only then does a weak quarter show as a slip or as the end of a trend.
- **Share count over several years.** The pattern of dilution says more than the last capital increase.

## Signals to look for

They are in no data set, but often the most telling part of an analysis.

- **Price outside the analyst range.** Above the highest target, the market pays more than any analyst considers justified. Name it, not only the mean.
- **Large distance to the mean, even inside the range.** Either the market is wrong or the models lag. Say which reading is closer.
- **Mean and median far apart.** One outlier pulls the mean. The median describes the typical analyst better.
- **Unanimity.** Not a single sell, or not a single buy, is a statement in itself.
- **Price below the last issue price.** It shows how fast the view turned and makes the next financing more expensive.
- **The story grows, the numbers shrink.** A pipeline is a list of possibilities, not an order book.
- **Accelerating cash outflow.** Often more important than revenue for young companies.
- **Negative P/E.** It means a loss. Write "loss-making", never quote it as a multiple.
- **Price against the 50-day and 200-day averages.** One sentence on the position, no chart-reading forecasts.

## Output structure

A skeleton, not a straitjacket. Leave out sections with nothing to say. Translate every heading into the user's language.

When the question aims at the day's events, such as "what is going on" or "why is it falling", the news comes right after the key statement and the numbers after that.

```markdown
## <Company>, <ISIN>

**Price <X>, market cap <Y>, 52-week range <A> to <B>**

<Two or three sentences: what the case turns on and where it stands. The key
statement is here at the top, not at the end.>

### Figures for <latest reporting period>
<Table with the three to five ratios that matter, against the prior year,
then the multi-year series for revenue and earnings.>

### Current news
<What happened since the last report, each item dated.>

### Valuation
<The multiples that fit this case, plus at least one own calculation with its
derivation.>

### Analyst picture
<Number of buy, hold and sell ratings. Target mean, median, range. Distance to
the price in percent. What stands out.>

### Assessment by horizon
**Short term:** <days to weeks, upcoming dates, position to the averages>
**Medium term:** <quarters, what has to happen for the thesis to work>
**Long term:** <years, structural position, competition, financing needs>

### For and against
<Two short lists, four to six points each, honestly weighted. Only sharpen what
was shown above.>

<If numbers were estimated, back-calculated or contradictory: a short paragraph
naming them and where to check them.>

---

<Disclaimer, two sentences>

Sources:
- [Title](URL)
```

**Several securities:** start with an overview table (price, change over one year, analyst target, character in three words), then one block per security. End with one line on what the selection has in common, such as shared drivers or risks. That is a property of the selection, not a statement about the user's portfolio.

## Language and style

Professional, no sales tone, in the user's language.

- **No semicolons.** Full stop or comma.
- **Simple sentences.** Two short ones rather than one with three clauses.
- Numbers in tables, judgements in prose.
- A concrete number beats an adjective: "down from 110 to 22, minus 80 percent", not "fell sharply".
- **Always write the currency.** Prices from the MCP are never converted, and different currencies are never added.
- No emojis.

**Length:** thorough, not long. The corridor is 1,200 to 1,500 words. Whoever goes far beyond usually repeats. The key statement is at the top: a reader who stops after five lines has the essentials.

**Caveats:** uncertainties in the data belong in the analysis, where they occur or in a short paragraph before the end, each with where to check it. Separate from that, the legal disclaimer at the very end is **two sentences**: no investment adviser and no recommendation, prices partly delayed and in local currency.

**Sources:** every analysis ends with `Sources:` and links to the pages actually used. No invented or unopened links.

## What this skill does not do

No personal investment advice, no recommendation to buy or sell, no orders. When asked: deliver the facts needed for one's own decision and say openly that the decision lies with the user.

Do not pretend to know what is not known. An honest gap is better than a plausible invention.

With visible financial distress or signs of problematic gambling, keep the numbers sober and do not fuel it.

---

# Appendix A: data traps

They are not specific to one provider. Stale share counts, ready-made ratios with an undocumented window and silently shortened lists exist with every bulk data provider.

## 1. Stale share count in the market cap

**The most dangerous trap**, because it silently distorts every valuation. The reported market cap is price times stored share count. After a capital increase, a conversion or a takeover, the stored count can be stale for weeks. A typical case: a small cap on the Stockholm exchange issues new shares, the provider keeps the old count, and the market cap shown is about a fifth too low, every multiple with it.

**The check takes ten seconds:** reported market cap divided by price gives the implied share count. Hold it against the annual report or the latest capital measure. If they differ, name both, value with the higher count and tell the user the standard sources show the lower one. Run the check after every news item on a capital increase, convertible, placement, buyback or takeover.

## 2. Ratios that fail on a loss

A negative P/E means a loss, not cheap. Switch to price to sales, price to book while equity is positive, or cash runway in quarters. Also be careful with a forward P/E in special situations: when valuation gains on held assets run through the income statement, a low P/E says nothing about earning power.

## 3. ISIN mix-ups

Resolve through the search, never from memory. If the resolved name could surprise, put it at the top of the answer and give the ISIN it could be confused with.

## 4. Empty fields that are no error

Analyst, holder, quarterly, insider and calendar data exist for single stocks only. For ETFs, funds and crypto they come back empty, and fund data only exists for funds. An empty field usually means the instrument has no such data. A real finding is a single stock with **no** analyst coverage or only one estimate.

## 5. Delayed and silently shortened data

Prices are partly delayed. During trading hours a price is a snapshot, not a close. Most queries return silently shortened lists, so a short list is no proof that the list is short. Raise a `limit` where one is offered. In a price history the last row can be a running session with empty prices but volume. Do not use it as a close.

## 6. Currencies

Nothing is converted. Every price, market cap and balance-sheet figure is in the instrument's currency. A comparison of a Swedish, a Hong Kong and a US security mixes three currencies without any hint in the data. Form multiples within one instrument, where the currency cancels out.

## 7. Beta and other artefacts

Beta is estimated from past prices. With extreme moves or a short history it becomes meaningless, for example negative for a stock that fell 80 percent in three months. Quote beta only when it is plausible. The same goes for price to book with a fluctuating equity base and for a dividend yield extrapolated from a one-off special dividend.

## 8. Options data

Options data exists for US-listed instruments only. Bid and ask can come back as zero, and the last traded prices may be from the previous day. An implied move from them is an approximation, given as a range.

## 9. Quick check before sending

1. **Is it really this company?** Resolved through the search.
2. **Is the share count right?** Market cap divided by price, against the latest known figure.
3. **Does the ratio I quote hold?** No negative P/E as a multiple, no absurd beta, no mixed currencies.
4. **Do I have the latest news?** Web search done, every price jump has a named trigger.

---

# Appendix B: instrument types

The structure stays the same. What changes is the question that decides the case.

**Profitable standard stock.** Is the price fair for this earning power? The usual ratios hold. Watch where the profit goes: in a group with large listed subsidiaries, part of the cash flow belongs to minority shareholders, and a group-level cash-flow yield overstates. Compare price and earnings over the same period. Check whether the dividend is covered by current earnings.

**Loss-making growth company.** Does the money last until the business model carries? In this order: liquidity and runway with capital spending included, then dilution and how far recent subscribers are under water, then the gap between narrative and revenue, and only then the valuation, by price to sales. One analyst is no consensus.

**ETF and fund.** What is really inside, and what does it cost over the holding period? What the index actually covers, often narrower than the name suggests. Ongoing costs and the transaction costs outside them. One-off costs kept apart from yearly ones. Withholding tax inside the fund as a real loss of return. Physical or swap-based, securities lending. Fund currency against trading currency.

**Preferred securities.** Can the issuer pay this for years? A stated yield refers to the par value, not to the market price. Back-calculate the par value from the stated payment and percentage, then the effective yield from the purchase price. Fixed or variable rate, paid from earnings or from new capital, cumulative or not, with or without a redemption date. A double-digit rate is the market's statement on default risk, not a gift.

**Treasury vehicles.** Companies whose value mostly comes from a held asset. Net asset value per common share against the market cap is the key ratio. Above one, issuing shares buys more of the asset per share. Below one, every issue destroys value per share. Check the average cost of the holding, the yearly burden of interest and preferred dividends against cash, and whether buying continues.

**Crypto.** No company data. Price, moving averages, 52-week range and volume, then the drivers: monetary policy and liquidity, regulation, flows into spot products, positioning in futures. Tell a short-covering rally from one carried by real inflows.

**Multiple listings.** The same company can trade as the original share, a secondary listing and a depositary receipt, which do not move in step. Always say which line is analysed. Outside the home market's trading hours, a price is often quoted without real price discovery and the spread is wider.
