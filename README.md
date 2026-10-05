# Ephemio

Ephemeral desktops as a service.

The Ephemio POC lets invited users launch a fresh Linux desktop in their browser,
use it for a limited session, and discard it when they are done. Files, browser state,
and installed software belong to that session. Users download anything they
want to keep before the desktop expires.

## Product direction

The core experience is a temporary personal desktop:

1. Sign in and choose a desktop and session duration.
2. Launch a fresh environment and open it in the browser.
3. Use its browser, applications, terminal, audio, and file transfer.
4. Reconnect to the same desktop while the session remains active.
5. End the session explicitly or let its time limit expire.
6. Remove the desktop and its session storage, and confirm cleanup.

Closing a browser tab disconnects the viewer; it does not immediately destroy
an active session. The service must keep showing the expiry time and enforce
it on the server, even if the user disconnects. The POC offers 15, 30, or 60
minutes. Idle timeout, resource tiers, and pricing remain to be decided.

The previous AI-agent workspace concept and its preview workload API are
retired from this repository. They are not the specification for this service.

## Current implementation

| Component | Status |
| --- | --- |
| Ubuntu KDE desktop and browser streaming | Supplied by LinuxServer Webtop, also used by the sibling PDWSLC project |
| Native Linux deployment | Docker Compose prototype with CPU/RAM limits and local HTTPS access |
| Optional Intel/AMD GPU access | Compose overlay supplied; hardware validation pending |
| Customer dashboard and sign-in | Deployed on Hostinger; invited accounts, setup/reset mail and login |
| Session provisioning, expiry, and verified cleanup | Implemented on host-0002 with a durable worker and fallback timer |
| Authenticated desktop gateway | Deployed with expiring tickets, browser grants and stream revocation |
| Customer isolation | POC bridge filtering and container limits; public multi-tenant isolation pending |
| Usage accounting and billing | Planned |

The hosted POC is at [ephemio.com](https://ephemio.com/). The first host admits
one desktop at a time. Browser streaming, audio signal delivery, keyboard input,
clipboard, file transfer, grant renewal and logout revocation have been checked.
See the [deployment report](docs/DEPLOYMENT.md) and [host service](runtime/host/README.md).
Concurrent capacity and subjective video/audio smoothness require further measurement.

## Try the desktop prototype

On a Linux host with Docker Engine and Docker Compose v2:

```bash
cd runtime/linux
docker compose -p ephemio-desktop-test up -d
```

Open `https://localhost:3001` on that host. For remote access, use the SSH tunnel
in the [Linux runtime guide](runtime/linux/README.md). The prototype binds to
loopback and does not implement customer authentication or automatic expiry.

When finished, remove the test desktop and its home storage:

```bash
docker compose -p ephemio-desktop-test down --volumes
```

## Service architecture

Webtop supplies the desktop and streaming. The Ephemio POC supplies the surrounding
service: accounts, launch/reconnect/end controls, session lifetimes, access
routing, resource allocation, and cleanup. Usage accounting is a later milestone.

The initial target is one Ubuntu KDE desktop option on a native Linux host.
The PHP portal allocates a separate environment and storage for each session.
An authenticated HTTPS gateway routes each tester to their own active desktop.
The host worker provisions environments and enforces expiry independently of
the browser connection. The host registry supports additional configured hosts.

Session lifecycle:

```text
requested -> provisioning -> active -> deleting -> deleted
```

Provisioning failures also enter cleanup. `deleted` means the environment and
its session storage have been observed removed. Failed cleanup must remain
visible and be retried after worker or host restarts. Access must be revoked
when a session ends, even if storage cleanup is still in progress.

Before public customer access, the service needs an isolation design for
untrusted desktop users, tenant network separation, resource and disk quotas,
and tested cleanup behavior. The current Docker Compose setup is a host
evaluation tool and does not establish those guarantees.

## Next milestones

The [POC implementation plan](docs/POC_PLAN.md) and [deployment report](docs/DEPLOYMENT.md)
record the initial delivery.

1. Measure sustained video/audio performance and capacity alongside the VPS's
   inference and RTC workloads.
2. Add a second host and exercise host selection, draining, and failure handling.
3. Establish isolation for public customers and hard resource/storage quotas.
4. Add usage accounting, billing and the initial service offering.
