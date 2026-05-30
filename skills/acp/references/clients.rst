ACP Clients (Editors) and Connecting an Agent
=============================================

The **client** is the editor/IDE. It launches the agent, exposes the
filesystem/terminal, mediates permissions, and renders the agent's streamed
updates. This file covers what a client provides and how to connect an agent in
the common editors.

.. contents:: Contents
   :local:
   :depth: 1

What the client is responsible for
----------------------------------

When you "connect an agent", the editor takes on these jobs (see ``protocol.rst``
for the methods behind each):

- **Spawn** the agent subprocess (command + args + env) and run ``initialize``.
- **Advertise capabilities** — whether it offers ``fs/*`` and ``terminal/*`` so
  edits and commands flow through the editor.
- **Render updates** — turn ``session/update`` notifications into UI (assistant
  text, tool calls, plans, diffs).
- **Mediate permissions** — answer ``session/request_permission``, usually by
  asking the user.
- **Forward MCP servers** — pass the user's configured MCP tools to the agent.

Zed
---

Zed has native ACP support and is the reference client. Built-in agents (Claude
Agent, Gemini CLI, Codex) need no config — open the agent panel (``cmd-?`` /
``ctrl-?``) and pick one.

To add any other agent, declare it under ``agent_servers`` in ``settings.json``.

**Custom agent** (you supply the command):

.. code:: json

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

**Registry agent** (Zed installs/updates it; override env if needed):

.. code:: json

   {
     "agent_servers": {
       "claude-acp": {
         "type": "registry",
         "env": { "CLAUDE_CODE_EXECUTABLE": "/path/to/claude" }
       }
     }
   }

The ``command``/``args``/``env`` triple is the universal shape: it is exactly the
process the editor spawns to speak ACP over stdio. Docs:
https://zed.dev/docs/ai/external-agents

Neovim
------

No native support; use a plugin that implements the ACP client:

- **CodeCompanion** — chat/agent plugin with ACP support.
- **avante.nvim** (``yetone/avante.nvim``).
- **agentic.nvim** (``carlos-algms/agentic.nvim``).

Each plugin configures agents with the same idea as Zed — a command to launch
the adapter — using that plugin's config schema.

VS Code
-------

Use the **"ACP Client"** extension (by *formulahendry*) from the Marketplace,
then point it at an agent command. (Note: GitHub Copilot CLI also ships its own
ACP *agent* mode — that is the agent side, not the client.)

JetBrains IDEs
--------------

Recent JetBrains IDEs include ACP support through the AI Assistant; connect an
external agent from the AI Assistant settings. See JetBrains' AI Assistant docs.

Emacs
-----

Use **agent-shell.el**, which speaks ACP and can drive ACP agents from a shell
buffer.

Other clients
-------------

ACP clients also exist for **Obsidian** ("Agent Client" plugin), **Chrome** (an
ACP extension/PWA), **Unity** (UnityACPClient / Unity Agent Client), and a range
of CLI/desktop tools (acpx, Nori CLI, Toad, Agent Studio, Jockey, …). The set
grows quickly — check the clients directory for current options.

Building a client
-----------------

If you are embedding an agent in your own app rather than using an editor, use a
language SDK (see below) and optionally a UI component kit:

- **ACP Components** — frontend components for agent UIs.
- **agent-client-kernel** — Jupyter integration.
- **stdio Bus** — transport-level routing kernel.

Language SDKs: Python, TypeScript, Java, Kotlin, Rust —
https://agentclientprotocol.com/libraries/python (swap the trailing segment for
the language you want). Building is out of scope for this skill, but the SDKs are
where to start.

The directory is the source of truth
-------------------------------------

Editor support and plugin names move fast. For a current list:
https://agentclientprotocol.com/get-started/clients
