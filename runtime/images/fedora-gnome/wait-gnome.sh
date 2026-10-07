#!/usr/bin/with-contenv bash
set -eu
for attempt in {1..180}; do
  if [ -S "${XDG_RUNTIME_DIR:-/config/.XDG}/ephemio-input.sock" ]; then
    exit 0
  fi
  sleep 0.5
done
echo 'GNOME input did not initialize' >&2
exit 1
