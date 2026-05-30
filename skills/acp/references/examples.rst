ACP Worked Examples
===================

Copy-paste setups, plus a hand-driven session that shows the raw protocol. The
first two are the realistic day-to-day workflows; the third is the fastest way
to actually *understand* what flows over the wire.

.. contents:: Contents
   :local:
   :depth: 1

Example 1 — Claude Code in Zed
------------------------------

Claude Code is built into Zed, so there is no config to write:

1. Open your project in Zed.
2. Open the agent panel: ``cmd-?`` (macOS) / ``ctrl-?`` (Linux).
3. Agent selector → **Claude Code**. First run installs the managed adapter and
   prompts you to sign in to your Claude account.
4. Prompt away — edits and tool calls render inline, with permission prompts.

Optional: pin the adapter to a specific Claude Code binary via ``settings.json``:

.. code:: json

   {
     "agent_servers": {
       "claude-acp": {
         "type": "registry",
         "env": { "CLAUDE_CODE_EXECUTABLE": "/usr/local/bin/claude" }
       }
     }
   }

Example 2 — pi (pi.dev) in Zed
------------------------------

pi is not built in, so add it as a custom agent. Prerequisites: Node.js 22+,
``pi`` installed globally and configured with a model provider.

``settings.json``:

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

Then open the agent panel, pick **pi**, and prompt. ``pi-acp`` launches
``pi --mode rpc`` behind the scenes and bridges it to ACP. pi skills appear as
``/skill:<name>`` commands.

The same shape works for any agent: set ``command``/``args`` to whatever launches
its adapter.

Example 3 — drive an agent by hand (raw stdio)
----------------------------------------------

An ACP agent is just a process that reads JSON-RPC on stdin and writes it on
stdout. Talking to one yourself demystifies the protocol. We use ``pi-acp``
because it runs standalone with ``npx`` (any stdio adapter works).

The message sequence (one JSON object per line — newline-delimited, no embedded
newlines):

.. code:: json

   {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":1,"clientCapabilities":{"fs":{"readTextFile":true,"writeTextFile":true},"terminal":true}}}
   {"jsonrpc":"2.0","id":2,"method":"session/new","params":{"cwd":"/absolute/path/to/project","mcpServers":[]}}
   {"jsonrpc":"2.0","id":3,"method":"session/prompt","params":{"sessionId":"SESSION_ID_FROM_STEP_2","prompt":[{"type":"text","text":"List the files in this directory and summarize the project."}]}}

What you will see on stdout:

- a response to ``id:1`` with the agent's ``protocolVersion`` + ``agentCapabilities``,
- a response to ``id:2`` containing the new ``sessionId``,
- a stream of ``session/update`` notifications (``agent_message_chunk``,
  ``tool_call``, ``tool_call_update``, ``plan`` …),
- finally a response to ``id:3`` with ``{ "stopReason": "end_turn" }``.

Because ``session/prompt`` needs the ``sessionId`` from step 2, the simplest way
to try this is **interactively** — start the agent, then paste the lines one at a
time, reading each response before sending the next:

.. code:: bash

   # Start the agent; it now reads JSON-RPC on stdin, writes on stdout.
   npx -y pi-acp
   # Paste the `initialize` line, press Enter, read the response.
   # Paste `session/new`, press Enter, copy the sessionId from the response.
   # Paste `session/prompt` (with that sessionId) and watch the updates stream.

Scripted variant (advanced) — keep stdin open with a coprocess so you can read
the ``sessionId`` before prompting:

.. code:: bash

   coproc AGENT { npx -y pi-acp; }
   send() { printf '%s\n' "$1" >&"${AGENT[1]}"; }

   send '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":1,"clientCapabilities":{"fs":{"readTextFile":true,"writeTextFile":true},"terminal":true}}}'
   read -r line <&"${AGENT[0]}"; echo "init  → $line"

   send '{"jsonrpc":"2.0","id":2,"method":"session/new","params":{"cwd":"'"$PWD"'","mcpServers":[]}}'
   read -r line <&"${AGENT[0]}"; echo "new   → $line"
   SID=$(printf '%s' "$line" | jq -r '.result.sessionId')

   send '{"jsonrpc":"2.0","id":3,"method":"session/prompt","params":{"sessionId":"'"$SID"'","prompt":[{"type":"text","text":"List the files here."}]}}'
   # Read lines until the response to id:3 arrives:
   while read -r line <&"${AGENT[0]}"; do
     echo "update→ $line"
     printf '%s' "$line" | jq -e '.id==3' >/dev/null 2>&1 && break
   done

These payloads are illustrative — confirm exact fields against the schema:
https://agentclientprotocol.com/protocol/schema

Example 4 — capture stderr for debugging
-----------------------------------------

The protocol forbids the agent from writing non-ACP data to stdout, so logs go
to **stderr**. When an agent misbehaves, split the streams:

.. code:: bash

   npx -y pi-acp 2> acp-agent.log
   # stdout stays clean for ACP messages; diagnostics land in acp-agent.log

In an editor, the equivalent is the adapter/agent log panel — the first place to
look when prompts hang or sessions fail.
