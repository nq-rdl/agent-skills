ACP Wire Protocol Reference
===========================

The Agent Client Protocol is JSON-RPC 2.0 between a **Client** (the editor) and
an **Agent** (the coding AI). This file distills the normative spec at
https://agentclientprotocol.com/protocol/overview for *using* and *reasoning
about* ACP. For the exhaustive type definitions, see the schema:
https://agentclientprotocol.com/protocol/schema

.. contents:: Contents
   :local:
   :depth: 1

Roles and conventions
---------------------

- **Client** — the editor/IDE. Launches the agent, owns the filesystem and
  terminal, renders updates, and decides what the agent may do.
- **Agent** — the coding AI subprocess. Does the work and reports progress.

Two message kinds (JSON-RPC 2.0):

- **Method** — a request expecting a response (result or error).
- **Notification** — one-way, no response.

Conventions that hold everywhere:

- File paths **MUST** be absolute.
- Line numbers are **1-based**.
- Text shown to users defaults to Markdown.
- Content blocks reuse MCP's representations (text, image, audio, resource), so
  ACP and MCP share a vocabulary.

Transports
----------

**stdio (primary).** The client spawns the agent as a subprocess and speaks
JSON-RPC over its pipes:

- ``stdin`` — the client writes ACP messages to the agent here.
- ``stdout`` — the agent writes ACP messages to the client here.
- ``stderr`` — the agent may write free-form UTF-8 logs; the client may capture,
  forward, or ignore them.

Messages are newline-delimited (``\n``) and **MUST NOT** contain embedded
newlines. The agent **MUST NOT** write anything to ``stdout`` that is not a valid
ACP message — debug output goes to ``stderr``. This is the single most common
cause of a broken agent: a stray ``console.log``/``print`` to stdout corrupts the
stream.

**HTTP / WebSocket.** Streamable HTTP is a *draft proposal, in discussion* — not
yet specified. Treat stdio as the only stable transport today. Implementers may
define custom transports as long as JSON-RPC framing and message lifecycle are
preserved.

The prompt turn
---------------

The whole protocol orbits one loop. After setup, a *prompt turn* is: the client
sends one user turn, the agent streams progress, and the call resolves with a
reason it stopped.

::

   initialize                    Client → Agent   negotiate version + capabilities
   [authenticate]                Client → Agent   only if the agent requires it
   session/new | session/load    Client → Agent   obtain a sessionId
   ─── prompt turn (repeats) ──────────────────────────────────────────────
   session/prompt                Client → Agent   send the user's turn
     session/update  ……………………    Agent  → Client   streamed: text, tools, plan
     session/request_permission  Agent  → Client   approve a tool call?
       fs/* and terminal/*       Agent  → Client   use the editor's resources
   → returns { stopReason }      Agent  → Client   turn ends
   [session/cancel]              Client → Agent   interrupt (notification)

Method reference
----------------

Agent methods (Client → Agent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==================== ========= ==================================================
Method               Required  Purpose
==================== ========= ==================================================
``initialize``       yes       Handshake; negotiate protocol version + caps
``authenticate``     yes\*     Authenticate using a method the agent advertised
``session/new``      yes       Create a session; returns ``sessionId``
``session/prompt``   yes       Run one user turn; resolves with ``stopReason``
``session/load``     optional  Resume a prior session (if ``loadSession`` cap)
``session/set_mode`` optional  Switch agent mode (e.g. ask ↔ code)
==================== ========= ==================================================

\* ``authenticate`` is only exchanged when the agent returns ``authMethods`` and
the client is not already authenticated.

Client methods (Agent → Client)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

============================= ========= =========================================
Method                        Required  Purpose
============================= ========= =========================================
``session/request_permission`` yes      Ask the user to approve an action
``fs/read_text_file``         optional  Read a file via the editor
``fs/write_text_file``        optional  Write a file via the editor
``terminal/create``           optional  Start a command in the editor's terminal
``terminal/output``           optional  Read current output of a terminal
``terminal/wait_for_exit``    optional  Await terminal exit
``terminal/kill``             optional  Kill a terminal command
``terminal/release``          optional  Release terminal resources
============================= ========= =========================================

Notifications
~~~~~~~~~~~~~

==================== =============== =============================================
Notification         Direction       Purpose
==================== =============== =============================================
``session/update``   Agent → Client  Stream turn progress (see variants below)
``session/cancel``   Client → Agent  Cancel the in-flight prompt turn
==================== =============== =============================================

initialize
----------

The client opens with ``initialize`` to agree on a protocol version and discover
capabilities. ``protocolVersion`` is a single **integer** (the latest each side
supports), not a semver string.

.. code:: json

   // Client → Agent
   {
     "protocolVersion": 1,
     "clientCapabilities": {
       "fs": { "readTextFile": true, "writeTextFile": true },
       "terminal": true
     },
     "clientInfo": { "name": "zed", "version": "0.x" }
   }

.. code:: json

   // Agent → Client
   {
     "protocolVersion": 1,
     "agentCapabilities": {
       "loadSession": true,
       "promptCapabilities": { "image": true, "audio": false, "embeddedContext": true },
       "mcpCapabilities": { "http": true, "sse": false }
     },
     "agentInfo": { "name": "claude-code", "version": "x.y" },
     "authMethods": []
   }

Each side **MUST** only use features the other advertised. Client and agent
**MUST** agree on a protocol version before any session setup.

Sessions
--------

- ``session/new`` — create a session. The client passes the working directory
  (``cwd``, absolute) and any MCP servers the agent should connect to. Returns a
  ``sessionId`` used by every later call.
- ``session/load`` — resume a previous session by id (only if the agent reported
  ``loadSession``). The agent replays history via ``session/update`` before
  responding.

session/prompt and stop reasons
-------------------------------

``session/prompt`` carries the user's turn as an array of content blocks and
**blocks until the turn ends**, then resolves with a ``stopReason``:

============================ ===================================================
``stopReason``               Meaning
============================ ===================================================
``end_turn``                 Model finished without requesting more tools
``max_tokens``               Token limit reached
``max_turn_requests``        Too many model requests in one turn
``refusal``                  Agent declined to continue
``cancelled``                Client sent ``session/cancel``
============================ ===================================================

While the turn runs, the agent emits ``session/update`` notifications. The
client may interrupt at any time with the ``session/cancel`` notification; the
turn then resolves with ``stopReason: "cancelled"``.

session/update variants
-----------------------

Every ``session/update`` carries a ``sessionUpdate`` discriminator naming the
payload shape:

========================== ====================================================
``sessionUpdate``          Payload
========================== ====================================================
``agent_message_chunk``    Incremental assistant text (the visible reply)
``agent_thought_chunk``    Incremental reasoning/thinking text
``tool_call``              A new tool invocation (id, title, kind, status)
``tool_call_update``       Changed fields of an existing tool call
``plan``                   The agent's task plan (entries: content/priority/status)
``available_commands_update`` The set of slash commands the agent offers
``current_mode_update``    The agent's active mode changed
========================== ====================================================

Permissions
-----------

When the agent wants to do something requiring consent (e.g. run a command, edit
a file), it calls ``session/request_permission`` with the proposed tool call and
a set of options. The client surfaces this to the user (or auto-answers by
policy) and returns the chosen option. This is the trust hinge of ACP: the agent
proposes, the client/user disposes.

Content blocks
--------------

Prompts and updates carry typed content blocks, mirroring MCP:

- ``text`` — Markdown text.
- ``image`` / ``audio`` — base64 media (gated by ``promptCapabilities``).
- ``resource`` — embedded resource contents (gated by ``embeddedContext``).
- ``resource_link`` — a reference to a resource by URI.

Tool calls
----------

A tool call reports something the agent is doing. Fields:

- ``toolCallId`` (required) — unique within the session.
- ``title`` (required) — human-readable description.
- ``kind`` — one of ``read``, ``edit``, ``delete``, ``move``, ``search``,
  ``execute``, ``think``, ``fetch``, ``other``.
- ``status`` — ``pending`` → ``in_progress`` → ``completed`` | ``failed``
  (defaults to ``pending``).
- ``content`` — output produced; ``locations`` — affected file paths;
  ``rawInput`` / ``rawOutput`` — raw tool I/O.

The first report uses ``sessionUpdate: "tool_call"``. Subsequent
``tool_call_update`` notifications send **only changed fields** (``toolCallId``
plus whatever moved). ``locations`` lets the editor "follow along" — e.g. jump to
the file the agent is editing.

Filesystem and terminal (client-provided)
-----------------------------------------

Rather than touching disk directly, an agent can ask the editor to act, so edits
flow through the editor's buffers, undo history, and permission model:

- ``fs/read_text_file`` / ``fs/write_text_file`` — read/write through the editor
  (honors unsaved buffers). Gated by ``clientCapabilities.fs``.
- ``terminal/create`` → ``terminal/output`` / ``terminal/wait_for_exit`` →
  ``terminal/kill`` → ``terminal/release`` — run commands in the editor's
  terminal with live output. Gated by ``clientCapabilities.terminal``.

Session modes and slash commands
--------------------------------

- **Modes** — an agent may expose modes (e.g. *ask* vs *code*); the client
  switches with ``session/set_mode`` and learns of changes via
  ``current_mode_update``. See https://agentclientprotocol.com/protocol/session-modes
- **Slash commands** — an agent advertises commands (e.g. ``/test``) via
  ``available_commands_update``; the client shows them to the user. See
  https://agentclientprotocol.com/protocol/slash-commands

Extensibility
-------------

ACP is designed to extend without forking:

- ``_meta`` fields may be attached to most objects for implementation-specific
  data.
- Custom methods/notifications use an underscore prefix (e.g. ``_myorg/foo``).

Unknown ``_``-prefixed fields and methods must be tolerated. See
https://agentclientprotocol.com/protocol/extensibility

Full schema
-----------

The complete, authoritative type definitions (every request, response, and
notification) live in the schema document — consult it when you need an exact
field: https://agentclientprotocol.com/protocol/schema
