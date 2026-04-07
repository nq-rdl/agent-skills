# Issue 21: 60s inactivity timeout kills sessions before slow providers respond to long prompts

## Summary
The 60s inactivity timeout in `Session` terminates the session if a response doesn't come back in time. This is problematic for slow providers or long prompts.

## Category
Bug/Feature

## Impact Assessment
- Scope: `Session` creation and configuration.
- Risk: Low.
- Effort: Low.
- Dependencies: None.

## Solution
### Approach
1. Add an optional `timeout_seconds` parameter to the `CreateRequest` Protobuf message in `skills/pi-rpc/scripts/proto/pirpc/v1/session.proto`.
2. Regenerate the Protobuf code using `make generate` in `skills/pi-rpc/scripts`.
3. Update `SessionHandler.Create` in `skills/pi-rpc/scripts/handler/session_handler.go` to extract `timeout_seconds` and pass it down.
4. Update `Manager.Create` in `skills/pi-rpc/scripts/session/manager.go` to accept the timeout parameter and set it in `session.Config.InactivityTimeout`.

### Changes
- `skills/pi-rpc/scripts/proto/pirpc/v1/session.proto`
- `skills/pi-rpc/scripts/handler/session_handler.go`
- `skills/pi-rpc/scripts/session/manager.go`

### Validation
- Verify that a `CreateRequest` with `timeout_seconds` correctly configures the timeout.
- Test that the session does not timeout earlier than `timeout_seconds`.

## Open Questions
None.
