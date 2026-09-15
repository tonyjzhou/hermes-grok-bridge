# Native Hermes API method

## When to use
- Hermes **gateway** is already running with **API server** enabled (`API_SERVER_ENABLED=true`, port **8642**)
- You want **lower Grok-token overhead** and easier **parallel** calls across many Hermes hosts
- Tailscale ACL already allows controller → node `:8642`

## How it works
Hermes ships an OpenAI-compatible **API server** on `:8642` (docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server).  
Grok Bot connects with a remote MCP or thin OpenAI client using `Authorization: Bearer <API_SERVER_KEY>` to `http://<tailscale-magicdns>:8642/v1`.

Default bind is often `127.0.0.1` — for Tailscale clients you must set `API_SERVER_HOST` to the node’s Tailscale IP (or an explicit private bind) **with a strong key**. Never Funnel.

## Install (operator checklist)
1. On each Hermes host: `API_SERVER_ENABLED=true`, set `API_SERVER_KEY`, set host bind for Tailscale, restart gateway.
2. Verify from the Grok controller: `curl http://<host>:8642/health` (and authenticated `/v1/models`).
3. Add MCP / connector per host named `hermes-<hostname>` pointing at that base URL + key (secret store).
4. Prefer this path for COS/ops orchestration; keep identity Grok bots optional.

See also marketplace template **Hermes API Fleet**. If the host is Desktop-only with no gateway, use [SSH_RELAY.md](./SSH_RELAY.md) instead.
