# EnvMan + VS Code Integration Guide

## How to Develop Inside EnvMan Containers

Once EnvMan starts your environment, there are three ways to connect VS Code to the running containers. Pick whichever fits your workflow.

---

## Prerequisites

1. **Docker Desktop** running (or Docker Engine on Linux)
2. **VS Code** installed
3. **EnvMan** started an environment (services verified and running)

Optional but recommended:
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (`ms-vscode-remote.remote-containers`)

---

## Option 1: Edit Locally with Bind Mounts (Simplest)

If your EnvMan config includes bind mounts, files on your host are mapped directly into the container. Changes are instant — no sync, no copy.

### How it works

```
Your machine                         Container
─────────────                        ─────────
D:\projects\myapp\src\app.js   ←→   /app/src/app.js
D:\projects\myapp\package.json ←→   /app/package.json
```

### Steps

```bash
# 1. Start your environment in EnvMan
#    (Node 20 + PostgreSQL 16 selected, containers running)

# 2. Open your project folder in VS Code
cd D:\projects\myapp
code .

# 3. Edit files normally
#    Node.js inside the container picks up changes immediately
```

### When to use this

- You want a lightweight workflow
- You're comfortable running commands in a separate terminal
- Your host has a decent file system (macOS/Windows with WSL2)

### Gotcha: Filesystem performance

On macOS and Windows, Docker bind mounts can be slow for large `node_modules`. If you notice lag:

- **macOS**: OrbStack is faster than Docker Desktop for file mounts
- **Windows**: Use WSL2 backend, keep project files inside WSL2 filesystem
- **Linux**: Native filesystem, no issues

---

## Option 2: Dev Containers Extension (Full Integration)

The Dev Containers extension lets VS Code run **entirely inside the container** — terminal, extensions, IntelliSense, debugging, everything.

### Install

```
VS Code → Extensions → Search "Dev Containers" → Install
Publisher: Microsoft
ID: ms-vscode-remote.remote-containers
```

### Method A: Attach to Running Container

This connects VS Code to an already-running EnvMan container.

```
1. Ctrl+Shift+P (or Cmd+Shift+P on macOS)
2. Type: "Dev Containers: Attach to Running Container"
3. Select: envman_node (or envman_postgres, etc.)
4. VS Code opens a new window inside the container
5. File → Open Folder → /app
```

Now you have:
- Terminal runs `bash` inside the container
- Extensions install inside the container (not on host)
- IntelliSense uses the container's Node.js/Python
- Debugging works against the container's runtime

### Method B: Reopen in Container (If Using Bind Mounts)

If your project folder is bind-mounted into a container, VS Code can detect this and reopen inside it.

```
1. Open your project folder in VS Code normally
2. Ctrl+Shift+P
3. Type: "Dev Containers: Reopen in Container"
4. Pick: envman_node
5. VS Code reloads, now container-native
```

### Method C: Generate devcontainer.json (Best for Teams)

For repeatable setups, create a `.devcontainer/devcontainer.json` that matches your EnvMan config:

```json
{
  "name": "My EnvMan Stack",
  "dockerComposeFile": "../envman-generated-compose.yml",
  "service": "node",
  "workspaceFolder": "/app",
  "forwardPorts": [3000, 5432, 6379],
  "portsAttributes": {
    "3000": { "label": "App", "onOpen": "openBrowser" },
    "5432": { "label": "PostgreSQL", "onOpen": "silent" },
    "6379": { "label": "Redis", "onOpen": "silent" }
  },
  "postCreateCommand": "npm install",
  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "ms-python.python"
      ],
      "settings": {
        "editor.formatOnSave": true
      }
    }
  }
}
```

This is a natural fit for EnvMan's **Phase 3 (Developer Experience)** — generating this file automatically from your environment config.

---

## Option 3: Docker Exec from VS Code Terminal (Quick Commands)

For one-off commands without the full Dev Containers experience.

### Steps

```
1. Open VS Code terminal: Ctrl+`
2. Run a command inside the container:

   docker exec -it envman_node bash        # Node.js container
   docker exec -it envman_postgres bash    # PostgreSQL container
   docker exec -it envman_redis bash       # Redis container
```

### Useful commands

```bash
# Check what's running inside
docker exec envman_node node -v
docker exec envman_postgres pg_isready -U postgres
docker exec envman_redis redis-cli ping

# Run your app's scripts
docker exec -it envman_node npm run dev
docker exec -it envman_node npm run db:migrate
docker exec -it envman_node npm test

# Check environment variables
docker exec envman_node env | grep DATABASE_URL

# View logs
docker logs envman_node --tail 50
```

### Split terminal workflow

```
┌─────────────────────────────────────────────┐
│  VS Code Terminal                           │
│                                             │
│  Tab 1: docker exec -it envman_node bash   │
│         $ npm run dev                       │
│         > Listening on :3000                │
│                                             │
│  Tab 2: docker exec -it envman_node bash   │
│         $ npm test                          │
│         ✓ 12 tests passed                  │
│                                             │
│  Tab 3: docker exec -it envman_postgres    │
│         $ psql -U postgres                  │
│         postgres=# SELECT * FROM users;    │
└─────────────────────────────────────────────┘
```

---

## Connecting to Services

### From your code (inside the container)

When EnvMan sets up networking, containers talk to each other by service name:

```javascript
// Node.js connecting to PostgreSQL (inside container)
const { Pool } = require('pg')
const pool = new Pool({
  host: 'postgres',      // ← Docker DNS resolves to the container
  port: 5432,
  user: 'postgres',
  password: 'postgres',
  database: 'myapp'
})

// Node.js connecting to Redis (inside container)
const redis = require('redis')
const client = redis.createClient({
  url: 'redis://redis:6379'  // ← "redis" is the service name
})
```

```
┌─────────────┐         ┌─────────────┐
│  envman_node│────────▶│envman_postgres│
│  (app code) │  DNS:   │  (database)  │
│             │ "postgres"│             │
└─────────────┘ resolves └─────────────┘
```

### From your host machine

EnvMan maps ports to localhost. Connect using `localhost:PORT`:

```
# From host terminal or any tool
psql -h localhost -p 5432 -U postgres     # PostgreSQL
redis-cli -h localhost -p 6379             # Redis
curl http://localhost:3000                  # Node.js app
```

---

## Recommended Extensions

Install these in VS Code (or add them to `devcontainer.json`):

| Extension | Purpose |
|-----------|---------|
| Dev Containers | Full container integration |
| Docker | View/manage containers from VS Code |
| PostgreSQL | Query Postgres from VS Code sidebar |
| Redis | Browse Redis keys from VS Code |
| ESLint | JavaScript linting |
| Prettier | Code formatting |
| Python | Python support (if using Python runtime) |

---

## Troubleshooting

### "Cannot connect to Docker daemon"

Docker Desktop isn't running. Start it and try again.

### "Port already in use"

Another project is using the same port. In EnvMan, you can configure different port mappings. Or stop the other container:

```bash
docker ps                           # find what's using the port
docker stop <container_id>          # stop it
```

### "Module not found" in VS Code IntelliSense

VS Code is using host Node.js, not the container's. Solutions:

1. Use Dev Containers extension (recommended)
2. Or tell VS Code to use the container's node_modules:
   ```
   "typescript.tsdk": "node_modules/typescript/lib"
   ```

### "Permission denied" when editing files

Container user might differ from your host user. Fix:

```bash
# Inside container
docker exec -u root envman_node chown -R vscode:vscode /app
```

### Files not updating (bind mount lag)

- macOS: Switch to OrbStack or use `--native-sequence-files` flag
- Windows: Ensure WSL2 backend, keep files in WSL2 filesystem
- Linux: Should be native speed, check mount with `docker inspect`

---

## Quick Reference

| Task | Command |
|------|---------|
| List running EnvMan containers | `docker ps --filter name=envman_` |
| Shell into Node container | `docker exec -it envman_node bash` |
| Shell into Postgres | `docker exec -it envman_postgres psql -U postgres` |
| View container logs | `docker logs envman_node --tail 100` |
| Check container health | `docker inspect --format='{{.State.Health.Status}}' envman_node` |
| Stop all EnvMan services | `docker stop $(docker ps --filter name=envman_ -q)` |
| Destroy all EnvMan services | `docker rm -f $(docker ps -a --filter name=envman_ -q)` |
