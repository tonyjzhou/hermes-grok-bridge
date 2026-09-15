# Hermes ↔ Grok Bot bridge

Two ways to connect [Grok Bot](https://grok.x.ai/) / Cursor agents to [Hermes Agent](https://hermes-agent.nousresearch.com/docs/) over a private network (typically Tailscale).

| Method | Best when | Tradeoff |
|--------|-----------|----------|
| **[SSH relay](./docs/SSH_RELAY.md)** | Hermes Desktop-primary host; no API gateway running; simplest “ask Hermes” | Extra hop; SSH dependency |
| **[Native API](./docs/NATIVE_API.md)** | Hermes gateway + API server (`:8642`) already on; parallel fleet orchestration | Needs API enabled + Tailscale reachability to `:8642` |

**Marketplace templates** (cross-linked):
- *Hermes SSH Relay* — ships the SSH method
- *Hermes API Fleet* — ships the native `:8642` method

Neither template embeds your hosts, SSH keys, or API keys. You point env / MCP config at **your** machines after install.

## Security (both methods)
- Tailscale (or equivalent private net) only — **no Funnel / public bind**
- Never commit `API_SERVER_KEY`, auth tokens, or live ledgers
- Do **not** use Grok bots to write into Hindsight / Hermes long-term memory unless you have an explicit memory plan
- Account-wide MCP tools are visible to all of a user’s Grok Bots — confine identity bots in their system prompt

## Repo layout
- `ssh-relay/` — stdio MCP (`ask`, `health`) via SSH → `hermes -z`
- `docs/` — operator guides for both methods
