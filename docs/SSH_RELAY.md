# SSH relay method

## When to use
- Hermes **Desktop-primary** (no standing messaging gateway)
- You want a working bridge **today** without enabling the HTTP API
- Single-host or light ask traffic

## How it works
Grok Bot computer runs a **stdio MCP** that SSHs to the Hermes Mac and runs `hermes -z "<prompt>"`.

## Install
1. Clone this repo onto the Grok Bot computer.
2. Add an MCP server (command mode):
   - command: `python3`
   - args: `…/ssh-relay/src/hermes_grok_relay/server.py`
   - env: `HERMES_RELAY_SSH_TARGET=user@host`, `HERMES_RELAY_IDENTITY_NAME=Scooby` (or your label)
3. Optional: create a Grok Bot whose name matches the Hermes identity; confine it to that MCP.

See also marketplace template **Hermes SSH Relay**. For fleet HTTP orchestration, see [NATIVE_API.md](./NATIVE_API.md).
