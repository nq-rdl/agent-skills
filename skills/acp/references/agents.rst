ACP Agents and the Adapter Pattern
==================================

This file answers "how do I make agent *X* available over ACP?" The short
answer is almost always: **run its ACP adapter**. Understand the pattern once
and every agent looks the same.

.. contents:: Contents
   :local:
   :depth: 1

The adapter pattern
-------------------

Most coding agents were not born speaking ACP. They already had their own
control surface — a JSON-over-stdio "RPC mode", an SDK, or a CLI. An **ACP
adapter** is a thin process that:

1. Is launched by the client (editor) as a subprocess.
2. Speaks **ACP JSON-RPC 2.0 over stdio** to the client.
3. Drives the underlying agent through its native interface and translates both
   ways — client requests in, agent events out.

::

   ┌──────────┐  ACP/JSON-RPC   ┌──────────────┐  native mode   ┌──────────┐
   │ editor   │ ◀────stdio────▶ │  ACP adapter │ ◀────────────▶ │  agent   │
   │ (client) │                 │  (pi-acp …)  │  (pi --mode    │  engine  │
   └──────────┘                 └──────────────┘   rpc, SDK…)   └──────────┘

So "does X support ACP?" really means "is there an adapter for X?". Because the
adapter is just another process the editor spawns, **adding an agent is mostly a
matter of telling the editor the command to run** (see ``clients.rst``).

How an agent process is launched
--------------------------------

An ACP agent is any executable that, once started, reads JSON-RPC requests on
``stdin`` and writes JSON-RPC messages on ``stdout`` (see ``protocol.rst`` for
the stdio rules). Editors store this as a *command + args + env*. The same
command is what you would run by hand to drive the protocol yourself
(``examples.rst``).

Built-in vs. custom agents
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Editors expose agents two ways:

- **Registry / built-in** — the editor knows the agent, installs the adapter for
  you, and keeps it updated. In Zed these are Claude Agent, Gemini CLI, and
  Codex. You usually just pick them from a menu.
- **Custom** — you provide the command yourself. This is how you add anything
  the editor doesn't bundle (e.g. ``pi-acp``).

Durable examples
----------------

Commands verified at the time of writing. Package names drift — confirm against
the registry (below) before quoting them as gospel.

Claude Code
~~~~~~~~~~~

- **Adapter:** ``@agentclientprotocol/claude-agent-acp`` (formerly
  ``@zed-industries/claude-code-acp``). Wraps the official Claude Agent SDK.
- **In Zed:** built-in — choose "Claude Code" / "Claude Agent"; Zed installs and
  manages the adapter automatically.
- **Auth:** sign in to your Claude account, or set ``ANTHROPIC_API_KEY``.
- **Tip:** ``CLAUDE_CODE_EXECUTABLE`` overrides which Claude Code binary the
  adapter drives.
- Full deep-dive (auth, Neovim, troubleshooting): ``claude-code.rst``.

pi (pi.dev)
~~~~~~~~~~~

- **Adapter:** ``pi-acp`` — launch with ``npx -y pi-acp``.
- **What it does:** spawns ``pi --mode rpc`` and bridges it to ACP over stdio.
- **Prerequisites:** Node.js 22+, ``pi`` installed globally and configured with a
  model provider. Optional: ``PI_ACP_ENABLE_EMBEDDED_CONTEXT=true``.
- **Note:** pi skills surface in the client as ``/skill:<name>`` slash commands;
  sessions resume on both sides.
- Custom-agent config: ``command: "npx"``, ``args: ["-y", "pi-acp"]``.

Gemini CLI
~~~~~~~~~~

- **Launch:** ``gemini --acp`` — Gemini CLI has a built-in ACP mode (no separate
  adapter package). The flag has shifted across releases; confirm with
  ``gemini --help`` if it is rejected.
- **In Zed:** built-in — choose "Gemini CLI".

Codex (OpenAI)
~~~~~~~~~~~~~~

- **Adapter:** ``codex-acp`` (``github.com/zed-industries/codex-acp``).
- **In Zed:** built-in — choose "Codex".

Others
~~~~~~

ACP adoption is broad and growing — Cursor, GitHub Copilot CLI (public preview),
Goose, Cline, JetBrains Junie, Kimi CLI, Docker cagent, and many more publish
adapters or native ACP modes. Rather than copy a list that rots, look them up
live (next section).

The registry is the source of truth
------------------------------------

The set of agents and their exact launch commands change frequently. When you
need a current, authoritative answer:

- **ACP Registry** — discover/install agents:
  https://agentclientprotocol.com/get-started/registry
- **Agents directory** — every known agent + links:
  https://agentclientprotocol.com/get-started/agents
- **LLM-friendly index** — machine-readable doc map:
  https://agentclientprotocol.com/llms.txt

If a launch command here ever fails, treat these as canonical and update
accordingly.
