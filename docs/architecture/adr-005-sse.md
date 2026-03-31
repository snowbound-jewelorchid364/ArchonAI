# ADR-005: Server-Sent Events Over WebSocket for Agent Progress

**Status:** Accepted
**Date:** 2026-03-31
**Deciders:** ARCHON founding team

---

## Context

ARCHON needs to stream real-time agent progress to the browser during a review (3–60 minutes). Options: WebSocket (bidirectional) or Server-Sent Events (unidirectional server → client).

---

## Decision

Use **Server-Sent Events (SSE)** on `GET /api/v1/analyses/:id/events`.

---

## Rationale

**Communication is unidirectional.** Agent progress flows server → client only. The browser does not need to send messages back on the progress channel — checkpoint responses go through standard REST endpoints. WebSocket's bidirectional capability is unused complexity here.

**HTTP/2 multiplexing.** SSE runs over HTTP/2, sharing the existing connection pool. No separate WebSocket upgrade handshake, no separate port.

**Automatic reconnection.** The browser's native `EventSource` API reconnects automatically on disconnect, including through load balancer restarts. This is critical for a 60-minute streaming session.

**Simpler FastAPI implementation.** FastAPI's `EventSourceResponse` (via `sse-starlette`) is 5 lines of code. A production-ready WebSocket implementation with reconnection, heartbeat, and state recovery is 200+ lines.

**Load balancer compatibility.** SSE works through standard HTTP reverse proxies. Railway's proxy is configured with `timeout = 0` for the `/events` path. WebSocket requires explicit proxy upgrade configuration and is incompatible with some CDN edges.

---

## Implementation

```python
# apps/api/src/archon/routers/events.py
from sse_starlette.sse import EventSourceResponse

@router.get("/analyses/{analysis_id}/events")
async def stream_events(analysis_id: UUID, user=Depends(get_current_user)):
    async def generator():
        while True:
            events = await get_new_events(analysis_id, since=last_event_id)
            for event in events:
                yield {"event": event.type, "data": event.json()}
            if await is_analysis_complete(analysis_id):
                break
            await asyncio.sleep(2)  # Poll interval
    return EventSourceResponse(generator())
```

---

## Consequences

- Railway proxy timeout must be set to 0 for `/events` path
- SSE connections count against the API's open file descriptor limit — monitor at scale
- Browser `EventSource` does not support custom headers (auth) — Clerk token passed as query param on the SSE URL, validated server-side
- Polling interval: 2 seconds — balance between latency and DB load

---

## Alternatives Rejected

**WebSocket:** More complex to implement, load balancer configuration required, bidirectionality is unnecessary. Revisit if ARCHON needs real-time bidirectional interaction (e.g., live agent steering).

**Long polling:** Simpler than WebSocket but higher server load than SSE. More complex client implementation. Rejected in favour of SSE's native browser support.

**Push notifications (Firebase/APNs):** Appropriate for mobile. Not relevant for a web app with an active browser session.
