# Issue #22: [skill:pi-rpc] RPC server uses wrong provider name — `openai` vs `openai-codex` OAuth mismatch

## Summary
The pi-rpc server incorrectly defaults to the `openai` provider, which fails when the user has authenticated via OAuth (`openai-codex` provider). Furthermore, early subprocess failures (like missing API keys) are masked by the inactivity timeout monitor, which blindly overwrites the existing error message.

## Category
skill-bug

## Impact Assessment
- **Scope**: `skills/pi-rpc/scripts/cmd/pi-server/main.go`, `skills/pi-rpc/scripts/cmd/pi-cli/serve.go`, `skills/pi-rpc/scripts/session/session.go`.
- **Risk**: Low — The changes only improve error reporting and sensible default detection without altering core agent execution.
- **Effort**: Small — Consists of reading a local JSON file to detect the default provider and preventing the inactivity monitor from overwriting existing error messages.
- **Dependencies**: None.

## Solution

### Approach
1. **Auto-detect default provider**: Update `main.go` and `serve.go` to auto-detect the default provider by inspecting `~/.pi/agent/auth.json`. If the `openai-codex` key exists, default to `openai-codex`. If not (or if the file doesn't exist), fallback to `openai`.
2. **Prevent error masking**: Update `session.go`'s `monitorInactivity` function. When it triggers a timeout, it currently overwrites `s.errorMsg` unconditionally. It should instead preserve any existing error message (such as "No API key found") so that authentic root causes are surfaced instead of misleading inactivity timeouts.

### Changes
1. **`skills/pi-rpc/scripts/cmd/pi-server/main.go` and `skills/pi-rpc/scripts/cmd/pi-cli/serve.go`**
   - Implement an `autoDetectProvider()` helper function that reads `~/.pi/agent/auth.json`.
   - If the file can be unmarshaled into a map and contains the key `openai-codex`, return `"openai-codex"`.
   - Otherwise, return `"openai"`.
   - Update the initialization of `defaultProvider` to use `autoDetectProvider()` when `os.Getenv("PI_DEFAULT_PROVIDER")` is empty.

2. **`skills/pi-rpc/scripts/session/session.go`**
   - In the `monitorInactivity` method, locate the block where `s.errorMsg` is assigned:
     ```go
     s.errorMsg = fmt.Sprintf("session killed: no activity for %s...", ...)
     ```
   - Modify it to check if `s.errorMsg` is already populated. If it is, append the timeout message rather than overwriting it, or keep the existing message as the primary error.
     ```go
     timeoutMsg := fmt.Sprintf("session killed: no activity for %s (provider=%s, model=%s)", s.inactivityTimeout, s.provider, s.model)
     if s.errorMsg == "" {
         s.errorMsg = timeoutMsg
     } else {
         s.errorMsg = s.errorMsg + "\n" + timeoutMsg
     }
     ```

### Validation
- Run `pixi run validate-skills` to ensure the skill specification remains valid.
- Build the Go CLI and server: `cd skills/pi-rpc/scripts && make test build-cli build-server`.
- Run tests (`make test`) to ensure no regressions in `session.go`.
- Manually run `pi-cli serve` without setting `PI_DEFAULT_PROVIDER` and observe that it correctly defaults to `openai-codex` if `~/.pi/agent/auth.json` is configured appropriately.
- Simulate a missing provider token and confirm that the resulting error message properly surfaces the "No API key found" message instead of only reporting an inactivity timeout.

## Open Questions
- Should `autoDetectProvider()` handle other potential provider names in the future? (Currently limiting scope to resolving the `openai` vs `openai-codex` mismatch).
