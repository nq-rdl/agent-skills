---
name: acp
license: CC-BY-4.0
description: >-
  Agent Client Protocol (ACP) — the open JSON-RPC standard that lets code
  editors (clients) drive coding agents over stdio, like LSP for AI agents.
  Use this skill to navigate or use ACP: understand the protocol (initialize,
  session/new, session/prompt, streamed session/update), run Claude Code as an
  ACP agent inside editors such as Zed, Neovim, VS Code, or JetBrains, wire up
  other ACP agents (pi via pi-acp, Gemini CLI, Codex), or pick which
  editor↔agent pair to connect. Trigger whenever the user mentions ACP, "Agent
  Client Protocol", running Claude Code or another agent inside an editor,
  pi-acp, claude-code-acp / claude-agent-acp, agent_servers config, or
  editor↔agent integration. This is editor↔agent integration — distinct from
  MCP (agent↔tools) and from driving an agent headlessly over HTTP (see the
  pi-rpc and opencode skills).
compatibility: >-
  Knowledge skill — no dependencies. Following the worked examples needs an ACP
  client (e.g. Zed) and Node.js for the npx-launched agent adapters.
metadata:
  repo: https://github.com/nq-rdl/agent-skills
---

# Agent Client Protocol (ACP) Skill

A navigation skill for **using** ACP — not building an implementation. It helps
a human or an agent understand the protocol, find which tools speak it, and wire
an editor to a coding agent. The headline example is running **Claude Code
inside an editor** over ACP.

## What ACP Is

The **Agent Client Protocol** standardizes how a code editor talks to a coding
agent, the same way the **Language Server Protocol (LSP)** standardized how an
editor talks to a language server. Before ACP, every editor↔agent pairing was a
bespoke integration; ACP lets any compliant editor drive any compliant agent.

Two roles, and it is easy to get them backwards:

- **Client** = the **editor / IDE** (Zed, Neovim, VS Code…). It owns the UI, the
  filesystem, and the user's trust. It *launches* the agent.
- **Agent** = the **coding AI** (Claude Code, Gemini CLI, pi…). It runs as a
  subprocess and does the work.

```
┌─────────────────┐   spawns subprocess    ┌──────────────────┐
│  CLIENT         │ ─────────────────────▶ │  AGENT           │
│  (the editor)   │                        │  (the coding AI) │
│  Zed / Neovim   │  ◀── JSON-RPC 2.0 ───▶ │  Claude Code     │
│  VS Code …      │     over stdin/stdout  │  pi / Gemini …   │
└─────────────────┘                        └──────────────────┘
        owns UI, files,                       reads/edits code,
        permissions, MCP                      calls tools, streams
                                              progress back
```

The editor boots the agent on demand and talks to it over the agent's
**stdin/stdout** using newline-delimited JSON-RPC. This inverts the usual
chatbot shape: the *editor* is in control and grants the agent access, with the
user approving sensitive actions.

> **The key insight for "how do I use X with ACP?":** almost no agent speaks ACP
> natively. A thin **adapter** wraps the agent's own mode and translates it to
> ACP JSON-RPC over stdio. Claude Code is wrapped by `claude-agent-acp`; pi is
> wrapped by `pi-acp`. Learn that one pattern and the whole ecosystem makes
> sense. See `references/agents.rst`.

### ACP vs. MCP vs. driving an agent over HTTP

These get conflated constantly. Keep them straight:

| Protocol / approach | Connects | Use the skill |
|---------------------|----------|---------------|
| **ACP** | editor ↔ agent | **this skill** |
| **MCP** | agent ↔ tools/data | MCP skills |
| **pi-rpc / opencode HTTP** | one agent driving another *headlessly* over HTTP/JSON | `pi-rpc`, `opencode` |

ACP is about putting an agent behind an editor's UI. If you want one agent to
dispatch work to another with no editor involved, that is the HTTP-driving case
— reach for `pi-rpc` or `opencode`, not ACP. (Note: pi and Claude Code are both
*agents*; "use pi with Claude Code" is not a native ACP topology — you would run
each as an agent inside the *same editor*.)

## When to Use This Skill

| You want to… | Start at |
|--------------|----------|
| Understand what ACP is and how the wire protocol works | this file → `references/protocol.rst` |
| Run **Claude Code** inside an editor (Zed, Neovim, …) | `references/claude-code.rst` |
| Wire up **another agent** (pi, Gemini, Codex) | `references/agents.rst` |
| Connect an agent in a specific **editor / client** | `references/clients.rst` |
| Copy a complete, working setup | `references/examples.rst` |
| Build an ACP agent or client from scratch | the SDKs — see [Source Material](#source-material) (this skill is about *using* ACP) |

## The Protocol at a Glance

A session runs through a small, fixed sequence of JSON-RPC calls. Methods named
`x/y` are namespaced; notifications are one-way (no response).

```
1. initialize            Client → Agent   negotiate protocol version + capabilities
   (authenticate)        Client → Agent   only if the agent reports it needs auth
2. session/new           Client → Agent   start a session (cwd, MCP servers) → sessionId
   (or session/load)     Client → Agent   resume a prior session
3. session/prompt        Client → Agent   send the user's turn → blocks until a stopReason
      session/update     Agent  → Client   *streamed* progress: message chunks, tool
                                           calls, plan updates, mode changes
      session/request_permission           Agent asks the user to approve a tool call
                         Agent  → Client
   (session/cancel)      Client → Agent   interrupt the running turn
```

Core methods (see `references/protocol.rst` for the full set and payloads):

| Direction | Method | Purpose |
|-----------|--------|---------|
| Client → Agent | `initialize` | Handshake: protocol version + capability negotiation |
| Client → Agent | `authenticate` | Authenticate if the agent requires it |
| Client → Agent | `session/new` | Create a session; returns a `sessionId` |
| Client → Agent | `session/load` | Resume an existing session (optional) |
| Client → Agent | `session/prompt` | Send a user turn; resolves with a `stopReason` |
| Client → Agent | `session/set_mode` | Switch agent mode, e.g. ask ↔ code (optional) |
| Agent → Client | `session/update` *(notification)* | Stream message/tool/plan progress |
| Agent → Client | `session/request_permission` | Ask the user to approve an action |
| Agent → Client | `fs/read_text_file`, `fs/write_text_file` | Use the editor's filesystem (optional) |
| Agent → Client | `terminal/*` | Run commands in the editor's terminal (optional) |
| Client → Agent | `session/cancel` *(notification)* | Cancel the current turn |

Conventions worth remembering: **file paths are absolute**, **line numbers are
1-based**, and content reuses MCP's content-block types (text, image, resource),
so an ACP-literate tool is already half MCP-literate.

## Quickstart 1 — Run Claude Code in Zed (the flagship)

The most common "ACP + Claude Code" workflow: Claude Code becomes an agent in
Zed's agent panel.

1. Install [Zed](https://zed.dev) and open your project.
2. Open the agent panel: `cmd-?` (macOS) / `ctrl-?` (Linux).
3. Click the agent selector and choose **Claude Code**. The first time, Zed
   auto-installs the adapter (`@agentclientprotocol/claude-agent-acp`, formerly
   `@zed-industries/claude-code-acp`) and prompts you to sign in to your Claude
   account.
4. Start a thread and prompt as usual — edits, tool calls, and permission
   requests now render in Zed's UI.

No `agent_servers` config is needed for the built-in agents. To point the
adapter at a specific Claude Code binary, set `CLAUDE_CODE_EXECUTABLE`. Full
setup, auth, Neovim, and troubleshooting: `references/claude-code.rst`.

## Quickstart 2 — Add any ACP agent (pi example)

Agents that aren't built into your editor are added via the editor's agent
config. In Zed's `settings.json`:

```json
{
  "agent_servers": {
    "pi": {
      "type": "custom",
      "command": "npx",
      "args": ["-y", "pi-acp"],
      "env": {}
    }
  }
}
```

`pi-acp` launches and bridges to `pi --mode rpc` over stdio (needs Node 22+ and
`pi` installed and configured). Gemini CLI uses `gemini --acp`; Codex uses the
`codex-acp` adapter. The catalog drifts — the live **ACP Registry** is the
source of truth. See `references/agents.rst`.

## Quickstart 3 — See the protocol by hand

You can drive an agent yourself to watch the JSON-RPC flow — the fastest way to
*understand* ACP. Pipe newline-delimited requests into an adapter's stdin and
read its stdout. A complete, runnable handshake is in `references/examples.rst`.

## Reference Docs

Read these as needed — each is loaded only when you follow the pointer.

- `references/protocol.rst` — The wire protocol: roles, transports, full
  lifecycle, every method, `session/update` variants, permissions, content
  blocks, tool calls, filesystem/terminal, modes, slash commands, extensibility.
- `references/agents.rst` — The adapter pattern and how to launch ACP agents
  (Claude Code, pi, Gemini CLI, Codex), plus the live registry.
- `references/clients.rst` — ACP editors/clients (Zed, Neovim, VS Code,
  JetBrains, Emacs…) and how to connect an agent in each.
- `references/claude-code.rst` — Flagship deep-dive: Claude Code as an ACP
  agent — adapters, install, auth, editor setup, capabilities, troubleshooting.
- `references/examples.rst` — Copy-paste end-to-end setups and a hand-driven
  raw-stdio session.

## Source Material

Canonical, authoritative references (consult these when facts may have changed —
the ecosystem moves fast):

- Introduction — https://agentclientprotocol.com/get-started/introduction
- Architecture — https://agentclientprotocol.com/get-started/architecture
- Protocol spec (source) — https://github.com/agentclientprotocol/agent-client-protocol/tree/main/docs/protocol
- Agents directory — https://agentclientprotocol.com/get-started/agents
- Clients directory — https://agentclientprotocol.com/get-started/clients
- ACP Registry — https://agentclientprotocol.com/get-started/registry
- LLM-friendly doc index — https://agentclientprotocol.com/llms.txt
- Zed external agents — https://zed.dev/docs/ai/external-agents
