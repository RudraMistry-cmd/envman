# EnvMan

A deterministic developer environment engine. Describe the services you want
(Postgres, Redis, Kafka, whatever) as a simple list, and EnvMan pulls the
images, networks the containers together, and — critically — actually
**verifies** each service is ready to use, not just that the container
process is alive.

> If EnvMan says an environment is ready, it's ready. That's the whole
> premise: `docker ps` tells you a container is running; EnvMan tells you
> Postgres will actually accept a query.

## Status

Early. Backend orchestration and verification are functional; the frontend
UI hasn't caught up to what the backend supports yet (see [Known
Limitations](#known-limitations)). Not production-ready — see the caveats
below before relying on this for anything real.

## How it works

```
your service list (JSON)
        ↓
   planner   → builds an ordered step plan (network → pull images → start containers)
        ↓
  executor   → runs each step via the Docker CLI (network create, pull, run)
        ↓
  verifier   → runs a real health check per service (not just "is it running")
        ↓
  WebSocket  → streams progress to the frontend in real time
```

Every service is described once in a central **registry**
(`backend/app/registry/services.py`) — its Docker image, default port, and
which health check to run. Verification dispatches off that registry instead
of guessing a service's identity from its image name, so adding a new
service means adding one registry entry plus (if needed) one new health
check function, not touching the core pipeline.

## Currently supported services (15)

| Category | Services |
|---|---|
| Runtimes | Node.js, Python |
| Databases | PostgreSQL, MySQL, MongoDB, SQLite, CouchDB |
| Cache | Redis |
| Message queues | RabbitMQ, Kafka, NATS |
| Search | Elasticsearch, MeiliSearch, Typesense |
| Storage | MinIO |

Each has a real, protocol-aware health check — e.g. Postgres gets a live
`SELECT 1` query, Redis gets a real `PING`/`PONG`, Kafka gets a broker API
version probe, HTTP-based services (Elasticsearch, MinIO, etc.) get an
actual request to their health endpoint. Nothing is verified by "the
container didn't crash" alone.

## Requirements

- Python 3.10+ (developed against 3.12/3.14)
- Node.js (for the frontend)
- Docker, running and accessible from the CLI

## Running it

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

The backend serves the API on `:8000` and a WebSocket at `/ws`; the frontend
dev server runs on `:5173`. CORS is already configured for that pairing.

## API

| Endpoint | What it does |
|---|---|
| `GET /health` | Liveness check for the backend itself |
| `GET /registry/services` | Returns the full service registry as JSON |
| `POST /setup` | Starts building an environment from a service list; returns immediately, progress streams over `/ws` |
| `WS /ws` | Real-time step-by-step progress + final verification report |

Example request to `/setup`:
```json
{
  "services": [
    { "name": "postgres", "image": "postgres:16", "port": 5432 },
    { "name": "redis", "image": "redis:7" }
  ]
}
```

## Architecture notes for contributors

- **Docker CLI via subprocess, not the Docker SDK.** Deliberate — see
  `executor.py`'s docstring. Commands are always list-based
  (`subprocess.run([...])`), never shell strings, to avoid injection.
- **One Docker network per environment.** Every container in a `/setup`
  request joins the same network, so services can reach each other by
  container name (`envman_<service-name>`).
- **SQLite persistence with a live-Docker fallback.** Environment/container
  state is persisted to SQLite, but verification also falls back to
  discovering `envman_*` containers directly via Docker if the in-memory
  registry is empty (e.g. after a backend restart) — see
  `verifier._discover_envman_containers`.
- **Registry-driven verification.** `verifier.py` looks up a container's
  service via the registry (prefix-matched on image name) and dispatches to
  the matching health check function. Don't add image-name string matching
  outside the registry lookup — that pattern was deliberately removed.

## Known limitations

Being upfront about what's not done yet, rather than letting the README
oversell it:

- **Frontend only exposes 2 of 15 services** (Node + Postgres) — the backend
  supports all 15, the UI hasn't caught up.
- **No cleanup/teardown mechanism.** If a multi-service setup fails partway,
  already-started containers are left running with no automatic cleanup.
- **No automated test suite.** Verification so far has been manual,
  evidence-based checks against live Docker containers, not a CI-run test
  suite.
- **No environment snapshots, templates, or AI-assisted config generation**
  yet — these are on the roadmap, not implemented.

## Roadmap

Being built in phases against a full technical spec (`TECHNICAL_SPEC.md` in
this repo) — Core Infrastructure and Service Expansion are done; Developer
Experience (templates, log aggregation, config import/export), Collaboration,
and Advanced Features (AI config generation, snapshots, monitoring) are
next. See `TECHNICAL_SPEC.md` and `COMPETITIVE_RESEARCH_REPORT.md` for the
full design rationale.