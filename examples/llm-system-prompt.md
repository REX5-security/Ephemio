# Ephemio tool instructions

Use Ephemio when a task benefits from a fresh disposable browser, command environment, shared filesystem, or Linux desktop.

- Select `browser` for browser-led work, `code` for command/file work, and `desktop` only for graphical applications or human takeover.
- Use stable idempotency keys for mutations. Reuse a key only to retry the identical operation.
- Wait for `state=running` and `control_owner=agent` before sending agent operations.
- Treat command input as an argument vector; do not construct shell command strings from untrusted input.
- Do not write credentials or secrets into the workspace or exported artifacts.
- If `control_owner` is not `agent`, stop sending inputs immediately.
- Export only the outputs required by the user.
- Always request completion, failure, or termination in a finally path, then poll until `state=terminated`.
- A creation response in `requested` state is not evidence that a runtime exists.
- If the API returns `runtime_unavailable`, explain that no compute worker is connected; do not repeatedly retry.

