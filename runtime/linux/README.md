# Native Linux desktop prototype

This runs the Ubuntu KDE Webtop image used by `../PDWSLC/` with Docker
instead of `wslc.exe`. A graphical host desktop, WSL and xrdp are unnecessary.
The browser connects to Webtop's own HTTPS streaming endpoint.

Status: Compose configuration validated locally. The hosted POC has now been
checked on a native Linux VPS for desktop streaming, browser audio, input and
file transfer. GPU acceleration and concurrent capacity remain unverified. This
is the desktop foundation for Ephemio's planned ephemeral desktop service.
This standalone Compose setup has no customer accounts or automatic expiry;
those are implemented by the separate [host service](../host/README.md).

## Run on a Linux host

Install Docker Engine and the Docker Compose v2 plugin. From this directory:

```bash
docker compose -p ephemio-desktop-test up -d
docker compose -p ephemio-desktop-test logs --tail=100 desktop
```

Open `https://localhost:3001` on that host and accept the local self-signed
certificate. Startup may take several minutes after the first image download.
An HTTPS response alone does not establish that KDE and streaming are ready;
check the browser and logs too.

For a remote server, forward the loopback endpoint over SSH:

```bash
ssh -N -L 3001:127.0.0.1:3001 user@linux-server
```

Then open `https://localhost:3001` on your own computer. The default endpoint
has no authentication and stays bound to host loopback. For public hosting,
use an authenticated TLS gateway with WebSocket support and short-lived,
session-specific authorization before making desktops accessible remotely.

The default resource budget is two CPUs, 4 GiB RAM and 1 GiB shared memory.
These are initial test settings, not measured capacity guarantees. Override
them with `EPHEMIO_DESKTOP_CPUS`, `EPHEMIO_DESKTOP_MEMORY`,
`EPHEMIO_DESKTOP_UID`, `EPHEMIO_DESKTOP_GID`, `EPHEMIO_DESKTOP_TZ`,
`EPHEMIO_DESKTOP_PORT` or `EPHEMIO_DESKTOP_IMAGE` in your shell.
Pin the image to a tested digest for reproducible deployments.

Stop and resume without deleting the home:

```bash
docker compose -p ephemio-desktop-test stop
docker compose -p ephemio-desktop-test start
```

Destroy this test desktop and its home when finished:

```bash
docker compose -p ephemio-desktop-test down --volumes
```

Use a unique Compose project and a unique host port for each concurrent test
desktop. Never reuse a previous customer's home volume. The named volume here
is for stop/resume testing; Ephemio must remove it when the session ends.
System package changes live in the container layer; bake required tools into
a derived image for reproducible replacement.

## Optional GPU

Start with CPU streaming. On Intel/AMD Linux hosts with `/dev/dri` available:

```bash
docker compose -p ephemio-desktop-test -f compose.yaml -f compose.gpu.yaml up -d
```

Use the same two `-f` arguments for subsequent commands. Nvidia requires a
separate host driver/runtime configuration; this overlay does not configure it.
Measure CPU use, frame rate, latency and audio synchronization during YouTube
playback on the actual server, including multiple concurrent desktops.

## What Ephemio still needs

The service will let customers launch, reconnect to, and end temporary desktops
through a browser dashboard. The deployed portal and host service implement the following capabilities;
this standalone Compose file does not:

- Customer accounts and authorized access to each active desktop.
- Session provisioning, resource reservation, and desktop readiness checks.
- Server-enforced session duration and idle policy, including expiry recovery
  after worker or host restart. Duration and idle defaults remain undecided.
- Access revocation and removal of the desktop, home, and other session storage
  on end or expiry, with verified cleanup and retries on failure.
- A dashboard showing session status, time remaining, connection, and end controls.
- Authenticated gateway routing, customer isolation, network policy, resource
  and disk quotas, usage accounting, and capacity testing.

The Compose prototype shares the host kernel and has no automatic expiry or
customer isolation guarantees. Public hosting requires a reviewed isolation
boundary for untrusted desktop users; VM or microVM isolation is a candidate
to evaluate. The desktop must not receive the host Docker socket or privileged
container access.

See the [product direction](../../README.md) for the proposed session lifecycle
and delivery milestones.

Upstream references: [Webtop configuration and security](https://docs.linuxserver.io/images/docker-webtop/)
and [Selkies documentation](https://docs.linuxserver.io/selkies/).
