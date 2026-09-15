#!/usr/bin/env python3
"""Hermes ↔ Grok Bot relay MCP (stdio).

Transports:
  ssh  — SSH to a Hermes host and run `hermes -z "<prompt>"` (default; Desktop-friendly)
  http — POST OpenAI-compatible chat to Hermes API server (port 8642)

Env (required for ssh): HERMES_RELAY_SSH_TARGET  e.g. user@hostname
Optional: HERMES_RELAY_SSH_IDENTITY, HERMES_RELAY_SSH_OPTS,
          HERMES_RELAY_TIMEOUT_SEC (default 300),
          HERMES_RELAY_MODE=ssh|http,
          HERMES_RELAY_HTTP_URL, HERMES_RELAY_HTTP_KEY,
          HERMES_RELAY_IDENTITY_NAME (display label only, default Hermes)

Never logs secrets. Never opens a public bind.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "hermes-grok-relay"
SERVER_VERSION = "0.1.0"


def _log(msg: str) -> None:
    sys.stderr.write(f"[{SERVER_NAME}] {msg}\n")
    sys.stderr.flush()


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def identity_label() -> str:
    return env("HERMES_RELAY_IDENTITY_NAME", "Hermes")


def mode() -> str:
    m = env("HERMES_RELAY_MODE", "ssh").lower()
    return m if m in ("ssh", "http") else "ssh"


def timeout_sec() -> int:
    try:
        return max(30, int(env("HERMES_RELAY_TIMEOUT_SEC", "300")))
    except ValueError:
        return 300




def ask_via_ssh(prompt: str) -> dict[str, Any]:
    import base64
    import shlex

    target = env("HERMES_RELAY_SSH_TARGET")
    if not target:
        return {"ok": False, "error": "HERMES_RELAY_SSH_TARGET is not set"}
    hermes_bin = env("HERMES_RELAY_HERMES_BIN", "$HOME/.local/bin/hermes")
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15"]
    ident = env("HERMES_RELAY_SSH_IDENTITY")
    if ident:
        cmd += ["-i", ident, "-o", "IdentitiesOnly=yes"]
    extra = env("HERMES_RELAY_SSH_OPTS")
    if extra:
        cmd += extra.split()
    b64 = base64.b64encode(prompt.encode("utf-8")).decode("ascii")
    # Single remote string executed by the user's login shell
    remote = (
        f"PROMPT=$(printf '%s' {shlex.quote(b64)} | base64 -d); "
        f"exec {hermes_bin} -z \"$PROMPT\""
    )
    cmd += [target, remote]
    t0 = time.time()
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec(),
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timeout after {timeout_sec()}s", "mode": "ssh"}
    except FileNotFoundError:
        return {"ok": False, "error": "ssh binary not found on relay host", "mode": "ssh"}
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    return {
        "ok": r.returncode == 0 and bool(out),
        "mode": "ssh",
        "identity": identity_label(),
        "elapsed_s": round(time.time() - t0, 3),
        "returncode": r.returncode,
        "answer": out[-50000:] if out else "",
        "stderr_tail": err[-2000:] if err else "",
    }


def ask_via_http(prompt: str) -> dict[str, Any]:
    url = env("HERMES_RELAY_HTTP_URL")
    key = env("HERMES_RELAY_HTTP_KEY")
    if not url or not key:
        return {
            "ok": False,
            "error": "HERMES_RELAY_HTTP_URL and HERMES_RELAY_HTTP_KEY required for http mode",
        }
    base = url.rstrip("/")
    if not base.endswith("/v1") and not base.endswith("/chat/completions"):
        endpoint = base + "/v1/chat/completions"
    elif base.endswith("/v1"):
        endpoint = base + "/chat/completions"
    else:
        endpoint = base
    body = json.dumps(
        {
            "model": "hermes-agent",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
    ).encode()
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": f"{SERVER_NAME}/{SERVER_VERSION}",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec()) as r:
            payload = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {
            "ok": False,
            "mode": "http",
            "error": f"HTTP {e.code}",
            "body": e.read().decode(errors="replace")[:500],
        }
    except Exception as e:
        return {"ok": False, "mode": "http", "error": type(e).__name__}
    try:
        answer = payload["choices"][0]["message"]["content"]
    except Exception:
        return {"ok": False, "mode": "http", "error": "unexpected response shape"}
    return {
        "ok": True,
        "mode": "http",
        "identity": identity_label(),
        "elapsed_s": round(time.time() - t0, 3),
        "answer": answer,
    }




def health() -> dict[str, Any]:
    m = mode()
    if m == "http":
        url = env("HERMES_RELAY_HTTP_URL", "").rstrip("/")
        if not url:
            return {"ok": False, "error": "HERMES_RELAY_HTTP_URL unset"}
        health_url = url.replace("/v1/chat/completions", "").rstrip("/")
        if health_url.endswith("/v1"):
            health_url = health_url[:-3]
        health_url = health_url.rstrip("/") + "/health"
        try:
            with urllib.request.urlopen(health_url, timeout=10) as r:
                return {"ok": True, "mode": "http", "health": json.loads(r.read().decode())}
        except Exception as e:
            return {"ok": False, "mode": "http", "error": type(e).__name__}
    target = env("HERMES_RELAY_SSH_TARGET")
    if not target:
        return {"ok": False, "error": "HERMES_RELAY_SSH_TARGET unset"}
    hermes_bin = env("HERMES_RELAY_HERMES_BIN", "$HOME/.local/bin/hermes")
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10"]
    ident = env("HERMES_RELAY_SSH_IDENTITY")
    if ident:
        cmd += ["-i", ident, "-o", "IdentitiesOnly=yes"]
    extra = env("HERMES_RELAY_SSH_OPTS")
    if extra:
        cmd += extra.split()
    cmd += [target, f"exec {hermes_bin} --version"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except Exception as e:
        return {"ok": False, "mode": "ssh", "error": type(e).__name__}
    return {
        "ok": r.returncode == 0,
        "mode": "ssh",
        "identity": identity_label(),
        "version": (r.stdout or r.stderr or "").strip()[:200],
        "returncode": r.returncode,
    }


TOOLS = [
    {
        "name": "ask",
        "description": (
            f"Send a natural-language request to {identity_label()} (the Hermes agent on the "
            "linked host) and return that agent's answer. Comms relay only — forward the user "
            "ask; do not instruct Hermes to write/save/upsert into Hindsight or other memory "
            "stores. Do not invent answers — always call this tool."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Exact user ask to forward to Hermes.",
                }
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "health",
        "description": "Check that the Hermes relay path (SSH or HTTP) is reachable.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


def handle_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "health":
        return health()
    if name == "ask":
        prompt = (arguments or {}).get("prompt") or ""
        if not str(prompt).strip():
            return {"ok": False, "error": "prompt is required"}
        if mode() == "http":
            return ask_via_http(str(prompt))
        return ask_via_ssh(str(prompt))
    return {"ok": False, "error": f"unknown tool {name}"}


def send(msg: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def result_text(obj: Any, req_id: Any) -> None:
    send(
        {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(obj, indent=2)}],
                "isError": not bool(obj.get("ok", True)) if isinstance(obj, dict) else False,
            },
        }
    )


def main() -> int:
    _log(f"starting mode={mode()} identity={identity_label()}")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method")
        req_id = msg.get("id")
        params = msg.get("params") or {}

        if method == "initialize":
            send(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    },
                }
            )
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            try:
                out = handle_tool(name, args)
            except Exception as e:
                out = {"ok": False, "error": type(e).__name__}
            result_text(out, req_id)
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": req_id, "result": {}})
        elif req_id is not None:
            send(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
