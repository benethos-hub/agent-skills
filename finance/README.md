# Finance skills

Skills for securities and portfolios. They calculate from current market data
and name every gap in it. They give no recommendation and no investment, tax or
legal advice.

**Contents**

- [Skills](#skills)
- [Setup](#setup)
  - [1. Install the skills](#1-install-the-skills)
  - [2. Connect a market-data server](#2-connect-a-market-data-server)
  - [3. Web search](#3-web-search)
  - [4. Check the setup](#4-check-the-setup)
- [Data the skills use](#data-the-skills-use)
- [Limits of the data](#limits-of-the-data)
- [Privacy](#privacy)
- [Disclaimer](#disclaimer)

## Skills

| Skill | What for | Needs |
|---|---|---|
| [asset-analysis](asset-analysis/SKILL.md) | An analysis of a single security with own calculations, data traps checked, an assessment by horizon and no recommendation | a market-data MCP server, a web search helps |
| [dividend-calendar](dividend-calendar/SKILL.md) | A dividend calendar for a portfolio, current or coming year, paid and forecast kept apart, with a list of gaps | a market-data MCP server |

## Setup

A skill brings the method, not the data. The finance skills need prices,
dividend histories, corporate calendars, financial statements and analyst
targets, and all of it changes daily. Without a market-data MCP server the
agent has no reliable source for any of it. The skills then say so openly
instead of filling the gap from memory, and the answer is little more than a
list of what is missing.

So the setup has two parts: the skills themselves and a server for the data.

### 1. Install the skills

Install each skill by its own folder, as described under
[Installing](../README.md#installing) in the main README.

### 2. Connect a market-data server

The skills describe the data they need, not the tool that delivers it, so any
provider works. They are tested with the
[Unofficial Yahoo Finance MCP Server](https://github.com/benethos-hub/yahoo-finance-mcp).
It needs no account and no API key. The steps below set up this server. Its
[README](https://github.com/benethos-hub/yahoo-finance-mcp#installation) has
further ways to install it.

#### Claude Desktop

The simplest way is the extension. Nothing has to be installed first.

1. Download
   [`benethos-yahoo-finance-mcp.mcpb`](https://github.com/benethos-hub/yahoo-finance-mcp/releases/latest/download/benethos-yahoo-finance-mcp.mcpb).
2. Open the file with a double click, or drag it onto Claude Desktop under
   Settings, Extensions. Confirm the installation.
3. Start a new chat. The first start of the server takes a few seconds.

Instead of the extension, the server can also be entered by hand. This needs
[uv](https://docs.astral.sh/uv/getting-started/installation/). Open Settings,
Developer, Edit Config and add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "benethos-yahoo-finance-mcp": {
      "command": "uvx",
      "args": ["benethos-yahoo-finance-mcp"]
    }
  }
}
```

Then quit Claude Desktop fully, from the tray as well, and start it again. Use
only one of the two ways. With both, every tool appears twice.

#### Claude Code

This needs [uv](https://docs.astral.sh/uv/getting-started/installation/). The
following command makes the server available in every project:

```bash
claude mcp add --scope user benethos-yahoo-finance-mcp -- uvx benethos-yahoo-finance-mcp
```

Without `--scope user` it applies to the current project only. `claude mcp list`
shows whether the server is connected.

#### Claude in the browser

The browser version cannot start a server on your computer. It only reaches
servers on the internet, added as a custom connector. The Yahoo Finance server
can run that way, but only as your own hosted service with HTTPS. Its
[containers README](https://github.com/benethos-hub/yahoo-finance-mcp/blob/main/containers/README.md)
describes that setup. For most people Claude Desktop is the easier way.

#### Other agents

Every MCP client that starts local servers can use the same command:

```json
{ "command": "uvx", "args": ["benethos-yahoo-finance-mcp"] }
```

Where this entry goes differs from client to client. The server's README lists
[compatible clients](https://github.com/benethos-hub/yahoo-finance-mcp#compatible-clients).

### 3. Web search

`asset-analysis` uses a web search when the agent has one. The headlines of a
data provider often lag behind, and a price jump needs a named trigger. Without
a web search the skill still works and says in the answer that the search is
missing. `dividend-calendar` does not use a web search.

### 4. Check the setup

Start a new chat and ask for the current price of a ticker you know. If the
agent calls a tool of the server and names a price, the server is connected. If the agent
says it has no current data, the server is missing or not started.

## Data the skills use

The table helps to check whether another provider covers what a skill needs.
The tool names are those of the Yahoo Finance server. Other providers name
their tools differently.

| Data | Yahoo Finance tool | asset-analysis | dividend-calendar |
|---|---|---|---|
| Symbol from an ISIN or a name | `search` | yes | yes |
| Price, ranges, market cap, exchange rates | `get_quote` | yes | yes |
| Dividend history | `get_dividends` | | yes |
| Corporate calendar with report and dividend dates | `get_calendar` | yes | yes |
| Company profile and ratios | `get_company_info` | yes | |
| Analyst ratings and price targets | `get_recommendations` | yes | |
| Consensus estimates | `get_estimates` | yes | |
| Financial statements | `get_financials` | yes | |
| Share count over time | `get_shares` | yes | |
| Price history | `get_history` | yes | |
| Headlines | `get_news` | yes | |
| Option chain | `get_options` | yes | |
| Fund data for ETFs | `get_fund_data` | yes | |

## Limits of the data

- **Unofficial source.** The Yahoo Finance server reads Yahoo's unofficial
  endpoints. They can change or break at any time, and Yahoo can limit the
  number of requests. On a rate limit the skills wait briefly and try again.
- **Delayed data.** Prices are partly delayed. During trading hours a price is
  a snapshot, not a close.
- **No WKNs.** German WKNs cannot be resolved. The skills then ask for an ISIN,
  a ticker or a name.
- **No corporate calendar for ETFs and funds.** Their pay dates are estimated.

Each skill has an appendix on the data traps it checks for.

## Privacy

A portfolio's share counts stay in the conversation. No data tool takes them.
Only symbols and ISINs are queried. The server places no orders, holds no
portfolio and signs in nowhere.

## Disclaimer

The skills deliver facts and calculations for one's own decisions. They are no
investment, tax or legal advice. Market data can be incomplete and delayed, and
every future value is a forecast.
