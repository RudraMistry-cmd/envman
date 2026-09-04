# EnvMan — Developer Use Case & Product Vision

## The Goal

**EnvMan eliminates "works on my machine" by making multi-service development environments visual, instant, and verified.**

Instead of spending 30-60 minutes writing `docker-compose.yml`, debugging networking, and manually checking if services are ready — a developer picks their stack, clicks Start, and watches it come alive.

---

## Use Case: Onboarding to a New Team

### The Problem (Today)

Sarah just joined a backend team. The README says:

```
Prerequisites:
- Node.js 20
- PostgreSQL 16
- Redis 7
- RabbitMQ 3.13

Setup:
1. Install nvm, use nvm to install node 20
2. Install Docker Desktop
3. Clone the repo
4. Copy .env.example to .env
5. Run docker compose up -d
6. Wait 30 seconds, then run pg_isready to check postgres
7. If redis isn't ready, wait and check again
8. Run npm install
9. Run npm run db:migrate
10. Run npm run dev
```

**What actually happens:**
- Step 2: Docker Desktop takes 5 minutes to install, needs restart
- Step 5: `docker compose up` fails — port 5432 is already in use from another project
- Step 6: `pg_isready` says "not ready" — is it starting or broken?
- Step 7: Redis times out — wrong network?
- Step 8: `npm install` fails because node 18 is active, not 20
- Total time: **45 minutes**, plus a Slack message to the team: "hey, postgres won't start"

### The EnvMan Flow

Sarah opens EnvMan.

```
┌─────────────────────────────────────────────────┐
│  Configure Your Stack                           │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Runtimes │  │ Databases│  │  Caches  │     │
│  │ 1 avail  │  │ 4 avail  │  │ 1 avail  │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│  ┌──────────┐  ┌──────────┐                    │
│  │  Queues  │  │  Search  │                    │
│  │ 3 avail  │  │ 2 avail  │                    │
│  └──────────┘  └──────────┘                    │
│                                                 │
│           [ Start Setup (3) ]                   │
└─────────────────────────────────────────────────┘
```

**Step 1 — Pick services (10 seconds):**
Sarah clicks "Runtimes" → selects Node 20
Sarah clicks "Databases" → selects PostgreSQL 16
Sarah clicks "Caches" → selects Redis 7
Sarah clicks "Queues" → selects RabbitMQ 3

**Step 2 — Watch it build (30-60 seconds):**

```
┌─────────────────────────────────────────────────┐
│  Setting Up...                                  │
│  ████████████████░░░░░░░░░░░  3 of 7 steps     │
│                                                 │
│  ✓ create_network                              │
│  ✓ pull_node                                   │
│  ✓ pull_postgres                               │
│  ● start_postgres  ← running                   │
│                                                 │
│  Live — receiving events                        │
└─────────────────────────────────────────────────┘
```

Each step streams real-time status via WebSocket. No guessing.

**Step 3 — Verified ready:**

```
┌─────────────────────────────────────────────────┐
│  ✓  Environment Ready                           │
│                                                 │
│  12.3s · 7/7 steps                             │
│                                                 │
│  Verification                                   │
│  ┌─────────────────────────────────────────┐   │
│  │ Node.js     ✓ ready    Port: 3000      │   │
│  │ PostgreSQL  ✓ ready    Port: 5432      │   │
│  │ Redis       ✓ ready    Port: 6379      │   │
│  │ RabbitMQ    ✓ ready    Port: 5672      │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  [ Open in VS Code ]  [ View Logs ]  [ Reset ] │
└─────────────────────────────────────────────────┘
```

Every service is **health-checked** — not just "container exists" but "service actually works." EnvMan ran `pg_isready`, `redis-cli ping`, and `rabbitmq-diagnostics ping` inside each container.

**Step 4 — Start coding:**
Sarah clicks "Open in VS Code." The workspace opens with all services running and networked.

**Total time: under 60 seconds.** No README. No YAML. No debugging.

---

## User Flow Diagram

```
                    ┌──────────────┐
                    │   Developer  │
                    └──────┬───────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Open EnvMan UI    │
                └──────────┬──────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Pick Services & Vers  │
              │  (Node 20, PG 16, ...) │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │    Click "Start"       │
              └───────────┬────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │  POST /setup → Backend Engine  │
         │  { services: [...] }           │
         └───────────────┬────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │  Planner   │ │  Executor  │ │  Verifier  │
   │  (steps)   │ │  (docker)  │ │  (health)  │
   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
         │              │              │
         ▼              ▼              ▼
   ┌────────────────────────────────────────┐
   │         WebSocket Events               │
   │  step_started → step_done → verify     │
   └───────────────────┬────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Frontend UI   │
              │  (real-time)    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Environment    │
              │  Ready ✓        │
              └─────────────────┘
```

---

## What EnvMan Does Under the Hood

```
┌─────────────────────────────────────────────────────────┐
│                    EnvMan Architecture                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐         ┌──────────────────────┐     │
│  │   Frontend   │◄──WS──►│      Backend API      │     │
│  │  React/Vite  │        │     FastAPI/Python    │     │
│  └──────────────┘        └──────────┬───────────┘     │
│                                     │                   │
│                    ┌────────────────┼────────────────┐ │
│                    ▼                ▼                ▼ │
│             ┌───────────┐   ┌───────────┐   ┌────────┐│
│             │  Planner  │   │ Executor  │   │Verifier││
│             │ (creates  │   │ (runs     │   │(health ││
│             │  steps)   │   │  docker)  │   │ checks)││
│             └─────┬─────┘   └─────┬─────┘   └───┬────┘│
│                   │               │              │      │
│                   ▼               ▼              ▼      │
│             ┌─────────────────────────────────────┐    │
│             │         Docker Engine               │    │
│             │  (containers, networks, volumes)    │    │
│             └─────────────────────────────────────┘    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Service Registry (14 services, verified tags)   │  │
│  │  node · postgres · python · mysql · mongo ·      │  │
│  │  redis · rabbitmq · kafka · nats · elasticsearch │  │
│  │  meilisearch · typesense · minio · couchdb       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## The Pipeline: Config → Plan → Execute → Verify

```
 User clicks "Start"
        │
        ▼
┌──────────────────┐
│  1. CONFIG       │  User's picks: [{node: "20"}, {postgres: "16"}]
│     Parse input  │  Validated by Pydantic models
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. PLAN         │  Planner creates ordered steps:
│     Create steps │  1. create_network
│                  │  2. pull node:20
│                  │  3. pull postgres:16
│                  │  4. start node container
│                  │  5. start postgres container
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  3. EXECUTE      │  Executor runs each step:
│     Docker CLI   │  docker network create
│     via subprocess│  docker pull node:20
│                  │  docker run -d --name envman_node ...
│                  │  (real-time events streamed via WS)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  4. VERIFY       │  Verifier checks EACH service:
│     Health checks│  node: docker exec node -v
│                  │  postgres: docker exec pg_isready -U postgres
│                  │  redis: docker exec redis-cli ping
│                  │  Returns: {service, status, checks[]}
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  5. REPORT       │  All green → "Environment Ready"
│     Final state  │  Any red → "Setup Failed" + specific error
└──────────────────┘
```

---

## Comparison: Before vs After EnvMan

| Step | Without EnvMan | With EnvMan |
|------|---------------|-------------|
| Install runtimes | `nvm install 20`, debug PATH | Pick from UI |
| Install Docker | Download, install, restart | Pre-requisite (one-time) |
| Write config | 50+ lines of YAML | Click 4 buttons |
| Networking | Debug container DNS | Automatic |
| Volumes | Figure out mount syntax | Automatic |
| Health checks | Manual `pg_isready`, `redis-cli` | Built-in, automatic |
| Verify ready | Hope and pray | Confirmed with evidence |
| **Time** | **30-60 minutes** | **< 60 seconds** |

---

## Who This Is For

1. **New team members** — onboarding in seconds, not hours
2. **Full-stack developers** — switching between projects without conflicts
3. **Open source contributors** — clone and run, no setup instructions needed
4. **DevOps-light teams** — no one needs to be the "Docker person"
5. **Polyglot developers** — Node + Python + Go projects, one tool manages all

---

## The Vision

EnvMan becomes the **default starting point** for any project that uses containers:

```
Today:     clone repo → read README → install stuff → write YAML → debug → code
With EnvMan: clone repo → open EnvMan → pick stack → code
```

The end state is a world where "works on my machine" is replaced by "works with EnvMan" — and EnvMan is available to every developer, on every platform, for free.
