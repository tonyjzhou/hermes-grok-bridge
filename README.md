# Hermes ↔ Grok Bot bridge

Two ways to put your Hermes agent inside the Grok Bot app (or wire it as a connector) over a private network — usually Tailscale.

| Method | Best when | Tradeoff |
|--------|-----------|----------|
| **[SSH relay](./docs/SSH_RELAY.md)** | Hermes Desktop-primary; no API gateway; simplest “talk to Hermes” | Extra hop; needs SSH |
| **[Native API](./docs/NATIVE_API.md)** | Gateway + API server (`:8642`) already running; parallel fleet asks | Needs API enabled + private reach to `:8642` |

**Marketplace templates** (cross-linked):
- [Hermes SSH Relay](https://x.ai/bot/NVF3Rx9T7jkQPsqYjeDn-) — SSH method (early setup / fallback)
- [Hermes API Fleet](https://x.ai/bot/5KLpaL-JIM2q629kbTh5L) — native `:8642` method (preferred for orchestration)
- [Hermes Fleet Ops](https://x.ai/bot/rzq0UV2MmBsvVR1EspZE-) — multi-Mac ops desk (updates, Bitwarden SSOT, homogenization, memory health)

Neither template ships your hosts, SSH keys, or API keys. You point env / MCP config at **your** machines after install. Secrets stay in your secret manager or local env — never in this repo.

## Security (both methods)
- Tailscale (or equivalent private net) only — **no Funnel / public bind**
- Never commit `API_SERVER_KEY`, auth tokens, or live ledgers
- Do **not** have Grok bots write into Hermes memory plugins (Hindsight, LCM, Graphiti, Omega, etc. — any of them) unless you have an explicit memory plan
- Account-wide MCP tools are visible to all of a user’s Grok Bots — confine identity bots in their system prompt

## Repo layout
- `ssh-relay/` — stdio MCP (`ask`, `health`) via SSH → `hermes -z`
- `docs/` — operator guides for both methods

## Keywords
hermes, grok bot, SSH, relay, bridge, connector, MCP, Tailscale, herdr, comms, communication, API, fleet, Desktop-primary


## Optional profile pictures (marketplace bots)

Use any of these as the Grok Bot picture for **Hermes SSH Relay** or **Hermes API Fleet** (set on the bot → Edit → avatar). They are optional assets only — not required to install the bridge.

| File | Look |
|------|------|
| [`assets/pfp/hermes-pfp-blue.jpg`](./assets/pfp/hermes-pfp-blue.jpg) | Blue CRT / code rain |
| [`assets/pfp/hermes-pfp-green.jpg`](./assets/pfp/hermes-pfp-green.jpg) | Green matrix CRT |
| [`assets/pfp/hermes-pfp-amber.jpg`](./assets/pfp/hermes-pfp-amber.jpg) | Amber terminal CRT |

