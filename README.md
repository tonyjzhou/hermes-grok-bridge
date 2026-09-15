# Hermes ↔ Grok Bot bridge

Two ways to put your Hermes agent inside the Grok Bot app (or wire it as a connector) over a private network — usually Tailscale.

| Method | Best when | Tradeoff |
|--------|-----------|----------|
| **[SSH relay](./docs/SSH_RELAY.md)** | Hermes Desktop-primary; no API gateway; simplest “talk to Hermes” | Extra hop; needs SSH |
| **[Native API](./docs/NATIVE_API.md)** | Gateway + API server (`:8642`) already running; parallel fleet asks | Needs API enabled + private reach to `:8642` |

**Marketplace templates** (cross-linked):
- *Hermes SSH Relay* — SSH method
- *Hermes API Fleet* — native `:8642` method

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
