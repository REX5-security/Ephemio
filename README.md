# Ephemio

Disposable computers for AI agents.

[Ephemio](https://ephemio.com/) gives a computer-using LLM a fresh, short-lived workspace for browser automation, code execution, file processing, and Linux desktop tasks. Every workload has an explicit lifetime and control owner, and its workspace is destroyed when the workload terminates.

Ephemio is designed for agents that need to use a computer—not for hosting an agent's model or reasoning loop.

> **Private beta:** The API shown here is a preview. Access, runtime capacity, endpoint details, and pricing may change. A workload reaching `requested` means the control plane accepted it; execution begins only when a runtime worker is connected.

## Why give an agent a disposable workspace?

- **Start clean:** each task begins without cookies, files, credentials, or state left by another task.
- **Combine tools:** browse the web, run programs, transform files, and use a graphical desktop inside one workload.
- **Bound the task:** duration, idle policy, resource use, and a two-hour hard limit are enforced outside the guest.
- **Hand off safely:** an agent can request human help, pause its own input, and resume after the human returns control.
- **Clean up by default:** success, failure, cancellation, and expiry all pass through destructive cleanup.
- **Retry safely:** mutating API requests use idempotency keys, so an agent can retry after a timeout without creating duplicate work.

## Example use cases

### Autonomous browser work

Give an agent a clean browser to navigate a site, fill forms, collect visible information, and save a screenshot or downloaded result as an artifact. This is useful for QA checks, repetitive back-office workflows, public-data collection, and research tasks that require interaction rather than a simple HTTP request.

### Isolated code and file processing

Upload input files, run a command as an argument vector, inspect the result, and export selected outputs. Examples include converting documents, analyzing a repository, generating reports, validating data, and running untrusted build steps in an environment intended to be discarded.

### Mixed browser and local-tool workflows

Use a browser and local programs against the same ephemeral filesystem. An agent can download a dataset, process it with Python or PHP, open the generated report in the browser, and export only the final artifact.

### Human fallback for GUI tasks

Launch a desktop with `autonomous_with_fallback`. If the agent encounters a CAPTCHA, ambiguous approval, or unfamiliar GUI state, it can request intervention. Ephemio pauses agent input, gives the authorized human a short-lived Guacamole connection, and returns control to the agent only after an explicit resume.

### Reproducible software checks

Run installation, build, lint, and test commands in a fresh environment. The workspace can be destroyed afterward, reducing the risk that cached dependencies or previous runs influence the result.

## API at a glance

The preview API lives at:

```text
https://ephemio.com/api/v1
```

Authenticate with a scoped bearer credential:

```http
Authorization: Bearer eph_...
```

Available scopes are `workloads:read`, `workloads:write`, and `workloads:intervene`. Keep credentials out of prompts, source control, command output, and artifacts.

### 1. Create a workload

```bash
curl --fail-with-body \
  --request POST \
  --header "Authorization: Bearer $EPHEMIO_API_TOKEN" \
  --header "Idempotency-Key: research-2026-08-14-create" \
  --header "Content-Type: application/json" \
  --data '{
    "profile": "browser",
    "execution_policy": "autonomous",
    "requested_seconds": 900,
    "idle_policy": "15"
  }' \
  https://ephemio.com/api/v1/workloads
```

Profiles:

| Profile | Intended capabilities |
| --- | --- |
| `browser` | Headless browser actions plus shared files and commands |
| `code` | Commands, files, and artifact export |
| `desktop` | Graphical Linux desktop and optional human takeover |

Execution policies:

| Policy | Behavior |
| --- | --- |
| `autonomous` | Agent retains control; human takeover is disabled |
| `supervised` | Human observation or control is expected |
| `autonomous_with_fallback` | Agent runs normally and may explicitly request help |

Save the returned `workload.public_id`. Never infer readiness from the creation response; poll until `workload.state` is `running`.

### 2. Inspect the workload

```bash
curl --fail-with-body \
  --header "Authorization: Bearer $EPHEMIO_API_TOKEN" \
  "https://ephemio.com/api/v1/workloads/$WORKLOAD_ID"
```

Normal lifecycle:

```text
requested -> reserved -> provisioning -> ready -> running
running -> stopping -> terminated
```

`terminated` is final and means runtime destruction has been observed. Do not treat `stopping` as cleanup completion.

### 3. Use the workspace

Write a file:

```bash
curl --fail-with-body \
  --request POST \
  --header "Authorization: Bearer $EPHEMIO_API_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"path":"/input.txt","contents":"hello from an agent","overwrite":false}' \
  "https://ephemio.com/api/v1/workloads/$WORKLOAD_ID/files/write"
```

Run a command without a shell:

```bash
curl --fail-with-body \
  --request POST \
  --header "Authorization: Bearer $EPHEMIO_API_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{
    "arguments":["php","-r","echo strtoupper(file_get_contents(\"input.txt\"));"],
    "working_directory":"/",
    "timeout_seconds":60
  }' \
  "https://ephemio.com/api/v1/workloads/$WORKLOAD_ID/commands"
```

Drive a browser:

```bash
curl --fail-with-body \
  --request POST \
  --header "Authorization: Bearer $EPHEMIO_API_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{
    "url":"https://example.com/",
    "actions":[],
    "screenshot_path":"/example.png",
    "timeout_seconds":30
  }' \
  "https://ephemio.com/api/v1/workloads/$WORKLOAD_ID/browser/actions"
```

Supported browser action types are `click`, `fill`, `press`, and bounded `wait`. The API intentionally does not accept arbitrary page JavaScript.

Export an artifact:

```bash
curl --fail-with-body \
  --request POST \
  --header "Authorization: Bearer $EPHEMIO_API_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"path":"/example.png","name":"example.png"}' \
  "https://ephemio.com/api/v1/workloads/$WORKLOAD_ID/artifacts"
```

### 4. Always terminate

Put cleanup in a `finally` block. Completion and failure both request destruction; neither bypasses it.

```bash
curl --fail-with-body \
  --request POST \
  --header "Authorization: Bearer $EPHEMIO_API_TOKEN" \
  --header "Idempotency-Key: research-2026-08-14-complete" \
  --header "Content-Type: application/json" \
  --data '{"reason":"agent_completed"}' \
  "https://ephemio.com/api/v1/workloads/$WORKLOAD_ID/complete"
```

Use `/fail` when the task fails and `/terminate` when it is cancelled. Continue polling until the state becomes `terminated`.

## Instructions for LLM agents

When Ephemio is available as an API tool, follow this operating policy:

1. Choose the narrowest profile that can complete the task.
2. Use `autonomous_with_fallback` only when human intervention is genuinely useful; otherwise use `autonomous`.
3. Request the shortest realistic duration and an idle timeout.
4. Generate a stable, unique idempotency key for every logical mutation and reuse it only when retrying that exact mutation.
5. Poll workload state with bounded backoff. Start runtime operations only in `running` with `control_owner=agent`.
6. Pass commands as argument arrays. Never concatenate untrusted values into a shell command.
7. Keep all task files under the workspace root. Export only outputs the user requested.
8. Never place API tokens, passwords, session cookies, or private keys in workspace files or artifacts.
9. If intervention is needed, request it explicitly and stop sending agent input until control returns.
10. In a `finally` path, complete, fail, or terminate the workload and confirm `terminated`.

A suitable system-prompt fragment is available in [`examples/llm-system-prompt.md`](examples/llm-system-prompt.md).

## More examples

- [`examples/curl-workflow.sh`](examples/curl-workflow.sh) — complete Bash lifecycle with polling and cleanup.
- [`examples/python_client.py`](examples/python_client.py) — dependency-free Python client and code-workload example.
- [`examples/llm-tool-schema.json`](examples/llm-tool-schema.json) — compact function schema for an LLM tool wrapper.

## Errors and retries

Errors use a stable JSON shape:

```json
{
  "error": {
    "code": "invalid_state",
    "message": "Workload transition is not allowed."
  }
}
```

Retry network failures, `429`, and transient `5xx` responses with bounded exponential backoff. Reuse the same idempotency key and identical body when retrying a mutation. Do not retry authorization, scope, validation, or invalid-state errors without changing the underlying request or state.

## Safety and acceptable use

Ephemio is not an anonymity service and is not intended to bypass third-party access controls. Do not use it for phishing, spam, malware, credential attacks, denial of service, unauthorized access, evasion, or unlawful activity. Agents remain responsible for respecting site policies, user authorization, and applicable law.

## Status and access

Ephemio is preparing a private beta. Runtime-backed API access is issued only to authorized testers.

- Product: [ephemio.com](https://ephemio.com/)
- Beta enquiries: [ephemio.com/contact](https://ephemio.com/contact)
- API-oriented machine summary: [ephemio.com/llms.txt](https://ephemio.com/llms.txt)

