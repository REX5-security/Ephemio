#!/usr/bin/env bash

set -Eeuo pipefail

: "${EPHEMIO_API_TOKEN:?Set EPHEMIO_API_TOKEN to a scoped beta credential}"

readonly API_BASE="${EPHEMIO_API_BASE:-https://ephemio.com/api/v1}"
readonly TASK_KEY="example-$(date +%s)-$$"
workload_id=""
finished=false

api() {
    curl --fail-with-body --silent --show-error \
        --header "Authorization: Bearer ${EPHEMIO_API_TOKEN}" \
        "$@"
}

cleanup() {
    if [[ -n "$workload_id" && "$finished" != true ]]; then
        api --request POST \
            --header "Idempotency-Key: ${TASK_KEY}-terminate" \
            --header 'Content-Type: application/json' \
            --data '{"reason":"client_cleanup"}' \
            "${API_BASE}/workloads/${workload_id}/terminate" >/dev/null || true
    fi
}
trap cleanup EXIT

created=$(api --request POST \
    --header "Idempotency-Key: ${TASK_KEY}-create" \
    --header 'Content-Type: application/json' \
    --data '{"profile":"code","execution_policy":"autonomous","requested_seconds":300,"idle_policy":"5"}' \
    "${API_BASE}/workloads")

workload_id=$(php -r '$v=json_decode(stream_get_contents(STDIN), true, 32, JSON_THROW_ON_ERROR); echo $v["workload"]["public_id"];' <<<"$created")

for attempt in {1..30}; do
    workload=$(api "${API_BASE}/workloads/${workload_id}")
    state=$(php -r '$v=json_decode(stream_get_contents(STDIN), true, 32, JSON_THROW_ON_ERROR); echo $v["workload"]["state"];' <<<"$workload")
    [[ "$state" == running ]] && break
    [[ "$state" == stopping || "$state" == terminated ]] && { echo "Workload stopped before execution" >&2; exit 1; }
    sleep 2
done
[[ "${state:-}" == running ]] || { echo "Workload did not become ready" >&2; exit 1; }

api --request POST \
    --header 'Content-Type: application/json' \
    --data '{"path":"/numbers.json","contents":"[2,3,5,7]"}' \
    "${API_BASE}/workloads/${workload_id}/files/write"

api --request POST \
    --header 'Content-Type: application/json' \
    --data '{"arguments":["php","-r","$v=json_decode(file_get_contents(\"numbers.json\"),true); file_put_contents(\"sum.txt\",(string)array_sum($v));"]}' \
    "${API_BASE}/workloads/${workload_id}/commands"

api --request POST \
    --header 'Content-Type: application/json' \
    --data '{"path":"/sum.txt","name":"sum.txt"}' \
    "${API_BASE}/workloads/${workload_id}/artifacts"

api --request POST \
    --header "Idempotency-Key: ${TASK_KEY}-complete" \
    --header 'Content-Type: application/json' \
    --data '{"reason":"example_completed"}' \
    "${API_BASE}/workloads/${workload_id}/complete"
finished=true

