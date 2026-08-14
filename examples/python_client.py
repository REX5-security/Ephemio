#!/usr/bin/env python3
"""Minimal dependency-free Ephemio preview client."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid


class EphemioError(RuntimeError):
    pass


class Ephemio:
    def __init__(self, token: str, base_url: str = "https://ephemio.com/api/v1") -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"}

    def request(self, method: str, path: str, body: dict | None = None, idempotency_key: str | None = None) -> dict:
        headers = dict(self.headers)
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body, separators=(",", ":")).encode()
        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key
        request = urllib.request.Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            details = error.read().decode(errors="replace")
            raise EphemioError(f"Ephemio returned HTTP {error.code}: {details}") from error

    def wait_for(self, workload_id: str, target: str, timeout: int = 120) -> dict:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            workload = self.request("GET", f"/workloads/{workload_id}")["workload"]
            if workload["state"] == target:
                return workload
            if workload["state"] == "terminated" and target != "terminated":
                raise EphemioError("Workload terminated before reaching the requested state")
            time.sleep(2)
        raise TimeoutError(f"Workload did not reach {target!r}")


def main() -> None:
    client = Ephemio(os.environ["EPHEMIO_API_TOKEN"], os.getenv("EPHEMIO_API_BASE", "https://ephemio.com/api/v1"))
    task_id = uuid.uuid4().hex
    workload_id = None
    completed = False
    try:
        created = client.request(
            "POST",
            "/workloads",
            {"profile": "code", "execution_policy": "autonomous", "requested_seconds": 300, "idle_policy": "5"},
            f"{task_id}-create",
        )
        workload_id = created["workload"]["public_id"]
        client.wait_for(workload_id, "running")
        client.request("POST", f"/workloads/{workload_id}/files/write", {"path": "/hello.txt", "contents": "hello"})
        result = client.request(
            "POST",
            f"/workloads/{workload_id}/commands",
            {"arguments": ["php", "-r", "echo strtoupper(file_get_contents('hello.txt'));"], "timeout_seconds": 30},
        )
        print(result["result"]["stdout"])
        client.request("POST", f"/workloads/{workload_id}/complete", {"reason": "example_completed"}, f"{task_id}-complete")
        completed = True
        client.wait_for(workload_id, "terminated")
    finally:
        if workload_id and not completed:
            try:
                client.request("POST", f"/workloads/{workload_id}/terminate", {"reason": "client_cleanup"}, f"{task_id}-terminate")
            except Exception as error:
                print(f"Cleanup request failed: {error}")


if __name__ == "__main__":
    main()

