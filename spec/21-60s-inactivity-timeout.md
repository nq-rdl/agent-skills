# Issue #21: [skill:pi-rpc] 60s inactivity timeout kills sessions before slow providers respond to long prompts

## Summary
The 60-second inactivity timeout in `pi-rpc` terminates sessions prematurely when a slow provider takes longer to begin streaming a response for a complex prompt. The issue requested that the timeout be made configurable per-session or increased by default, especially distinguishing between the initial processing time and mid-stream stalling.

## Category
skill-enhancement

## Impact Assessment
- **Scope**:
  - `skills/pi-rpc/scripts/proto/pirpc/v1/session.proto`
  - Generated protobuf and connect-go code (`skills/pi-rpc/scripts/gen/pirpc/v1/*`)
  - `skills/pi-rpc/scripts/session/manager.go`
  - `skills/pi-rpc/scripts/session/session.go`
  - `skills/pi-rpc/scripts/handler/session_handler.go`
  - `skills/pi-rpc/scripts/cmd/pi-cli/session.go`
- **Risk**: Low — Adding an optional timeout field and preserving the 60-second default for unspecified or zero values ensures full backward compatibility with existing clients.
- **Effort**: Small — Standard Protobuf RPC message update with straightforward parameter plumbing through the Go server stack.
- **Dependencies**: Need to run `buf generate` via `make generate` within the `skills/pi-rpc/scripts/` directory to regenerate Go stubs.

## Solution

### Approach
Add an optional `timeout_seconds` parameter to the `CreateRequest` message. Pass this parameter from the RPC handler down to the session configuration. Update the session manager to use this configuration. To ensure the inactivity watchdog behaves well, if `timeout_seconds` is zero or not provided, the session will continue to default to the existing 60-second `DefaultInactivityTimeout`.

### Changes
1. **`skills/pi-rpc/scripts/proto/pirpc/v1/session.proto`**
   - Add `int32 timeout_seconds = 5;` to the `CreateRequest` message.
   - Run `cd skills/pi-rpc/scripts && make generate` to rebuild the Go stubs.
2. **`skills/pi-rpc/scripts/session/session.go`**
   - Update `Config` struct (ensure `InactivityTimeout time.Duration` is present, it already is).
   - The logic `if timeout == 0 { timeout = DefaultInactivityTimeout }` in `NewSession` will naturally apply the default.
3. **`skills/pi-rpc/scripts/session/manager.go`**
   - Update `Manager.Create` signature to accept `timeoutSeconds int32`: `func (m *Manager) Create(ctx context.Context, provider, model, cwd, thinkingLevel string, timeoutSeconds int32) (string, error)`.
   - In `Manager.Create`, map `timeoutSeconds` to `time.Duration(timeoutSeconds) * time.Second` and set `InactivityTimeout` on the `Config` struct.
4. **`skills/pi-rpc/scripts/handler/session_handler.go`**
   - In `SessionHandler.Create()`, retrieve `req.Msg.TimeoutSeconds` from the request.
   - Pass it to `h.mgr.Create()`.
5. **`skills/pi-rpc/scripts/cmd/pi-cli/session.go`**
   - Add a `--timeout` int flag (default 0) to the `session create` Cobra command.
   - Pass this value to the Connect client `CreateRequest` as `TimeoutSeconds`.

### Validation
1. Verify the Go tests pass by running `make test` inside `skills/pi-rpc/scripts/`.
2. Start the local server `make serve`.
3. Test creating a session using `pi-cli` with `--timeout 300`.
4. Trigger a long prompt using a known slow provider or simulate a slow provider. Ensure the session outlives the default 60s timeout but gets killed if it exceeds the custom 300s timeout.

## Open Questions
- Is distinguishing between "waiting for first token" vs "stalled mid-stream" strictly necessary for this fix, or is making the total inactivity timeout configurable sufficient for orchestration needs? The configurable timeout should solve the immediate orchestration issue gracefully.
