# Security — Hermes ↔ Grok Bot relay

## Threat model
This MCP lets Grok Bots send natural-language prompts to a Hermes host over Tailscale SSH (or optionally the Hermes API server on port 8642). Hermes may have full tools on that Mac.

## Hard rules
1. **Tailscale only** — never expose Hermes API via Funnel/public internet.
2. **ACL** — only `tag:herdr-controller` → Hermes node ports `22` / `8642` / `9119`.
3. **No memory writes from Grok** — relay bots must not instruct Hermes to write Hindsight/Graphiti/Omega/MEMORY.md unless the human later authorizes a memory plan.
4. **Account-scoped MCP** — adding this connector to Cursor makes the tools visible to *all* of this user's Grok Bots. Confine the Scooby bot in its system prompt; other bots must not use it.
5. **Secrets** — never put API keys or SSH private keys in the public template. Prefer SSH key auth already on the controller; for HTTP mode keep `HERMES_RELAY_HTTP_KEY` in a secret store.
6. **Least prompt** — forward user asks; do not wrap them in “also save this to memory” instructions.

## Preferred transport (this fleet)
SSH + `hermes -z` keeps Scooby **Desktop-primary** (no messaging-gateway LaunchAgent required for relay). HTTP API mode is optional later and requires a locked-down API server + bearer key.
