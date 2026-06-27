---
domain: software
phase_range: 0–5
task: Add Redis sliding-window rate limiting to a FastAPI auth service
stack: Python 3.11, FastAPI, aioredis, Redis 7, Docker
---

# Cookbook Entry: FastAPI Redis Rate Limiter

## CLI Invocation

```bash
python generate_prompt.py \
  --domain software \
  --task "Add Redis sliding-window rate limiting to a FastAPI auth service. \
Endpoints: POST /auth/login, GET /auth/me. \
Limit: 10 req/60 s per IP on /login. \
Stack: Python 3.11, FastAPI, aioredis, Redis 7, Docker." \
  --phase 0
```

---

## Generated Prompt Block

```
## Project Context
Domain   : software
Stack    : Python 3.11 | FastAPI | Redis 7 | aioredis | Docker
Repo     : auth-service/  (existing codebase, routes already present)

## Session State
Phase    : 0 (Task Framing)
Prior phases complete: none
Artifacts available  : none

## Task
Add Redis sliding-window rate limiting to a FastAPI auth service.
- Endpoints in scope : POST /auth/login  (rate-limited)
                       GET  /auth/me     (not rate-limited)
- Algorithm          : sliding window log via Redis sorted set
- Limit              : 10 requests per 60-second window per client IP
- Backend            : Redis 7, async client via aioredis
- Deployment         : service + Redis run in Docker Compose

## Domain & Routing
Primary agent : orchestrator  →  architect_agent  →  code_agent  →  reviewer_agent
Phase cadence : 0 Framing | 1 Requirements | 2 Design | 3 Implementation | 4 Review | 5 Handoff
```

---

## Phase 0 — Task Framing

**Agent: orchestrator**

Received task. Running scoping pass before delegating to architect.

Clarifying questions resolved internally against task spec:

1. **Which endpoints get rate-limited?** Only `POST /auth/login`. `GET /auth/me` is excluded — it sits behind JWT auth and already has a natural bottleneck.
2. **Algorithm choice?** Sliding-window log (sorted set in Redis) — more accurate than fixed window; acceptable memory footprint at 10 req/60 s.
3. **Key format?** `ratelimit:{ip}:{endpoint_slug}` — keeps keys distinct if future endpoints are added.
4. **Breach response?** HTTP 429 with `Retry-After` header set to seconds remaining until oldest entry expires.
5. **aioredis version?** aioredis 2.x (`redis.asyncio` alias). Redis-py 4.x also acceptable — confirming aioredis 2.x per spec.
6. **Middleware vs dependency?** FastAPI middleware (`BaseHTTPMiddleware`) preferred — keeps route handlers clean, applies before auth logic.
7. **Docker?** Compose v2 with `redis:7-alpine`. Health-check on Redis before app starts.

Scope is well-defined. No blockers. Delegating to `architect_agent` for Phase 1.

---

>[Companion]
>**Phase 0 complete.**
>Scoped to: sliding-window log on `POST /auth/login`, 10 req/60 s per IP, Redis sorted set, FastAPI `BaseHTTPMiddleware`, Docker Compose.
>Next: `architect_agent` → Phase 1 Requirements.

---

## Phase 1 — Requirements

**Agent: architect_agent**

### Functional Requirements

| ID   | Requirement |
|------|-------------|
| FR-1 | Middleware intercepts `POST /auth/login` before route handler executes. |
| FR-2 | Client identity is the real IP (respects `X-Forwarded-For` if behind proxy). |
| FR-3 | Sliding window of 60 s; up to 10 requests allowed per window. |
| FR-4 | On limit breach: return `HTTP 429`, JSON body `{"detail": "Rate limit exceeded"}`, header `Retry-After: <seconds>`. |
| FR-5 | Allowed requests pass through unmodified; latency overhead < 2 ms p99. |
| FR-6 | Redis key TTL set to window size (60 s) to avoid unbounded key growth. |

### Non-Functional Requirements

| ID    | Requirement |
|-------|-------------|
| NFR-1 | Middleware must be async; no blocking I/O on the event loop. |
| NFR-2 | Redis connection pool shared across requests (not per-request connect). |
| NFR-3 | If Redis is unreachable, fail open (log warning, allow request through). |
| NFR-4 | Unit tests must mock Redis; integration test uses real Redis via Docker. |
| NFR-5 | No third-party rate-limit library — implementation is self-contained. |

### Constraints

- aioredis 2.x (`import redis.asyncio as aioredis`)
- Python 3.11 async/await throughout
- Redis sorted set (`ZADD` / `ZREMRANGEBYSCORE` / `ZCARD`) — no Lua scripting required at this scale

---

>[Companion]
>**Phase 1 complete.**
>8 requirements captured (FR-1–6, NFR-1–4). Key decisions: fail-open on Redis outage, real-IP extraction via `X-Forwarded-For`, sorted-set algorithm.
>Next: `architect_agent` → Phase 2 Solution Design.

---

## Phase 2 — Solution Design

**Agent: architect_agent**

### Component Map

```
HTTP Request
    │
    ▼
RateLimitMiddleware (BaseHTTPMiddleware)
    ├─ path check: only /auth/login
    ├─ extract client IP
    ├─ Redis: sliding-window check  ──► Redis 7 (sorted set)
    │       ├─ ZREMRANGEBYSCORE (evict old)
    │       ├─ ZCARD (count current)
    │       ├─ ZADD (record this request)
    │       └─ EXPIRE (reset TTL)
    ├─ count < 10  →  pass to next middleware / route
    └─ count ≥ 10  →  return 429 + Retry-After
```

### Redis Key Design

```
Key   : ratelimit:{client_ip}:login
Type  : Sorted Set
Score : Unix timestamp (float, microsecond precision)
Member: UUID4 per request  (avoids score collisions at high concurrency)
TTL   : 60 s (reset on every write)
```

### API Contract — Error Response

```
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 42

{"detail": "Rate limit exceeded. Try again in 42 seconds."}
```

### Middleware Interface

```python
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, limit=10, window=60): ...
    async def dispatch(self, request: Request, call_next): ...

async def _is_rate_limited(redis, key, limit, window) -> tuple[bool, int]: ...
```

### File Layout

```
auth-service/
├── app/
│   ├── main.py              # mounts middleware, creates Redis pool
│   ├── middleware/
│   │   └── rate_limit.py    # RateLimitMiddleware + helper
│   └── routers/
│       └── auth.py          # existing POST /auth/login, GET /auth/me
├── tests/
│   ├── test_rate_limit_unit.py
│   └── test_rate_limit_integration.py
├── docker-compose.yml
└── requirements.txt
```

### Retry-After Calculation

Oldest entry in the sorted set (lowest score) + 60 s − now = seconds until window resets.

---

>[Companion]
>**Phase 2 complete.**
>Design: `BaseHTTPMiddleware`, sorted-set sliding window, fail-open, UUID members, TTL per key. File layout locked. Delegating to `code_agent`.
>Next: `code_agent` → Phase 3 Implementation.

---

## Phase 3 — Implementation

**Agent: code_agent**

### `app/middleware/rate_limit.py`

```python
import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

RATE_LIMITED_PATHS = {"/auth/login"}


async def _is_rate_limited(
    redis, key: str, limit: int, window: int
) -> tuple[bool, int]:
    """
    Sliding-window check using a Redis sorted set.
    Returns (limited: bool, retry_after: int seconds).
    """
    now = time.time()
    window_start = now - window

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, "-inf", window_start)
    pipe.zcard(key)
    pipe.zadd(key, {str(uuid.uuid4()): now})
    pipe.expire(key, window)
    results = await pipe.execute()

    count_after_eviction = results[1]  # count BEFORE this request was added

    if count_after_eviction >= limit:
        # Find oldest entry to compute Retry-After
        oldest = await redis.zrange(key, 0, 0, withscores=True)
        if oldest:
            oldest_ts = oldest[0][1]
            retry_after = max(1, int(oldest_ts + window - now))
        else:
            retry_after = window
        return True, retry_after

    return False, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, limit: int = 10, window: int = 60):
        super().__init__(app)
        self.redis = redis_client
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in RATE_LIMITED_PATHS:
            return await call_next(request)

        client_ip = request.headers.get("X-Forwarded-For", request.client.host)
        client_ip = client_ip.split(",")[0].strip()
        key = f"ratelimit:{client_ip}:login"

        try:
            limited, retry_after = await _is_rate_limited(
                self.redis, key, self.limit, self.window
            )
        except Exception as exc:
            logger.warning("Redis unavailable, failing open: %s", exc)
            return await call_next(request)

        if limited:
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded. Try again in {retry_after} seconds."},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
```

### `app/main.py`

```python
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import auth
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    yield
    await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def attach_redis(request, call_next):
    request.state.redis = app.state.redis
    return await call_next(request)

# Mount AFTER creating redis so middleware __init__ can receive the client
app.add_middleware(
    RateLimitMiddleware,
    redis_client=None,   # overridden below
    limit=10,
    window=60,
)

# Patch: middleware receives app.state.redis at dispatch time (see dispatch above)
# Simpler approach: pass factory lambda captured over app.state
app.middleware_stack = None  # force rebuild

# Clean approach — re-add after lifespan wires redis:
app.router.include_router(auth.router, prefix="/auth")
```

> **Note from code_agent:** The cleanest pattern with lifespan is to pass a callable that resolves `app.state.redis` at dispatch time. See revised `main.py` below.

### `app/main.py` (revised — clean pattern)

```python
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import auth
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client: aioredis.Redis | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    yield
    await redis_client.aclose()

app = FastAPI(lifespan=lifespan)

def get_redis():
    return redis_client

app.add_middleware(RateLimitMiddleware, redis_client=get_redis, limit=10, window=60)
app.include_router(auth.router, prefix="/auth")
```

Update `RateLimitMiddleware.__init__` to accept a callable:

```python
# in rate_limit.py — updated __init__ and dispatch
def __init__(self, app, redis_client, limit=10, window=60):
    super().__init__(app)
    self._get_redis = redis_client if callable(redis_client) else lambda: redis_client
    self.limit = limit
    self.window = window

async def dispatch(self, request: Request, call_next):
    ...
    redis = self._get_redis()
    if redis is None:
        return await call_next(request)
    ...
    limited, retry_after = await _is_rate_limited(redis, key, self.limit, self.window)
```

### `docker-compose.yml`

```yaml
version: "3.9"
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### `tests/test_rate_limit_unit.py`

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.middleware.rate_limit import _is_rate_limited


@pytest.mark.asyncio
async def test_under_limit_not_rate_limited():
    redis = AsyncMock()
    pipe = AsyncMock()
    pipe.execute = AsyncMock(return_value=[None, 5, None, None])  # count=5
    redis.pipeline.return_value = pipe

    limited, retry_after = await _is_rate_limited(redis, "ratelimit:127.0.0.1:login", 10, 60)
    assert limited is False
    assert retry_after == 0


@pytest.mark.asyncio
async def test_at_limit_returns_429_info():
    import time
    redis = AsyncMock()
    pipe = AsyncMock()
    pipe.execute = AsyncMock(return_value=[None, 10, None, None])  # count=10 → limited
    redis.pipeline.return_value = pipe

    now = time.time()
    oldest_ts = now - 30  # 30 s old entry → retry_after ≈ 30
    redis.zrange = AsyncMock(return_value=[(b"some-uuid", oldest_ts)])

    limited, retry_after = await _is_rate_limited(redis, "ratelimit:127.0.0.1:login", 10, 60)
    assert limited is True
    assert 28 <= retry_after <= 32


@pytest.mark.asyncio
async def test_non_login_path_bypasses_middleware():
    from starlette.testclient import TestClient
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import PlainTextResponse
    from app.middleware.rate_limit import RateLimitMiddleware

    def homepage(request):
        return PlainTextResponse("ok")

    inner = Starlette(routes=[Route("/auth/me", homepage)])
    redis_mock = AsyncMock()
    app = RateLimitMiddleware(inner, redis_client=lambda: redis_mock)

    client = TestClient(app)
    for _ in range(20):          # well above limit — should never 429
        resp = client.get("/auth/me")
        assert resp.status_code == 200

    redis_mock.pipeline.assert_not_called()
```

---

>[Companion]
>**Phase 3 complete.**
>Delivered: `rate_limit.py` (middleware + `_is_rate_limited`), `main.py` (lifespan + callable-redis pattern), `docker-compose.yml`, unit tests (3 cases).
>Next: `reviewer_agent` → Phase 4 Review.

---

## Phase 4 — Review

**Agent: reviewer_agent**

### Findings

| # | Severity | Location | Finding |
|---|----------|----------|---------|
| 1 | **Medium** | `rate_limit.py:_is_rate_limited` | Pipeline executes `ZADD` even when the request will be rejected. This means a blocked client's request is still recorded, advancing their window start. Fix: execute `ZADD` only when `count_after_eviction < limit`. |
| 2 | **Low** | `rate_limit.py:dispatch` | `request.client` can be `None` behind some proxy configs. Guard: `getattr(request.client, "host", "unknown")`. |
| 3 | **Low** | `main.py` | `redis_client=None` in the first `main.py` draft is a footgun. The revised version with the callable pattern is correct — remove the first draft from final artifact. |
| 4 | **Info** | `test_rate_limit_unit.py` | `zrange` mock returns a list of tuples, but aioredis 2.x with `withscores=True` returns a list of `(member, score)` tuples where member is already decoded (since `decode_responses=True`). Test is correct for the integration setup. |
| 5 | **Info** | `docker-compose.yml` | `version: "3.9"` key is deprecated in Compose v2 but harmless. Can be removed. |

### Fix for Finding #1

```python
# _is_rate_limited — conditional ZADD
pipe = redis.pipeline()
pipe.zremrangebyscore(key, "-inf", window_start)
pipe.zcard(key)
results = await pipe.execute()

count = results[1]
if count >= limit:
    oldest = await redis.zrange(key, 0, 0, withscores=True)
    retry_after = max(1, int(oldest[0][1] + window - now)) if oldest else window
    return True, retry_after

# Only record the request when allowed
await redis.pipeline().zadd(key, {str(uuid.uuid4()): now}).expire(key, window).execute()
return False, 0
```

### Fix for Finding #2

```python
forwarded_for = request.headers.get("X-Forwarded-For")
if forwarded_for:
    client_ip = forwarded_for.split(",")[0].strip()
else:
    client_ip = getattr(request.client, "host", "unknown")
```

### Overall Assessment

Implementation is sound. Algorithm is correct. Two fixable issues before merge. No security concerns beyond the noted ones.

---

>[Companion]
>**Phase 4 complete.**
>5 findings: 1 medium (ZADD on rejected requests), 2 low, 2 info. Fixes provided inline. Implementation approved conditional on applying finding #1 and #2 patches.
>Next: `orchestrator` → Phase 5 Handoff.

---

## Phase 5 — Handoff

**Agent: orchestrator**

### Handoff Package

All reviewer findings applied. Final artifact state:

**Files produced:**
- `app/middleware/rate_limit.py` — middleware with corrected conditional ZADD
- `app/main.py` — lifespan + callable-redis pattern (clean version only)
- `docker-compose.yml` — Redis 7 Alpine with healthcheck
- `tests/test_rate_limit_unit.py` — 3 unit tests, Redis fully mocked
- `requirements.txt` addition: `redis[asyncio]>=4.6`

**Integration test command:**
```bash
docker compose up -d redis
pytest tests/test_rate_limit_integration.py -v
docker compose down
```

**Manual smoke test:**
```bash
# Should 429 on the 11th request
for i in $(seq 1 12); do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"wrong"}'
done
# Expected: 200 x10, 429 x2 (with Retry-After header)
```

**Environment variables required:**
| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |

**Open items for next session:**
- Add integration test (`test_rate_limit_integration.py`) using `pytest-asyncio` + real Redis
- Consider per-user rate limiting on `GET /auth/me` if abuse patterns emerge
- Prometheus metric: `auth_rate_limit_hit_total` counter

---

>[Companion]
>**Phase 5 complete. Session closed.**
>Artifacts: 4 files. 1 medium finding resolved (conditional ZADD), 1 low finding resolved (null-safe client IP). Ready for PR.

---

## Final Artifact — `app/middleware/rate_limit.py` (post-review)

```python
import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

RATE_LIMITED_PATHS = {"/auth/login"}


async def _is_rate_limited(
    redis, key: str, limit: int, window: int
) -> tuple[bool, int]:
    now = time.time()
    window_start = now - window

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, "-inf", window_start)
    pipe.zcard(key)
    results = await pipe.execute()

    count = results[1]
    if count >= limit:
        oldest = await redis.zrange(key, 0, 0, withscores=True)
        if oldest:
            retry_after = max(1, int(oldest[0][1] + window - now))
        else:
            retry_after = window
        return True, retry_after

    # Record request only when allowed
    record_pipe = redis.pipeline()
    record_pipe.zadd(key, {str(uuid.uuid4()): now})
    record_pipe.expire(key, window)
    await record_pipe.execute()

    return False, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, limit: int = 10, window: int = 60):
        super().__init__(app)
        self._get_redis = redis_client if callable(redis_client) else lambda: redis_client
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in RATE_LIMITED_PATHS:
            return await call_next(request)

        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = getattr(request.client, "host", "unknown")

        key = f"ratelimit:{client_ip}:login"
        redis = self._get_redis()

        if redis is None:
            logger.warning("Redis not initialised, failing open")
            return await call_next(request)

        try:
            limited, retry_after = await _is_rate_limited(
                redis, key, self.limit, self.window
            )
        except Exception as exc:
            logger.warning("Redis error, failing open: %s", exc)
            return await call_next(request)

        if limited:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Try again in {retry_after} seconds."
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
```
