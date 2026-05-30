Claude Code as an ACP Agent
===========================

The headline use of ACP: run **Claude Code inside an editor**. Claude Code
becomes the *agent*; the editor (Zed, Neovim, …) is the *client*. You get
Claude Code's engine with the editor's native UI — inline diffs, file
following, permission prompts, terminals.

.. contents:: Contents
   :local:
   :depth: 1

What the adapter is
-------------------

Claude Code does not speak ACP directly. An adapter built on the **official
Claude Agent SDK** (which runs Claude Code under the hood) implements the ACP
agent side and translates to ACP JSON-RPC over stdio. It supports:

- Context ``@``-mentions and images
- Tool calls with permission requests (``session/request_permission``)
- "Following" the agent through files as it edits
- Edit review (diffs surfaced in the editor)
- TODO lists (surfaced as ``plan`` updates)
- Interactive and background terminals
- Custom slash commands
- Client-provided MCP servers

Packages and naming
-------------------

The package has been renamed, so you will see more than one name in the wild:

- ``@agentclientprotocol/claude-agent-acp`` — current name (per the adapter's
  own README badge).
- ``@zed-industries/claude-code-acp`` — the earlier name; still widely
  referenced and what Zed's registry has historically installed.
- ``Xuanwo/acp-claude-code`` — a community implementation.

You rarely type these yourself: in an editor with a registry (Zed) the adapter
is installed and updated for you. Quote a specific package only after checking
the registry — see https://agentclientprotocol.com/get-started/registry

Setup in Zed (recommended)
--------------------------

1. Open your project in Zed.
2. Open the agent panel: ``cmd-?`` (macOS) / ``ctrl-?`` (Linux).
3. Click the agent selector (left, in the empty state) or the ``+`` button
   (top-right) and choose **Claude Code**.
4. On first use, Zed installs the managed adapter and prompts you to sign in to
   your Claude account.
5. Start a thread and prompt. Edits, tool calls, and permission requests now
   render in Zed.

Zed always uses its **managed** adapter version, even if you have Claude Code
installed globally. To make the adapter drive a specific Claude Code binary, set
``CLAUDE_CODE_EXECUTABLE`` for the registry entry:

.. code:: json

   {
     "agent_servers": {
       "claude-acp": {
         "type": "registry",
         "env": { "CLAUDE_CODE_EXECUTABLE": "/usr/local/bin/claude" }
       }
     }
   }

Docs: https://zed.dev/docs/ai/external-agents and
https://zed.dev/blog/claude-code-via-acp

Setup in Neovim
---------------

Use an ACP-capable plugin (``CodeCompanion``, ``avante.nvim``, or
``agentic.nvim`` — see ``clients.rst``) and register Claude Code as an agent.
The plugin needs the command that launches the adapter; with Node available that
is the adapter package run via ``npx`` (confirm the exact package name from the
registry). Follow the plugin's agent-configuration docs for where the
``command``/``args``/``env`` go.

Authentication
--------------

Two paths, same as Claude Code itself:

- **Claude account** — sign in when the editor prompts (uses your Claude
  subscription).
- **API key** — set ``ANTHROPIC_API_KEY`` in the agent's ``env``.

If prompts never produce a response, auth is the first suspect (see below).

Capabilities and limits
------------------------

- The agent runs as an independent process; the editor provides the UI and
  brokers file/terminal access and permissions.
- What is available depends on capability negotiation at ``initialize`` — e.g.
  image input requires the agent's ``promptCapabilities.image`` and the editor
  sending image content blocks.
- ACP today is stdio-only in practice (HTTP transport is a draft), so the agent
  runs locally alongside the editor.

Troubleshooting
---------------

============================== ============================== ============================================
Symptom                        Likely cause                   Fix
============================== ============================== ============================================
Adapter won't install/start    Node/npm missing or offline    Ensure Node.js + network; check editor logs
Prompts hang, no response      Auth not completed/expired     Re-sign-in or set ``ANTHROPIC_API_KEY``; restart
Wrong Claude version runs      Managed adapter, not your CLI  Set ``CLAUDE_CODE_EXECUTABLE`` to your binary
Garbled / "invalid message"    Agent wrote junk to stdout     A non-ACP write corrupts stdio; inspect stderr
Tool calls never auto-approve  Permission prompts pending     Approve in the editor, or set its permission policy
============================== ============================== ============================================

When stuck, read the agent's **stderr** (the editor usually exposes adapter
logs) — per the protocol, stderr is where the agent is allowed to log, so it is
the diagnostic channel. See ``examples.rst`` for capturing it directly.

Sources
-------

- Claude Code in Zed (beta) — https://zed.dev/blog/claude-code-via-acp
- Claude Agent (ACP) — https://zed.dev/acp/agent/claude-agent
- Adapter repo — https://github.com/zed-industries/claude-code-acp
- External agents config — https://zed.dev/docs/ai/external-agents
