# <img src="https://raw.githubusercontent.com/benethos-hub/agent-skills/main/assets/brand/icon.svg" alt="" width="40" height="40"> Finance skills

[![CI](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/benethos-hub/agent-skills/badges/coverage.json&logo=githubactions&logoColor=white)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/benethos-hub/agent-skills?logo=opensourceinitiative&logoColor=white)](https://github.com/benethos-hub/agent-skills/blob/main/LICENSE)

[![Release](https://img.shields.io/github/v/release/benethos-hub/agent-skills?label=Release&logo=github&logoColor=white)](https://github.com/benethos-hub/agent-skills/releases/latest)

[![Sponsor](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/sponsor.svg)](https://github.com/sponsors/BeneODev)
[![PayPal](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/paypal.svg)](https://paypal.me/BeneODev)

Skills for securities and portfolios. They calculate from current market data
and name every gap in it. They give no recommendation and no investment, tax or
legal advice.

**Contents**

- [Skills](#skills)
- [Quick start](#quick-start)
- [Setup in detail](#setup-in-detail)
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

A skill brings the method, not the data. The finance skills need prices,
dividend histories, corporate calendars, financial statements and analyst
targets, and all of it changes daily. Without a market-data MCP server the
agent has no reliable source for any of it. The skills then say so openly
instead of filling the gap from memory, and the answer is little more than a
list of what is missing.

So every setup has two parts: the skills and a server for the data.

## Quick start

The shortest way for each client, simplest first:

| Client | Steps |
|---|---|
| Claude Code | Add the marketplace and install the bundle `finance`. It brings both skills and the market-data server. Needs [uv](https://docs.astral.sh/uv/getting-started/installation/). |
| Claude Desktop | Upload both ZIPs under Settings, Skills. Then open the server's extension `benethos-yahoo-finance-mcp.mcpb`. |
| Other agents | Unpack both ZIPs into the agent's skills directory and add the server with `uvx benethos-yahoo-finance-mcp`. |
| claude.ai in the browser | Upload both ZIPs. The server only works there as your own hosted service. |

For Claude Code these are the two commands:

```bash
claude plugin marketplace add benethos-hub/agent-skills
claude plugin install finance@benethos-agent-skills
```

Then check the setup as in [step 4](#4-check-the-setup). The sections below
explain each part and the other ways.

## Setup in detail

### 1. Install the skills

In Claude Code the bundle `finance` brings both skills and the market-data
server from step 2:

```bash
claude plugin marketplace add benethos-hub/agent-skills
claude plugin install finance@benethos-agent-skills
```

Each skill also comes on its own:

| Skill | Download | Claude Code |
|---|---|---|
| asset-analysis | [asset-analysis.zip](https://github.com/benethos-hub/agent-skills/releases/latest/download/asset-analysis.zip) | `claude plugin install asset-analysis@benethos-agent-skills` |
| dividend-calendar | [dividend-calendar.zip](https://github.com/benethos-hub/agent-skills/releases/latest/download/dividend-calendar.zip) | `claude plugin install dividend-calendar@benethos-agent-skills` |

The steps for each client, the ZIP of a fixed version and updates work the
same for every skill of this repository. The
[main README](../../README.md#installing) covers them.

### 2. Connect a market-data server

The skills describe the data they need, not the tool that delivers it, so any
provider works. They are tested with the
[Unofficial Yahoo Finance MCP Server](https://github.com/benethos-hub/yahoo-finance-mcp).
It needs no account and no API key. The steps below set up this server. Its
[README](https://github.com/benethos-hub/yahoo-finance-mcp#installation) has
further ways to install it.

Set the server up one way only. Two ways at once can start it twice, and
every tool then appears twice.

#### Claude Code

With the bundle `finance` from step 1 the server is already there. Nothing
else is needed.

Without the bundle, install the server as a plugin of its own. It needs
[uv](https://docs.astral.sh/uv/getting-started/installation/) and the
marketplace from step 1:

```bash
claude plugin install benethos-yahoo-finance-mcp@benethos-agent-skills
```

Without the marketplace, this command makes the server available in every
project. Without `--scope user` it applies to the current project only:

```bash
claude mcp add --scope user benethos-yahoo-finance-mcp -- uvx benethos-yahoo-finance-mcp
```

`claude mcp list` shows whether the server is connected. No skill installs the
server by itself, because the skills work with any provider of the same data.

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

Then quit Claude Desktop fully, from the tray as well, and start it again.

#### Other agents

Every MCP client that starts local servers can use the same command. It needs
[uv](https://docs.astral.sh/uv/getting-started/installation/):

```json
{ "command": "uvx", "args": ["benethos-yahoo-finance-mcp"] }
```

Where this entry goes differs from client to client. The server's README lists
[compatible clients](https://github.com/benethos-hub/yahoo-finance-mcp#compatible-clients).

#### Claude in the browser

The browser version cannot start a server on your computer. It only reaches
servers on the internet, added as a custom connector. The Yahoo Finance server
can run that way, but only as your own hosted service with HTTPS. Its
[containers README](https://github.com/benethos-hub/yahoo-finance-mcp/blob/main/containers/README.md)
describes that setup. For most people Claude Desktop is the easier way.

### 3. Web search

`asset-analysis` uses a web search when the agent has one. The headlines of a
data provider often lag behind, and a price jump needs a named trigger. Without
a web search the skill still works and says in the answer that the search is
missing. `dividend-calendar` does not use a web search.

### 4. Check the setup

Start a new chat and ask for the current price of a ticker you know. If the
agent calls a tool of the server and names a price, the server is connected.
If the agent says it has no current data, the server is missing or not
started.

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
