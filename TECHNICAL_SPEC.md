# EnvMan Technical Specification

## From Docker GUI Wrapper to Category-Defining Developer Environment Platform

**Version:** 1.0
**Date:** August 2026
**Status:** Architecture Design

---

# Part 1: Technical Analysis of Existing Tools

## 1. Docker Compose

### Config Format and Schema
The Compose Specification is a YAML-based format. The latest spec (merged from legacy 2.x/3.x) supports:

```yaml
# Top-level keys
services:     # Required - container definitions
networks:     # Optional - network configuration
volumes:      # Optional - persistent storage
configs:      # Optional - non-sensitive config files
secrets:      # Optional - sensitive config files
```

Each service supports: `image`, `build`, `ports`, `volumes`, `environment`, `depends_on`, `healthcheck`, `networks`, `restart`, `deploy`, `logging`, `ulimits`, `extra_hosts`, `sysctls`, and more.

### Networking
- Services on the same network communicate via DNS using the service name as hostname.
- Docker Compose auto-creates a default bridge network named `{project}_default`.
- Services can join multiple named networks.
- Cross-network communication requires explicit network attachment.
- DNS resolution is automatic: `postgres` resolves to the postgres container's IP.

### Volumes
Three mount types:
1. **Named volumes** - Managed by Docker engine, persisted across restarts
2. **Bind mounts** - Map host path to container path (live reload for dev)
3. **tmpfs** - In-memory mounts (for sensitive/ephemeral data)

```yaml
volumes:
  # Named volume (Docker-managed)
  pg_data:
  # Bind mount
  - ./src:/app/src
  # tmpfs
  - /tmp
```

### Health Checks
```yaml
healthcheck:
  test: ["CMD", "pg_isready", "-U", "postgres"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
  start_interval: 5s
```
Status transitions: `starting` -> `healthy` | `unhealthy` | `none`

### Lifecycle Management
- `docker compose up` - Create and start all services
- `docker compose down` - Stop and remove containers, networks
- `docker compose start/stop` - Start/stop without recreation
- `docker compose restart` - Restart specific services
- `docker compose logs` - Stream logs from services
- `docker compose ps` - List running services
- `docker compose exec` - Run command in running container

### Version Conflicts
- Multiple versions of same service: use different service names
- Port conflicts: explicit port mapping, Compose errors on duplicates
- Image tag pinning prevents unexpected upgrades
- `depends_on` with `condition: service_healthy` ensures readiness

---

## 2. Devbox (Nix-based)

### Config Format (`devbox.json`)
```json
{
  "packages": ["node@20", "python@3.12"],
  "packages": {
    "rustup": {
      "version": "latest",
      "platforms": ["aarch64-darwin", "x86_64-linux"]
    }
  },
  "env": {
    "PROJECT_DIR": "$PWD"
  },
  "env_from": [".env"],
  "shell": {
    "init_hook": ["poetry install"],
    "scripts": {
      "start": "poetry run python -m main.py",
      "test": "poetry run pytest"
    }
  },
  "include": [
    "github:org/repo/ref?dir=plugin-path"
  ]
}
```

### Isolation Mechanism
- Uses Nix packages (functional, reproducible builds)
- Each project gets its own Nix shell environment
- Packages are isolated from system-wide installations
- No Docker containers needed - pure Nix isolation
- Shells can generate devcontainers, Dockerfiles, or run locally

### Service Discovery
- No built-in networking between services
- Services run as Nix-managed processes (not containers)
- Plugin system can add services (e.g., MongoDB plugin)
- Ports must be configured manually

### Data Persistence
- Nix store is read-only and content-addressed
- Project data persists in normal filesystem paths
- No volume abstraction - relies on host filesystem

### Health Checks
- No built-in health check system
- Relies on process-level checks (exit codes)
- Scripts can include custom health logic

### Lifecycle
- `devbox shell` - Enter isolated shell
- `devbox run <script>` - Execute named script
- `devbox add <package>` - Add package to environment
- `devbox generate dockerfile` - Generate Docker image
- `devbox generate devcontainer` - Generate devcontainer.json

### Version Conflict Handling
- Nix's functional approach ensures reproducibility
- Different projects can use different versions of the same tool
- `flake.nix` + `flake.lock` pin exact versions
- No global version conflicts possible

---

## 3. Dev Containers (VS Code)

### Config Format (`devcontainer.json`)
```json
{
  "name": "My Project",
  "image": "mcr.microsoft.com/devcontainers/typescript-node:20",
  "build": {
    "dockerfile": "Dockerfile",
    "context": "..",
    "args": { "VARIANT": "20" }
  },
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace",
  "forwardPorts": [3000, 5432],
  "portsAttributes": {
    "3000": { "label": "App", "onOpen": "openBrowser" },
    "5432": { "label": "Database", "onOpen": "silent" }
  },
  "containerEnv": { "NODE_ENV": "development" },
  "remoteEnv": { "PATH": "${containerEnv:PATH}:/usr/local/bin" },
  "remoteUser": "vscode",
  "postCreateCommand": "npm install",
  "postStartCommand": "npm run dev",
  "customizations": {
    "vscode": {
      "extensions": ["dbaeumer.vscode-eslint"],
      "settings": { "editor.formatOnSave": true }
    }
  },
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  }
}
```

### Networking
- Single-container mode: port forwarding via `forwardPorts`
- Compose mode: references docker-compose.yml, connects to specified `service`
- Port forwarding is automatic and managed by the IDE
- DNS resolution works within Docker networks

### Data Persistence
- `workspaceMount` controls how source code is mounted
- Default: bind mount current directory to `/workspace`
- Named volumes for container data persist across rebuilds

### Health Checks
- No built-in health check in the spec itself
- Lifecycle scripts (`postCreateCommand`, etc.) serve as implicit readiness checks
- `waitFor` property controls when lifecycle scripts run

### Lifecycle
1. `initializeCommand` - Run on host before container creation
2. Container build/pull
3. `onCreateCommand` - First-time setup (runs once)
4. `updateContentCommand` - On content changes
5. `postCreateCommand` - After container creation
6. `postStartCommand` - Every container start
7. `postAttachCommand` - Every IDE attach

### Version Conflicts
- Features system allows adding tools without conflicts
- Multiple devcontainer.json files in subdirectories for different configs
- Docker Compose handles multi-container orchestration
- Platform-specific settings via `platforms` in features

---

## 4. asdf / mise (Version Managers)

### Config Format (`.tool-versions`)
```
nodejs 20.10.0
python 3.12.0
rust 1.75.0
golang 1.21.5
```

### Config Format (`.mise.toml` - mise's preferred format)
```toml
[tools]
node = "20.10.0"
python = ["3.12.0", "3.11.7"]  # multiple versions
rust = "latest"
terraform = "1.6.0"

[env]
NODE_ENV = "development"
```

### Version Specification Syntax
```
20.10.0        # Exact version
20.10          # Latest patch
20             # Latest minor
latest         # Latest release
lts            # Latest LTS
ref:master     # Git ref
prefix:1.19    # Prefix match (for Go)
path:./local   # Local compiled version
sub-2:lts      # 2 versions behind LTS
```

### Isolation Mechanism
- Installs tools in user-space directories (`~/.asdf/installs/`)
- Manipulates `PATH` via shell hooks (shims)
- Each project's `.tool-versions` overrides global settings
- No container isolation - pure filesystem + PATH manipulation

### Service Discovery
- Not designed for service orchestration
- Version managers only manage CLI tools/runtimes
- No networking or service-to-service communication

### Data Persistence
- Tool installations persist in `~/.asdf/installs/{tool}/{version}/`
- Global config in `~/.asdfrc` or `~/.config/mise/config.toml`
- Legacy version files: `.node-version`, `.python-version`, `.ruby-version`

### Health Checks
- No built-in health checks
- `asdf current` / `mise current` shows active versions
- Tools are validated by running them (e.g., `node -v`)

### Lifecycle
- `asdf install` / `mise install` - Install all tools from config
- `asdf shell` / `mise shell` - Activate shell with tools
- `asdf use` / `mise use` - Set version for project
- `asdf global` / `mise global` - Set global default
- Shim management is automatic

### Version Conflict Handling
- Each project can use different tool versions
- Shell hooks ensure correct version activation
- `MISE_${TOOL}_VERSION` env vars override config
- Multiple versions of same tool can coexist (e.g., `node 18` and `node 20`)

---

## 5. Gitpod / Codespaces (Cloud Environments)

### Gitpod Config (`.gitpod.yml`)
```yaml
image:
  file: .gitpod.Dockerfile

tasks:
  - name: Install & Build
    init: npm install && npm run build
    command: npm run dev
    env:
      NODE_ENV: development

ports:
  - port: 3000
    onOpen: open-preview
    name: App
  - port: 5432
    onOpen: ignore

vscode:
  extensions:
    - dbaeumer.vscode-eslint

github:
  prebuilds:
    master: true
    pullRequests: true
```

### Codespaces Config (`devcontainer.json`)
- Uses the Dev Container spec (same as VS Code Dev Containers)
- Adds Codespaces-specific properties: `hostRequirements`, `customizations.codespaces`
- Automatic port forwarding, secret management, dotfiles support

### Networking
- Each workspace gets its own VM/container
- Port forwarding is automatic (proxy-based)
- Services within workspace communicate via localhost or Docker networks
- External access via forwarded URLs with authentication

### Data Persistence
- Workspace storage is ephemeral (destroyed on stop)
- Git repositories persist on external Git host
- Volume mounts for workspace data
- Prebuilds cache dependencies for faster startup

### Health Checks
- Task commands serve as implicit health checks
- Prebuild validation ensures init commands succeed
- Port availability checks before exposing services

### Lifecycle
1. Workspace creation (from git repo)
2. Image build (Dockerfile or prebuilt)
3. Task initialization (init commands)
4. Task startup (command)
5. IDE connection
6. Workspace running
7. Workspace stop/archive

### Version Conflicts
- Base image determines available tools
- Features system for adding tools
- Multiple configurations per repo (`.devcontainer/{name}/devcontainer.json`)
- Docker Compose for multi-service environments

---

# Part 2: Feature Architecture Design

## A. Service Registry System

### Registry Schema

```python
# backend/app/registry/schema.py

from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from enum import Enum

class ServiceCategory(str, Enum):
    RUNTIME = "runtime"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    SEARCH = "search"
    STORAGE = "storage"
    MONITORING = "monitoring"
    PROXY = "proxy"
    MESSAGE_BROKER = "message_broker"
    OTHER = "other"

class HealthCheckConfig(BaseModel):
    """How to verify this service is ready."""
    type: str  # "command", "http", "tcp", "custom"
    command: Optional[str] = None      # For "command" type
    url: Optional[str] = None          # For "http" type
    port: Optional[int] = None         # For "tcp" type
    interval: int = 5                  # Seconds between checks
    timeout: int = 10                  # Max seconds per check
    retries: int = 3                   # Max retry attempts
    start_period: int = 10             # Grace period before checks

class VolumeMount(BaseModel):
    """Default volume mount point for service data."""
    container_path: str
    volume_name: Optional[str] = None  # Named volume template
    description: str = ""

class ServiceDefinition(BaseModel):
    """Complete definition of a service type."""
    id: str
    name: str
    category: ServiceCategory
    description: str
    docker_image_template: str  # e.g., "postgres:{version}"
    default_version: str
    available_versions: List[str]
    default_port: int
    additional_ports: List[int] = []
    default_env: Dict[str, str] = {}
    required_env: List[str] = []
    health_check: HealthCheckConfig
    volume_mounts: List[VolumeMount] = []
    network_aliases: List[str] = []
    platform_support: Dict[str, bool] = {
        "linux": True,
        "macos": True,
        "windows": True
    }
    resource_requirements: Dict[str, str] = {
        "memory": "256Mi",
        "cpu": "0.25"
    }
    tags: List[str] = []
```

### Complete Service Registry

```python
# backend/app/registry/services.py

SERVICES: Dict[str, ServiceDefinition] = {
    # ===== RUNTIMES =====
    "node": ServiceDefinition(
        id="node",
        name="Node.js",
        category="runtime",
        description="JavaScript runtime for server-side applications",
        docker_image_template="node:{version}",
        default_version="20",
        available_versions=["18", "20", "22"],
        default_port=3000,
        default_env={"NODE_ENV": "development"},
        health_check=HealthCheckConfig(
            type="command",
            command="node --version",
            interval=5,
            retries=2,
        ),
        volume_mounts=[
            VolumeMount(container_path="/app", description="Application code"),
        ],
        tags=["javascript", "typescript", "frontend", "backend"],
    ),
    "python": ServiceDefinition(
        id="python",
        name="Python",
        category="runtime",
        description="Python programming language runtime",
        docker_image_template="python:{version}-slim",
        default_version="3.12",
        available_versions=["3.10", "3.11", "3.12", "3.13"],
        default_port=8000,
        default_env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"},
        health_check=HealthCheckConfig(
            type="command",
            command="python --version",
            interval=5,
            retries=2,
        ),
        volume_mounts=[
            VolumeMount(container_path="/app", description="Application code"),
        ],
        tags=["python", "django", "flask", "fastapi"],
    ),
    "go": ServiceDefinition(
        id="go",
        name="Go",
        category="runtime",
        description="Go programming language runtime",
        docker_image_template="golang:{version}-alpine",
        default_version="1.22",
        available_versions=["1.21", "1.22", "1.23"],
        default_port=8080,
        health_check=HealthCheckConfig(
            type="command",
            command="go version",
            interval=5,
            retries=2,
        ),
        volume_mounts=[
            VolumeMount(container_path="/app", description="Application code"),
        ],
        tags=["go", "golang"],
    ),
    "rust": ServiceDefinition(
        id="rust",
        name="Rust",
        category="runtime",
        description="Rust programming language runtime",
        docker_image_template="rust:{version}",
        default_version="1.78",
        available_versions=["1.77", "1.78", "1.79"],
        default_port=8080,
        health_check=HealthCheckConfig(
            type="command",
            command="rustc --version",
            interval=5,
            retries=2,
        ),
        volume_mounts=[
            VolumeMount(container_path="/app", description="Application code"),
        ],
        tags=["rust"],
    ),
    "ruby": ServiceDefinition(
        id="ruby",
        name="Ruby",
        category="runtime",
        description="Ruby programming language runtime",
        docker_image_template="ruby:{version}-slim",
        default_version="3.3",
        available_versions=["3.2", "3.3"],
        default_port=3000,
        health_check=HealthCheckConfig(
            type="command",
            command="ruby --version",
            interval=5,
            retries=2,
        ),
        volume_mounts=[
            VolumeMount(container_path="/app", description="Application code"),
        ],
        tags=["ruby", "rails"],
    ),
    "java": ServiceDefinition(
        id="java",
        name="Java",
        category="runtime",
        description="Java runtime environment",
        docker_image_template="eclipse-temurin:{version}-jdk-jammy",
        default_version="21",
        available_versions=["17", "21"],
        default_port=8080,
        health_check=HealthCheckConfig(
            type="command",
            command="java --version",
            interval=5,
            retries=2,
        ),
        volume_mounts=[
            VolumeMount(container_path="/app", description="Application code"),
        ],
        tags=["java", "spring", "jvm"],
    ),
    "php": ServiceDefinition(
        id="php",
        name="PHP",
        category="runtime",
        description="PHP scripting language runtime",
        docker_image_template="php:{version}-cli",
        default_version="8.3",
        available_versions=["8.2", "8.3"],
        default_port=8000,
        health_check=HealthCheckConfig(
            type="command",
            command="php --version",
            interval=5,
            retries=2,
        ),
        volume_mounts=[
            VolumeMount(container_path="/app", description="Application code"),
        ],
        tags=["php", "laravel", "wordpress"],
    ),
    "dotnet": ServiceDefinition(
        id="dotnet",
        name=".NET",
        category="runtime",
        description=".NET runtime and SDK",
        docker_image_template="mcr.microsoft.com/dotnet/sdk:{version}",
        default_version="8.0",
        available_versions=["6.0", "7.0", "8.0"],
        default_port=5000,
        health_check=HealthCheckConfig(
            type="command",
            command="dotnet --version",
            interval=5,
            retries=2,
        ),
        volume_mounts=[
            VolumeMount(container_path="/app", description="Application code"),
        ],
        tags=["dotnet", "csharp", "aspnet"],
    ),

    # ===== DATABASES =====
    "postgres": ServiceDefinition(
        id="postgres",
        name="PostgreSQL",
        category="database",
        description="Advanced open-source relational database",
        docker_image_template="postgres:{version}",
        default_version="16",
        available_versions=["14", "15", "16", "17"],
        default_port=5432,
        default_env={
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "postgres",
        },
        required_env=["POSTGRES_PASSWORD"],
        health_check=HealthCheckConfig(
            type="command",
            command="pg_isready -U postgres",
            interval=5,
            timeout=5,
            retries=5,
            start_period=10,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/var/lib/postgresql/data",
                volume_name="pg_data",
                description="Database files"
            ),
        ],
        resource_requirements={"memory": "256Mi", "cpu": "0.25"},
        tags=["sql", "relational", "acid"],
    ),
    "mysql": ServiceDefinition(
        id="mysql",
        name="MySQL",
        category="database",
        description="Popular open-source relational database",
        docker_image_template="mysql:{version}",
        default_version="8.4",
        available_versions=["8.0", "8.4"],
        default_port=3306,
        default_env={
            "MYSQL_ROOT_PASSWORD": "root",
            "MYSQL_DATABASE": "app",
            "MYSQL_USER": "user",
            "MYSQL_PASSWORD": "password",
        },
        health_check=HealthCheckConfig(
            type="command",
            command="mysqladmin ping -h localhost -u root -proot",
            interval=5,
            timeout=5,
            retries=5,
            start_period=15,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/var/lib/mysql",
                volume_name="mysql_data",
                description="Database files"
            ),
        ],
        resource_requirements={"memory": "512Mi", "cpu": "0.5"},
        tags=["sql", "relational"],
    ),
    "mongodb": ServiceDefinition(
        id="mongodb",
        name="MongoDB",
        category="database",
        description="NoSQL document-oriented database",
        docker_image_template="mongo:{version}",
        default_version="7.0",
        available_versions=["6.0", "7.0"],
        default_port=27017,
        default_env={
            "MONGO_INITDB_ROOT_USERNAME": "admin",
            "MONGO_INITDB_ROOT_PASSWORD": "password",
        },
        health_check=HealthCheckConfig(
            type="command",
            command="mongosh --eval 'db.adminCommand({ping:1})' --quiet",
            interval=5,
            timeout=5,
            retries=5,
            start_period=10,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/data/db",
                volume_name="mongo_data",
                description="Database files"
            ),
        ],
        resource_requirements={"memory": "256Mi", "cpu": "0.25"},
        tags=["nosql", "document", "bson"],
    ),
    "redis": ServiceDefinition(
        id="redis",
        name="Redis",
        category="cache",
        description="In-memory data structure store (cache/database)",
        docker_image_template="redis:{version}-alpine",
        default_version="7",
        available_versions=["6", "7"],
        default_port=6379,
        health_check=HealthCheckConfig(
            type="command",
            command="redis-cli ping",
            interval=5,
            timeout=3,
            retries=3,
            start_period=5,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/data",
                volume_name="redis_data",
                description="Redis data"
            ),
        ],
        resource_requirements={"memory": "128Mi", "cpu": "0.1"},
        tags=["cache", "in-memory", "pubsub"],
    ),
    "sqlite": ServiceDefinition(
        id="sqlite",
        name="SQLite",
        category="database",
        description="Self-contained SQL database engine",
        docker_image_template="sqlite:latest",  # Usually embedded, not containerized
        default_version="3",
        available_versions=["3"],
        default_port=0,  # No network port
        health_check=HealthCheckConfig(
            type="command",
            command="sqlite3 --version",
            interval=5,
            retries=2,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/data",
                volume_name="sqlite_data",
                description="Database file"
            ),
        ],
        resource_requirements={"memory": "64Mi", "cpu": "0.05"},
        tags=["sql", "embedded", "lightweight"],
    ),
    "couchdb": ServiceDefinition(
        id="couchdb",
        name="CouchDB",
        category="database",
        description="NoSQL document database with HTTP API",
        docker_image_template="couchdb:{version}",
        default_version="3",
        available_versions=["3"],
        default_port=5984,
        default_env={
            "COUCHDB_USER": "admin",
            "COUCHDB_PASSWORD": "password",
        },
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:5984/_up",
            interval=5,
            retries=3,
            start_period=10,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/opt/couchdb/data",
                volume_name="couchdb_data",
                description="Database files"
            ),
        ],
        tags=["nosql", "document", "http"],
    ),
    "elasticsearch": ServiceDefinition(
        id="elasticsearch",
        name="Elasticsearch",
        category="search",
        description="Distributed search and analytics engine",
        docker_image_template="docker.elastic.co/elasticsearch/elasticsearch:{version}",
        default_version="8.14.0",
        available_versions=["8.13.0", "8.14.0"],
        default_port=9200,
        default_env={
            "discovery.type": "single-node",
            "xpack.security.enabled": "false",
            "ES_JAVA_OPTS": "-Xms512m -Xmx512m",
        },
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:9200/_cluster/health",
            interval=10,
            timeout=10,
            retries=5,
            start_period=30,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/usr/share/elasticsearch/data",
                volume_name="es_data",
                description="Index data"
            ),
        ],
        resource_requirements={"memory": "1Gi", "cpu": "1.0"},
        tags=["search", "analytics", "full-text"],
    ),

    # ===== MESSAGE QUEUES =====
    "rabbitmq": ServiceDefinition(
        id="rabbitmq",
        name="RabbitMQ",
        category="message_broker",
        description="Open-source message broker",
        docker_image_template="rabbitmq:{version}-management",
        default_version="3.13",
        available_versions=["3.12", "3.13"],
        default_port=5672,
        additional_ports=[15672],  # Management UI
        default_env={
            "RABBITMQ_DEFAULT_USER": "guest",
            "RABBITMQ_DEFAULT_PASS": "guest",
        },
        health_check=HealthCheckConfig(
            type="command",
            command="rabbitmq-diagnostics -q ping",
            interval=10,
            timeout=5,
            retries=5,
            start_period=20,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/var/lib/rabbitmq",
                volume_name="rabbitmq_data",
                description="Message data"
            ),
        ],
        resource_requirements={"memory": "256Mi", "cpu": "0.25"},
        tags=["amqp", "queue", "messaging"],
    ),
    "kafka": ServiceDefinition(
        id="kafka",
        name="Kafka",
        category="message_broker",
        description="Distributed event streaming platform",
        docker_image_template="confluentinc/cp-kafka:{version}",
        default_version="7.6.0",
        available_versions=["7.5.0", "7.6.0"],
        default_port=9092,
        default_env={
            "KAFKA_NODE_ID": "1",
            "KAFKA_PROCESS_ROLES": "broker,controller",
            "KAFKA_LISTENERS": "PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093",
            "KAFKA_ADVERTISED_LISTENERS": "PLAINTEXT://localhost:9092",
            "KAFKA_CONTROLLER_QUORUM_VOTERS": "1@localhost:9093",
            "KAFKA_CONTROLLER_LISTENER_NAMES": "CONTROLLER",
            "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP": "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT",
            "CLUSTER_ID": "MkU3OEVBNTcwNTJENDM2Qk",
        },
        health_check=HealthCheckConfig(
            type="command",
            command="kafka-broker-api-versions --bootstrap-server localhost:9092",
            interval=10,
            timeout=10,
            retries=5,
            start_period=30,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/var/lib/kafka/data",
                volume_name="kafka_data",
                description="Kafka data"
            ),
        ],
        resource_requirements={"memory": "512Mi", "cpu": "0.5"},
        tags=["streaming", "event", "distributed"],
    ),
    "nats": ServiceDefinition(
        id="nats",
        name="NATS",
        category="message_broker",
        description="Cloud-native messaging system",
        docker_image_template="nats:{version}-alpine",
        default_version="2.10",
        available_versions=["2.9", "2.10"],
        default_port=4222,
        additional_ports=[8222],  # Monitoring
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:8222/healthz",
            interval=5,
            retries=3,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/data",
                volume_name="nats_data",
                description="NATS data"
            ),
        ],
        resource_requirements={"memory": "128Mi", "cpu": "0.1"},
        tags=["messaging", "pubsub", "lightweight"],
    ),

    # ===== SEARCH =====
    "meilisearch": ServiceDefinition(
        id="meilisearch",
        name="MeiliSearch",
        category="search",
        description="Lightning-fast, hyper-relevant search engine",
        docker_image_template="getmeili/meilisearch:{version}",
        default_version="v1.8",
        available_versions=["v1.7", "v1.8"],
        default_port=7700,
        default_env={
            "MEILI_MASTER_KEY": "masterKey",
            "MEILI_ENV": "development",
        },
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:7700/health",
            interval=5,
            retries=3,
            start_period=10,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/meili_data",
                volume_name="meili_data",
                description="Search index data"
            ),
        ],
        resource_requirements={"memory": "256Mi", "cpu": "0.25"},
        tags=["search", "instant", "typo-tolerant"],
    ),
    "typesense": ServiceDefinition(
        id="typesense",
        name="Typesense",
        category="search",
        description="Blazingly fast, typo-tolerant search engine",
        docker_image_template="typesense/typesense:{version}",
        default_version="26.1",
        available_versions=["25.1", "26.1"],
        default_port=8108,
        default_env={
            "TYPESENSE_API_KEY": "xyz",
            "TYPESENSE_DATA_DIR": "/data",
        },
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:8108/health",
            interval=5,
            retries=3,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/data",
                volume_name="typesense_data",
                description="Search data"
            ),
        ],
        resource_requirements={"memory": "256Mi", "cpu": "0.25"},
        tags=["search", "instant"],
    ),

    # ===== STORAGE =====
    "minio": ServiceDefinition(
        id="minio",
        name="MinIO",
        category="storage",
        description="S3-compatible object storage",
        docker_image_template="minio/minio:{version}",
        default_version="latest",
        available_versions=["latest"],
        default_port=9000,
        additional_ports=[9001],  # Console
        default_env={
            "MINIO_ROOT_USER": "minioadmin",
            "MINIO_ROOT_PASSWORD": "minioadmin",
        },
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:9000/minio/health/live",
            interval=5,
            retries=3,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/data",
                volume_name="minio_data",
                description="Object storage data"
            ),
        ],
        command="server /data --console-address :9001",
        resource_requirements={"memory": "256Mi", "cpu": "0.25"},
        tags=["s3", "object-storage", "minio"],
    ),

    # ===== MONITORING =====
    "prometheus": ServiceDefinition(
        id="prometheus",
        name="Prometheus",
        category="monitoring",
        description="Monitoring and alerting toolkit",
        docker_image_template="prom/prometheus:{version}",
        default_version="v2.53.0",
        available_versions=["v2.52.0", "v2.53.0"],
        default_port=9090,
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:9090/-/healthy",
            interval=10,
            retries=3,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/prometheus",
                volume_name="prometheus_data",
                description="Metrics data"
            ),
        ],
        resource_requirements={"memory": "256Mi", "cpu": "0.25"},
        tags=["monitoring", "metrics", "alerting"],
    ),
    "grafana": ServiceDefinition(
        id="grafana",
        name="Grafana",
        category="monitoring",
        description="Observability and data visualization platform",
        docker_image_template="grafana/grafana:{version}",
        default_version="11.1.0",
        available_versions=["11.0.0", "11.1.0"],
        default_port=3000,
        default_env={
            "GF_SECURITY_ADMIN_USER": "admin",
            "GF_SECURITY_ADMIN_PASSWORD": "admin",
        },
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:3000/api/health",
            interval=10,
            retries=3,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/var/lib/grafana",
                volume_name="grafana_data",
                description="Grafana data"
            ),
        ],
        resource_requirements={"memory": "128Mi", "cpu": "0.1"},
        tags=["monitoring", "visualization", "dashboards"],
    ),

    # ===== PROXY / REVERSE PROXY =====
    "nginx": ServiceDefinition(
        id="nginx",
        name="Nginx",
        category="proxy",
        description="High-performance web server and reverse proxy",
        docker_image_template="nginx:{version}-alpine",
        default_version="1.27",
        available_versions=["1.25", "1.26", "1.27"],
        default_port=80,
        additional_ports=[443],
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:80",
            interval=5,
            retries=3,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/etc/nginx/conf.d",
                volume_name="nginx_config",
                description="Nginx configuration"
            ),
        ],
        resource_requirements={"memory": "64Mi", "cpu": "0.05"},
        tags=["web-server", "reverse-proxy", "load-balancer"],
    ),
    "traefik": ServiceDefinition(
        id="traefik",
        name="Traefik",
        category="proxy",
        description="Cloud-native reverse proxy and load balancer",
        docker_image_template="traefik:{version}",
        default_version="v3.1",
        available_versions=["v2.11", "v3.0", "v3.1"],
        default_port=80,
        additional_ports=[8080],  # Dashboard
        default_env={
            "TRAEFIK_API_INSECURE": "true",
        },
        health_check=HealthCheckConfig(
            type="http",
            url="http://localhost:8080/api/overview",
            interval=5,
            retries=3,
        ),
        volume_mounts=[
            VolumeMount(
                container_path="/etc/traefik",
                volume_name="traefik_config",
                description="Traefik configuration"
            ),
        ],
        resource_requirements={"memory": "64Mi", "cpu": "0.05"},
        tags=["reverse-proxy", "load-balancer", "letsencrypt"],
    ),

    # ===== OTHER =====
    "mailhog": ServiceDefinition(
        id="mailhog",
        name="MailHog",
        category="other",
        description="Email testing tool for developers",
        docker_image_template="mailhog/mailhog:{version}",
        default_version="latest",
        available_versions=["latest"],
        default_port=1025,
        additional_ports=[8025],  # Web UI
        health_check=HealthCheckConfig(
            type="tcp",
            port=1025,
            interval=5,
            retries=3,
        ),
        resource_requirements={"memory": "64Mi", "cpu": "0.05"},
        tags=["email", "testing", "smtp"],
    ),
}
```

---

## B. Configuration Schema

### Full EnvMan Config Format (`envman.yaml`)

```yaml
# backend/app/models/config.py - Schema definition
# This is the universal config format for EnvMan environments.

apiVersion: envman.dev/v1
kind: Environment
metadata:
  name: "my-mern-project"
  description: "MERN stack with Redis caching"
  labels:
    team: "backend"
    project: "myapp"
  createdAt: "2026-08-30T10:00:00Z"

spec:
  services:
    node:
      type: runtime
      image: node:20-alpine
      version: "20"
      ports:
        - "3000:3000"
      volumes:
        - type: bind
          source: ./src
          target: /app/src
        - type: named
          name: node_modules
          target: /app/node_modules
      env:
        NODE_ENV: development
        MONGO_URL: "mongodb://mongo:27017/myapp"
        REDIS_URL: "redis://redis:6379"
      dependsOn:
        mongo:
          condition: service_healthy
        redis:
          condition: service_started
      command: ["npm", "run", "dev"]
      workingDir: /app
      healthCheck:
        type: http
        url: "http://localhost:3000/health"
        interval: 10
        retries: 3
        startPeriod: 15
      resources:
        memory: 512Mi
        cpu: "1.0"

    mongo:
      type: database
      engine: mongodb
      image: mongo:7
      version: "7"
      ports:
        - "27017:27017"
      volumes:
        - type: named
          name: mongo_data
          target: /data/db
      env:
        MONGO_INITDB_ROOT_USERNAME: admin
        MONGO_INITDB_ROOT_PASSWORD: password
        MONGO_INITDB_DATABASE: myapp
      healthCheck:
        type: command
        command: "mongosh --eval 'db.adminCommand({ping:1})' --quiet"
        interval: 5
        retries: 5
        startPeriod: 10

    redis:
      type: cache
      image: redis:7-alpine
      version: "7"
      ports:
        - "6379:6379"
      volumes:
        - type: named
          name: redis_data
          target: /data
      healthCheck:
        type: command
        command: "redis-cli ping"
        interval: 5
        retries: 3
      command: ["redis-server", "--appendonly", "yes"]

    nginx:
      type: proxy
      image: nginx:1.27-alpine
      version: "1.27"
      ports:
        - "80:80"
        - "443:443"
      volumes:
        - type: bind
          source: ./nginx/nginx.conf
          target: /etc/nginx/conf.d/default.conf
          readOnly: true
      dependsOn:
        node:
          condition: service_started

  networks:
    default:
      driver: bridge
    backend:
      driver: bridge
    frontend:
      driver: bridge

  volumes:
    mongo_data:
    redis_data:
    node_modules:

  configs:
    nginx_conf:
      file: ./nginx/nginx.conf

  secrets:
    db_password:
      environment: DB_PASSWORD

  # Global settings
  settings:
    autoRemove: false        # Remove containers on destroy
    pullPolicy: if-not-present  # Always, if-not-present, never
    logDriver: json-file
    logOptions:
      max-size: "10m"
      max-file: "3"
```

### Config Validation Model

```python
# backend/app/models/config.py

from pydantic import BaseModel, field_validator, model_validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum

class MountType(str, Enum):
    BIND = "bind"
    NAMED = "named"
    TMPFS = "tmpfs"

class MountConfig(BaseModel):
    type: MountType
    source: Optional[str] = None  # For bind mounts
    name: Optional[str] = None    # For named volumes
    target: str
    readOnly: bool = False

class DependsOnCondition(str, Enum):
    SERVICE_STARTED = "service_started"
    SERVICE_HEALTHY = "service_healthy"
    SERVICE_COMPLETED_SUCCESSFULLY = "service_completed_successfully"

class DependsOnConfig(BaseModel):
    condition: DependsOnCondition = DependsOnCondition.SERVICE_STARTED
    required: bool = True

class HealthCheckType(str, Enum):
    COMMAND = "command"
    HTTP = "http"
    TCP = "tcp"

class HealthCheckConfig(BaseModel):
    type: HealthCheckType
    command: Optional[str] = None
    url: Optional[str] = None
    port: Optional[int] = None
    interval: int = 5
    timeout: int = 10
    retries: int = 3
    startPeriod: int = 0

class ResourceConfig(BaseModel):
    memory: str = "256Mi"
    cpu: str = "0.25"

class ServiceConfig(BaseModel):
    type: str
    image: str
    version: Optional[str] = None
    ports: List[str] = []
    volumes: List[Union[str, MountConfig]] = []
    env: Dict[str, str] = {}
    dependsOn: Dict[str, Union[str, DependsOnConfig]] = {}
    command: Optional[Union[str, List[str]]] = None
    workingDir: Optional[str] = None
    healthCheck: Optional[HealthCheckConfig] = None
    resources: Optional[ResourceConfig] = None
    network: Optional[str] = None
    restart: str = "unless-stopped"

class NetworkConfig(BaseModel):
    driver: str = "bridge"
    external: bool = False
    name: Optional[str] = None

class VolumeConfig(BaseModel):
    driver: str = "local"
    external: bool = False
    name: Optional[str] = None

class EnvironmentMetadata(BaseModel):
    name: str
    description: str = ""
    labels: Dict[str, str] = {}
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class EnvironmentSpec(BaseModel):
    services: Dict[str, ServiceConfig]
    networks: Dict[str, NetworkConfig] = {}
    volumes: Dict[str, VolumeConfig] = {}
    configs: Dict[str, Any] = {}
    secrets: Dict[str, Any] = {}
    settings: Dict[str, Any] = {}

class EnvironmentConfig(BaseModel):
    apiVersion: str = "envman.dev/v1"
    kind: str = "Environment"
    metadata: EnvironmentMetadata
    spec: EnvironmentSpec

    @model_validator(mode='after')
    def validate_dependencies(self):
        """Ensure all dependsOn references exist in services."""
        services = self.spec.services
        for name, service in services.items():
            for dep_name in service.dependsOn:
                if dep_name not in services:
                    raise ValueError(
                        f"Service '{name}' depends on '{dep_name}' which is not defined"
                    )
        return self

    @model_validator(mode='after')
    def validate_port_conflicts(self):
        """Ensure no two services claim the same host port."""
        port_map: Dict[int, str] = {}
        for name, service in self.spec.services.items():
            for port_str in service.ports:
                parts = port_str.split(":")
                if len(parts) >= 1:
                    host_port = int(parts[0])
                    if host_port in port_map:
                        raise ValueError(
                            f"Port conflict: {host_port} used by both "
                            f"'{port_map[host_port]}' and '{name}'"
                        )
                    port_map[host_port] = name
        return self
```

---

## C. Networking Architecture

### Network Model

```python
# backend/app/engine/networking.py

from typing import Dict, List, Set, Optional
from app.models.config import EnvironmentConfig, ServiceConfig
from app.utils.logger import get_logger

logger = get_logger("networking")


class NetworkManager:
    """Manages Docker networks for the environment."""

    def __init__(self, config: EnvironmentConfig):
        self.config = config
        self.networks: Dict[str, Dict] = {}
        self.service_networks: Dict[str, Set[str]] = {}
        self.port_registry: Dict[int, str] = {}  # port -> service name

    async def plan_networks(self) -> List[Dict]:
        """Create network creation steps."""
        steps = []

        # Always create default network
        env_name = self.config.metadata.name
        default_net = f"{env_name}_default"

        networks = self.config.spec.networks or {}
        if not networks:
            networks = {"default": {"driver": "bridge"}}

        for net_name, net_config in networks.items():
            full_name = f"{env_name}_{net_name}"
            steps.append({
                "id": f"create_network_{net_name}",
                "type": "create_network",
                "params": {
                    "name": full_name,
                    "driver": net_config.get("driver", "bridge"),
                },
            })
            self.networks[net_name] = {"name": full_name, "config": net_config}

        return steps

    async def connect_service(self, service_name: str, service_config: ServiceConfig) -> List[Dict]:
        """Plan network connection for a service."""
        steps = []
        env_name = self.config.metadata.name

        # Determine which networks this service joins
        networks_to_join = set()

        # Default network unless specified
        if service_config.network:
            networks_to_join.add(service_config.network)
        else:
            networks_to_join.add("default")

        # Services with dependencies join the same networks as their dependencies
        for dep_name in service_config.dependsOn:
            dep_networks = self.service_networks.get(dep_name, {"default"})
            networks_to_join.update(dep_networks)

        self.service_networks[service_name] = networks_to_join

        for net_name in networks_to_join:
            full_net_name = f"{env_name}_{net_name}"
            container_name = f"envman_{service_name}"

            steps.append({
                "id": f"connect_{service_name}_{net_name}",
                "type": "connect_network",
                "params": {
                    "network": full_net_name,
                    "container": container_name,
                    "aliases": [service_name],
                },
                "depends_on": f"create_network_{net_name}",
            })

        return steps

    def detect_port_conflicts(self) -> List[Dict[str, Any]]:
        """Detect port conflicts between services."""
        conflicts = []
        port_to_service: Dict[int, str] = {}

        for name, service in self.config.spec.services.items():
            for port_str in service.ports:
                parts = port_str.split(":")
                if len(parts) >= 1:
                    host_port = int(parts[0])
                    if host_port in port_to_service:
                        conflicts.append({
                            "port": host_port,
                            "service1": port_to_service[host_port],
                            "service2": name,
                        })
                    else:
                        port_to_service[host_port] = name
                        self.port_registry[host_port] = name

        return conflicts

    def get_service_url(self, service_name: str, port: Optional[int] = None) -> str:
        """Get the URL to reach a service."""
        service = self.config.spec.services.get(service_name)
        if not service:
            raise ValueError(f"Service '{service_name}' not found")

        if port:
            return f"localhost:{port}"

        # Use first published port
        if service.ports:
            port_str = service.ports[0]
            host_port = int(port_str.split(":")[0])
            return f"localhost:{host_port}"

        # Use container-internal address (for service-to-service)
        env_name = self.config.metadata.name
        return f"{service_name}.{env_name}_default"

    def get_internal_url(self, service_name: str, port: Optional[int] = None) -> str:
        """Get the internal Docker network URL (for service-to-service)."""
        service = self.config.spec.services.get(service_name)
        if not service:
            raise ValueError(f"Service '{service_name}' not found")

        target_port = port or service.ports[0].split(":")[-1] if service.ports else ""
        env_name = self.config.metadata.name

        if target_port:
            return f"{service_name}:{target_port}"
        return service_name
```

### DNS Resolution
- Docker's embedded DNS server resolves service names within a network
- Services on the same network can communicate using service name as hostname
- Example: `mongodb://mongo:27017/myapp` from node service
- Network aliases allow alternative names

### Port Mapping Rules
1. Host port must be unique across all services
2. Container port can be shared (different containers, same internal port)
3. Port range: 1024-65535 for user services (avoid system ports)
4. Auto-allocation: If port 3000 is taken, suggest 3001, 3002, etc.

### Network Isolation
- Default network: All services join by default
- Frontend network: Only services exposed to users (nginx, node)
- Backend network: Only internal services (databases, caches)
- Custom networks: User-defined isolation boundaries

---

## D. Lifecycle Management

### Full Lifecycle States

```python
# backend/app/engine/lifecycle.py

from enum import Enum
from typing import Dict, List, Optional, Any

class ServiceState(str, Enum):
    PENDING = "pending"           # Defined but not started
    CREATING = "creating"         # Container being created
    STARTING = "starting"         # Container starting up
    HEALTHY = "healthy"           # Service ready to use
    UNHEALTHY = "unhealthy"       # Service running but failing health checks
    RUNNING = "running"           # Running (no health check configured)
    STOPPED = "stopped"           # Explicitly stopped
    ERROR = "error"               # Failed to start
    REMOVING = "removing"         # Being removed
    REMOVED = "removed"           # Successfully removed

class EnvironmentState(str, Enum):
    EMPTY = "empty"               # No services defined
    PLANNING = "planning"         # Creating execution plan
    STARTING = "starting"         # Services being started
    RUNNING = "running"           # All services healthy
    PARTIAL = "partial"           # Some services unhealthy
    STOPPING = "stopping"         # Services being stopped
    STOPPED = "stopped"           # All services stopped
    ERROR = "error"               # Setup failed


class LifecycleManager:
    """Manages the full lifecycle of environments and services."""

    def __init__(self):
        self.environments: Dict[str, Dict[str, Any]] = {}

    async def create_environment(self, config: EnvironmentConfig) -> str:
        """Create a new environment from config."""
        env_id = config.metadata.name
        self.environments[env_id] = {
            "config": config,
            "state": EnvironmentState.PLANNING,
            "services": {},
            "created_at": datetime.now(timezone.utc),
        }
        return env_id

    async def start_service(self, env_id: str, service_name: str) -> Dict:
        """Start a single service."""
        env = self.environments[env_id]
        service_config = env["config"].spec.services[service_name]

        # Check dependencies first
        for dep_name, dep_config in service_config.dependsOn.items():
            dep_state = env["services"].get(dep_name, {}).get("state")
            if dep_config.condition == "service_healthy":
                if dep_state != ServiceState.HEALTHY:
                    raise DependencyNotReadyError(dep_name, dep_state)

        # Execute start steps
        plan = await plan_service_start(service_name, service_config)
        result = await execute_plan(plan)

        env["services"][service_name] = {
            "state": ServiceState.STARTING,
            "container_id": result.get("container_id"),
            "started_at": datetime.now(timezone.utc),
        }

        return result

    async def stop_service(self, env_id: str, service_name: str) -> Dict:
        """Stop a single service."""
        env = self.environments[env_id]

        # Check if other services depend on this one
        dependents = self._get_dependents(env_id, service_name)
        if dependents:
            raise HasDependentsError(service_name, dependents)

        result = await run_command([
            "docker", "stop", f"envman_{service_name}"
        ])

        env["services"][service_name]["state"] = ServiceState.STOPPED
        return result

    async def restart_service(self, env_id: str, service_name: str) -> Dict:
        """Restart a single service."""
        await self.stop_service(env_id, service_name)
        return await self.start_service(env_id, service_name)

    async def get_logs(self, env_id: str, service_name: str,
                       tail: int = 100, follow: bool = False) -> Any:
        """Get logs from a service."""
        cmd = ["docker", "logs", f"envman_{service_name}"]
        if tail:
            cmd.extend(["--tail", str(tail)])
        if follow:
            cmd.append("--follow")
        return await run_command(cmd)

    async def destroy_environment(self, env_id: str) -> Dict:
        """Destroy all resources in an environment."""
        env = self.environments[env_id]
        results = []

        # Stop and remove containers in reverse dependency order
        for service_name in reversed(list(env["config"].spec.services.keys())):
            try:
                await self.remove_service(env_id, service_name)
                results.append({"service": service_name, "status": "removed"})
            except Exception as e:
                results.append({"service": service_name, "error": str(e)})

        # Remove networks
        for net_name in env["config"].spec.networks:
            await run_command([
                "docker", "network", "rm",
                f"{env_id}_{net_name}"
            ])

        # Remove volumes
        for vol_name in env["config"].spec.volumes:
            await run_command([
                "docker", "volume", "rm",
                f"{env_id}_{vol_name}"
            ])

        env["state"] = EnvironmentState.STOPPED
        return {"results": results}

    async def export_environment(self, env_id: str) -> Dict:
        """Export environment config for sharing."""
        env = self.environments[env_id]
        return env["config"].model_dump()

    async def import_environment(self, config_data: Dict) -> str:
        """Import environment from config."""
        config = EnvironmentConfig(**config_data)
        return await self.create_environment(config)

    def _get_dependents(self, env_id: str, service_name: str) -> List[str]:
        """Find services that depend on the given service."""
        env = self.environments[env_id]
        dependents = []
        for name, config in env["config"].spec.services.items():
            if service_name in config.dependsOn:
                dependents.append(name)
        return dependents
```

---

## E. Verification Engine Enhancement

### Plugin-Based Health Check System

```python
# backend/app/engine/verifier_plugins.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio

class HealthCheckPlugin(ABC):
    """Base class for health check plugins."""

    @property
    @abstractmethod
    def service_type(self) -> str:
        """The service type this plugin handles."""
        pass

    @abstractmethod
    async def check(self, container_name: str, config: Dict) -> Dict[str, Any]:
        """Run health check and return result."""
        pass

    async def _run_command(self, cmd: list, timeout: int = 10) -> Dict:
        """Helper to run commands in container."""
        from app.engine.executor import run_command
        return await run_command(cmd, timeout=timeout)


class PostgresHealthCheck(HealthCheckPlugin):
    service_type = "postgres"

    async def check(self, container_name: str, config: Dict) -> Dict[str, Any]:
        checks = []

        # Check 1: pg_isready
        result = await self._run_command(
            ["docker", "exec", container_name, "pg_isready", "-U", "postgres"]
        )
        pg_ready = result["code"] == 0
        checks.append({
            "name": "pg_isready",
            "passed": pg_ready,
            "detail": "accepting connections" if pg_ready else "not accepting connections",
        })

        # Check 2: Run test query
        if pg_ready:
            result = await self._run_command(
                ["docker", "exec", container_name,
                 "psql", "-U", "postgres", "-c", "SELECT 1 AS connected;"]
            )
            checks.append({
                "name": "query_execution",
                "passed": result["code"] == 0,
                "detail": result["stdout"] if result["code"] == 0 else result["stderr"],
            })

        return {
            "service": "postgres",
            "status": "ready" if all(c["passed"] for c in checks) else "failed",
            "checks": checks,
        }


class RedisHealthCheck(HealthCheckPlugin):
    service_type = "redis"

    async def check(self, container_name: str, config: Dict) -> Dict[str, Any]:
        checks = []

        # Check 1: PING
        result = await self._run_command(
            ["docker", "exec", container_name, "redis-cli", "ping"]
        )
        ping_ok = result["code"] == 0 and "PONG" in result["stdout"]
        checks.append({
            "name": "ping",
            "passed": ping_ok,
            "detail": "responding" if ping_ok else "not responding",
        })

        # Check 2: SET/GET test
        if ping_ok:
            await self._run_command(
                ["docker", "exec", container_name,
                 "redis-cli", "set", "envman_test", "ok"]
            )
            result = await self._run_command(
                ["docker", "exec", container_name,
                 "redis-cli", "get", "envman_test"]
            )
            data_ok = result["code"] == 0 and "ok" in result["stdout"]
            checks.append({
                "name": "read_write",
                "passed": data_ok,
                "detail": "read/write working" if data_ok else "read/write failed",
            })
            await self._run_command(
                ["docker", "exec", container_name,
                 "redis-cli", "del", "envman_test"]
            )

        return {
            "service": "redis",
            "status": "ready" if all(c["passed"] for c in checks) else "failed",
            "checks": checks,
        }


class MongoHealthCheck(HealthCheckPlugin):
    service_type = "mongodb"

    async def check(self, container_name: str, config: Dict) -> Dict[str, Any]:
        checks = []

        # Check 1: Ping
        result = await self._run_command(
            ["docker", "exec", container_name,
             "mongosh", "--eval", "db.adminCommand({ping:1})", "--quiet"]
        )
        ping_ok = result["code"] == 0
        checks.append({
            "name": "ping",
            "passed": ping_ok,
            "detail": "responding" if ping_ok else "not responding",
        })

        # Check 2: Insert and query
        if ping_ok:
            result = await self._run_command(
                ["docker", "exec", container_name,
                 "mongosh", "--eval",
                 "db.envman_test.insertOne({test:true}); db.envman_test.findOne();",
                 "--quiet"]
            )
            checks.append({
                "name": "read_write",
                "passed": result["code"] == 0,
                "detail": "read/write working" if result["code"] == 0 else result["stderr"],
            })

        return {
            "service": "mongodb",
            "status": "ready" if all(c["passed"] for c in checks) else "failed",
            "checks": checks,
        }


class NodeHealthCheck(HealthCheckPlugin):
    service_type = "node"

    async def check(self, container_name: str, config: Dict) -> Dict[str, Any]:
        checks = []

        # Check 1: Node version
        result = await self._run_command(
            ["docker", "exec", container_name, "node", "-v"]
        )
        version = result["stdout"].strip() if result["code"] == 0 else None
        checks.append({
            "name": "node_version",
            "passed": result["code"] == 0,
            "detail": version or "could not get version",
        })

        # Check 2: npm available
        result = await self._run_command(
            ["docker", "exec", container_name, "npm", "--version"]
        )
        npm_ok = result["code"] == 0
        checks.append({
            "name": "npm_available",
            "passed": npm_ok,
            "detail": f"npm {result['stdout'].strip()}" if npm_ok else "npm not found",
        })

        return {
            "service": "node",
            "status": "ready" if all(c["passed"] for c in checks) else "failed",
            "version": version,
            "checks": checks,
        }


class HTTPHealthCheck(HealthCheckPlugin):
    """Generic HTTP health check for any service."""
    service_type = "_http"

    async def check(self, container_name: str, config: Dict) -> Dict[str, Any]:
        url = config.get("healthCheck", {}).get("url")
        if not url:
            return {"service": container_name, "status": "skipped", "checks": []}

        result = await self._run_command(
            ["docker", "exec", container_name, "curl", "-sf", url]
        )

        return {
            "service": container_name,
            "status": "ready" if result["code"] == 0 else "failed",
            "checks": [{
                "name": "http_check",
                "passed": result["code"] == 0,
                "detail": url,
            }],
        }


# Plugin registry
HEALTH_CHECK_PLUGINS: Dict[str, HealthCheckPlugin] = {
    "postgres": PostgresHealthCheck(),
    "redis": RedisHealthCheck(),
    "mongodb": MongoHealthCheck(),
    "node": NodeHealthCheck(),
    "_http": HTTPHealthCheck(),
}


class UniversalVerifier:
    """Plugin-based verification engine."""

    def __init__(self):
        self.plugins = HEALTH_CHECK_PLUGINS

    def register_plugin(self, plugin: HealthCheckPlugin):
        """Register a custom health check plugin."""
        self.plugins[plugin.service_type] = plugin

    async def verify_service(self, service_name: str, service_config: Dict) -> Dict:
        """Verify a single service using the appropriate plugin."""
        container_name = f"envman_{service_name}"
        service_type = service_config.get("type", "_http")

        # Find the right plugin
        plugin = self.plugins.get(service_type)
        if not plugin:
            plugin = self.plugins.get("_http")

        if not plugin:
            return {
                "service": service_name,
                "status": "no_plugin",
                "checks": [],
            }

        return await plugin.check(container_name, service_config)

    async def verify_all(self, config: EnvironmentConfig) -> List[Dict]:
        """Verify all services in the environment."""
        results = []
        for name, service_config in config.spec.services.items():
            result = await self.verify_service(name, service_config.model_dump())
            results.append(result)
        return results
```

---

# Part 3: Compatibility Matrix

## Service Compatibility Matrix

```
┌─────────────────┬────────┬────────┬────────┬────────┬────────┬────────┬────────┐
│ Service         │ Node   │ Python │ Go     │ Rust   │ Java   │ Ruby   │ PHP    │
├─────────────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│ PostgreSQL      │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ MySQL           │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ MongoDB         │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ⚠️   │
│ Redis           │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ Elasticsearch   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ RabbitMQ        │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ Kafka           │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ⚠️   │   ⚠️   │
│ NATS            │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ MinIO           │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ Nginx           │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
│ MailHog         │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
└─────────────────┴────────┴────────┴────────┴────────┴────────┴────────┴────────┘
✅ = Fully compatible  ⚠️ = Limited support  ❌ = Not recommended
```

## Version Compatibility

```
┌─────────────────┬─────────────────────────────────────────────────────────────┐
│ Service         │ Known Compatible Versions                                   │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ Node 18         │ PostgreSQL 14-17, Redis 6-7, MongoDB 6-7, MySQL 8.x       │
│ Node 20         │ PostgreSQL 14-17, Redis 6-7, MongoDB 6-7, MySQL 8.x       │
│ Node 22         │ PostgreSQL 15-17, Redis 7, MongoDB 7, MySQL 8.4            │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ Python 3.10     │ PostgreSQL 14-16, Redis 6-7, MongoDB 6-7, MySQL 8.x       │
│ Python 3.12     │ PostgreSQL 14-17, Redis 6-7, MongoDB 6-7, MySQL 8.x       │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ Go 1.21         │ PostgreSQL 14-16, Redis 6-7, MongoDB 6-7                  │
│ Go 1.22         │ PostgreSQL 14-17, Redis 6-7, MongoDB 6-7                  │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ PostgreSQL 14   │ Node 18-22, Python 3.10-3.12, Go 1.21-1.22                │
│ PostgreSQL 16   │ Node 18-22, Python 3.10-3.12, Go 1.21-1.22                │
│ PostgreSQL 17   │ Node 20-22, Python 3.12, Go 1.22                          │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ Redis 6         │ All runtimes                                              │
│ Redis 7         │ All runtimes                                              │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ MongoDB 6       │ Node 18-20, Python 3.10-3.11                              │
│ MongoDB 7       │ Node 18-22, Python 3.10-3.12                              │
└─────────────────┴─────────────────────────────────────────────────────────────┘
```

## Port Conflict Detection Rules

```python
# backend/app/engine/port_checker.py

PORT_CONFLICT_RULES = {
    # Conflicts that will always fail
    "hard_conflicts": {
        3000: ["node", "grafana"],      # Both default to 3000
        5432: ["postgres"],
        3306: ["mysql"],
        6379: ["redis"],
        27017: ["mongodb"],
    },

    # Services that can share ports with configuration
    "soft_conflicts": {
        80: ["nginx", "traefik"],       # Can use different host ports
        8080: ["traefik", "prometheus"], # Dashboard ports
    },

    # Auto-remap rules
    "auto_remap": {
        3000: [3000, 3001, 3002, 3003, 3004, 3005],
        5432: [5432, 5433, 5434],
        6379: [6379, 6380, 6381],
    },
}

# Platform-specific port restrictions
PLATFORM_PORT_RULES = {
    "linux": {
        "privileged_ports": list(range(1, 1024)),  # Need root
        "ephemeral_ports": list(range(49152, 65535)),
    },
    "macos": {
        "privileged_ports": [],  # No restriction on macOS
        "common_blocked": [0],   # Port 0 always blocked
    },
    "windows": {
        "privileged_ports": [],  # No restriction on Windows
        "hyper_v_reserved": [3785, 4500, 5000, 5355, 8100],
    },
}
```

## Resource Requirements per Service

```
┌─────────────────┬────────────┬─────────┬──────────────────────────────────┐
│ Service         │ Min Memory │ Min CPU │ Notes                            │
├─────────────────┼────────────┼─────────┼──────────────────────────────────┤
│ Node.js         │ 128 Mi     │ 0.25    │ Depends on application           │
│ Python          │ 128 Mi     │ 0.25    │ Depends on application           │
│ Go              │ 64 Mi      │ 0.25    │ Low resource usage               │
│ Rust            │ 512 Mi     │ 0.5     │ Compilation needs more resources  │
│ Ruby            │ 128 Mi     │ 0.25    │ Rails apps need more             │
│ Java            │ 512 Mi     │ 0.5     │ JVM heap allocation              │
│ PHP             │ 64 Mi      │ 0.1     │ Very lightweight                 │
│ .NET            │ 256 Mi     │ 0.25    │ Runtime overhead                 │
├─────────────────┼────────────┼─────────┼──────────────────────────────────┤
│ PostgreSQL      │ 256 Mi     │ 0.25    │ Increase for production data     │
│ MySQL           │ 512 Mi     │ 0.5     │ InnoDB buffer pool               │
│ MongoDB         │ 256 Mi     │ 0.25    │ WiredTiger cache                 │
│ Redis           │ 128 Mi     │ 0.1     │ In-memory, minimal overhead      │
│ SQLite          │ 64 Mi      │ 0.05    │ Embedded, no server overhead     │
│ Elasticsearch   │ 1 Gi       │ 1.0     │ JVM + Lucene index               │
│ CouchDB         │ 256 Mi     │ 0.25    │ B-tree storage                   │
├─────────────────┼────────────┼─────────┼──────────────────────────────────┤
│ RabbitMQ        │ 256 Mi     │ 0.25    │ Erlang runtime                   │
│ Kafka           │ 512 Mi     │ 0.5     │ JVM-based, needs disk I/O        │
│ NATS            │ 128 Mi     │ 0.1     │ Very lightweight                 │
├─────────────────┼────────────┼─────────┼──────────────────────────────────┤
│ MeiliSearch     │ 256 Mi     │ 0.25    │ Index in memory                  │
│ Typesense       │ 256 Mi     │ 0.25    │ Index in memory                  │
├─────────────────┼────────────┼─────────┼──────────────────────────────────┤
│ MinIO           │ 256 Mi     │ 0.25    │ Object storage                   │
│ Prometheus      │ 256 Mi     │ 0.25    │ Time-series database             │
│ Grafana         │ 128 Mi     │ 0.1     │ Visualization only               │
│ Nginx           │ 64 Mi      │ 0.05    │ Very lightweight                 │
│ Traefik         │ 64 Mi      │ 0.05    │ Very lightweight                 │
│ MailHog         │ 64 Mi      │ 0.05    │ Test email server                │
└─────────────────┴────────────┴─────────┴──────────────────────────────────┘
```

## Platform Compatibility

```
┌─────────────────┬─────────┬─────────┬─────────┬────────────────────────────┐
│ Service         │ Linux   │ macOS   │ Windows │ Notes                      │
├─────────────────┼─────────┼─────────┼─────────┼────────────────────────────┤
│ Node.js         │   ✅    │   ✅    │   ✅    │ Full support               │
│ Python          │   ✅    │   ✅    │   ✅    │ Full support               │
│ Go              │   ✅    │   ✅    │   ✅    │ Full support               │
│ Rust            │   ✅    │   ✅    │   ⚠️    │ Windows compilation slower  │
│ Ruby            │   ✅    │   ✅    │   ⚠️    │ Native extensions may fail  │
│ Java            │   ✅    │   ✅    │   ✅    │ Full support               │
│ PHP             │   ✅    │   ✅    │   ⚠️    │ Some extensions missing     │
│ .NET            │   ✅    │   ✅    │   ✅    │ Full support               │
├─────────────────┼─────────┼─────────┼─────────┼────────────────────────────┤
│ PostgreSQL      │   ✅    │   ✅    │   ✅    │ Full support               │
│ MySQL           │   ✅    │   ✅    │   ✅    │ Full support               │
│ MongoDB         │   ✅    │   ✅    │   ✅    │ Full support               │
│ Redis           │   ✅    │   ✅    │   ✅    │ Full support               │
│ SQLite          │   ✅    │   ✅    │   ✅    │ Embedded, universal        │
│ Elasticsearch   │   ✅    │   ⚠️    │   ⚠️    │ Needs Java, high memory    │
│ CouchDB         │   ✅    │   ✅    │   ✅    │ Full support               │
├─────────────────┼─────────┼─────────┼─────────┼────────────────────────────┤
│ RabbitMQ        │   ✅    │   ✅    │   ✅    │ Full support               │
│ Kafka           │   ✅    │   ⚠️    │   ⚠️    │ Resource intensive         │
│ NATS            │   ✅    │   ✅    │   ✅    │ Full support               │
├─────────────────┼─────────┼─────────┼─────────┼────────────────────────────┤
│ MinIO           │   ✅    │   ✅    │   ✅    │ Full support               │
│ Prometheus      │   ✅    │   ✅    │   ✅    │ Full support               │
│ Grafana         │   ✅    │   ✅    │   ✅    │ Full support               │
│ Nginx           │   ✅    │   ✅    │   ⚠️    │ Windows config differs     │
│ Traefik         │   ✅    │   ✅    │   ✅    │ Full support               │
│ MailHog         │   ✅    │   ✅    │   ✅    │ Full support               │
└─────────────────┴─────────┴─────────┴─────────┴────────────────────────────┘
✅ = Fully supported  ⚠️ = Limited/partial support  ❌ = Not supported
```

---

# Part 4: Data Model

## 1. Environment Config Schema

```python
# backend/app/models/environment.py (expanded)

from pydantic import BaseModel, field_validator, model_validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from enum import Enum

class EnvironmentStatus(str, Enum):
    DRAFT = "draft"
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class EnvironmentConfig(BaseModel):
    """Complete environment configuration."""
    id: Optional[str] = None
    apiVersion: str = "envman.dev/v1"
    kind: str = "Environment"
    metadata: EnvironmentMetadata
    spec: EnvironmentSpec
    status: EnvironmentStatus = EnvironmentStatus.DRAFT
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('metadata.name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        import re
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', v):
            raise ValueError(
                "Name must be lowercase alphanumeric with hyphens, "
                "starting with alphanumeric"
            )
        if len(v) > 63:
            raise ValueError("Name must be 63 characters or less")
        return v

class EnvironmentSummary(BaseModel):
    """Summary for listing environments."""
    id: str
    name: str
    description: str
    status: EnvironmentStatus
    serviceCount: int
    createdAt: datetime
    updatedAt: datetime
```

## 2. Service Definition Schema

```python
# backend/app/models/service.py

class ServiceStatus(str, Enum):
    PENDING = "pending"
    CREATING = "creating"
    STARTING = "starting"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class ServiceInstance(BaseModel):
    """Runtime state of a service instance."""
    id: str
    name: str
    type: str
    image: str
    containerId: Optional[str] = None
    status: ServiceStatus = ServiceStatus.PENDING
    ports: List[str] = []
    networks: List[str] = []
    volumes: List[str] = []
    env: Dict[str, str] = {}
    healthCheckStatus: Optional[str] = None
    lastHealthCheck: Optional[datetime] = None
    startedAt: Optional[datetime] = None
    stoppedAt: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
```

## 3. Step Plan Schema

```python
# backend/app/models/step.py (expanded)

class StepType(str, Enum):
    PULL_IMAGE = "pull_image"
    CREATE_NETWORK = "create_network"
    CONNECT_NETWORK = "connect_network"
    CREATE_VOLUME = "create_volume"
    REMOVE_CONTAINER = "remove_container"
    START_CONTAINER = "start_container"
    STOP_CONTAINER = "stop_container"
    EXEC_COMMAND = "exec_command"
    VERIFY_HEALTH = "verify_health"
    REMOVE_NETWORK = "remove_network"
    REMOVE_VOLUME = "remove_volume"

class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

class Step(BaseModel):
    """One action in the execution plan."""
    id: str
    type: StepType
    params: Dict[str, Any]
    dependsOn: Optional[Union[str, List[str]]] = None
    status: StepStatus = StepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    retryCount: int = 0
    maxRetries: int = 3

class Plan(BaseModel):
    """Execution plan for environment setup."""
    id: str
    steps: List[Step]
    environmentId: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: StepStatus = StepStatus.PENDING
```

## 4. Verification Result Schema

```python
# backend/app/models/verification.py

class CheckResult(BaseModel):
    """Result of a single health check."""
    name: str
    passed: bool
    detail: str
    duration_ms: Optional[int] = None

class ServiceVerification(BaseModel):
    """Verification results for a single service."""
    service: str
    status: str  # "ready", "failed", "not_tracked", "not_found", "not_running"
    version: Optional[str] = None
    checks: List[CheckResult] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnvironmentVerification(BaseModel):
    """Complete verification report for an environment."""
    environmentId: str
    services: List[ServiceVerification]
    allReady: bool
    duration_ms: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

## 5. Event Schema for WebSocket

```python
# backend/app/events/schemas.py

from pydantic import BaseModel
from typing import Any, Dict, Optional, List
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    # Setup lifecycle
    SETUP_STARTED = "setup_started"
    SETUP_COMPLETED = "setup_completed"
    SETUP_FAILED = "setup_failed"

    # Step events
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"

    # Verification
    VERIFY_STARTED = "verify_started"
    VERIFY_COMPLETED = "verify_completed"

    # Service lifecycle
    SERVICE_STARTED = "service_started"
    SERVICE_STOPPED = "service_stopped"
    SERVICE_HEALTHY = "service_healthy"
    SERVICE_UNHEALTHY = "service_unhealthy"

    # Logs
    LOG_LINE = "log_line"

    # Status
    STATUS_UPDATE = "status_update"

class WSEvent(BaseModel):
    """WebSocket event message."""
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SetupStartedData(BaseModel):
    environmentId: str
    totalSteps: int
    services: List[str]

class StepStartedData(BaseModel):
    stepId: str
    stepType: str
    stepIndex: int
    totalSteps: int
    message: str

class StepCompletedData(BaseModel):
    stepId: str
    stepIndex: int
    totalSteps: int
    message: str
    duration_ms: int

class StepFailedData(BaseModel):
    stepId: str
    stepIndex: int
    totalSteps: int
    error: str
    message: str

class LogLineData(BaseModel):
    service: str
    line: str
    stream: str  # "stdout" or "stderr"
    timestamp: datetime

class ServiceStatusData(BaseModel):
    service: str
    status: str
    healthCheckStatus: Optional[str] = None
```

---

# Part 5: API Design

## REST API Endpoints

```python
# backend/app/api/routes.py (expanded)

from fastapi import APIRouter, HTTPException, Query, WebSocket
from typing import List, Optional
from app.models.environment import EnvironmentConfig, EnvironmentSummary
from app.models.verification import EnvironmentVerification
from app.models.step import Plan

router = APIRouter(prefix="/api/v1", tags=["environments"])

# ============================================================
# Environment CRUD
# ============================================================

@router.post("/environments", response_model=EnvironmentConfig, status_code=201)
async def create_environment(config: EnvironmentConfig):
    """Create a new environment from config."""
    pass

@router.get("/environments", response_model=List[EnvironmentSummary])
async def list_environments(
    status: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List all environments with optional filtering."""
    pass

@router.get("/environments/{env_id}", response_model=EnvironmentConfig)
async def get_environment(env_id: str):
    """Get detailed environment configuration and status."""
    pass

@router.put("/environments/{env_id}", response_model=EnvironmentConfig)
async def update_environment(env_id: str, config: EnvironmentConfig):
    """Update environment configuration."""
    pass

@router.delete("/environments/{env_id}", status_code=204)
async def delete_environment(env_id: str):
    """Delete an environment and all its resources."""
    pass

# ============================================================
# Environment Lifecycle
# ============================================================

@router.post("/environments/{env_id}/start")
async def start_environment(env_id: str):
    """Start all services in an environment."""
    pass

@router.post("/environments/{env_id}/stop")
async def stop_environment(env_id: str):
    """Stop all services in an environment."""
    pass

@router.post("/environments/{env_id}/restart")
async def restart_environment(env_id: str):
    """Restart all services in an environment."""
    pass

# ============================================================
# Service Management
# ============================================================

@router.get("/environments/{env_id}/services")
async def list_services(env_id: str):
    """List all services in an environment with their status."""
    pass

@router.get("/environments/{env_id}/services/{service_name}")
async def get_service(env_id: str, service_name: str):
    """Get details of a specific service."""
    pass

@router.post("/environments/{env_id}/services/{service_name}/start")
async def start_service(env_id: str, service_name: str):
    """Start a specific service."""
    pass

@router.post("/environments/{env_id}/services/{service_name}/stop")
async def stop_service(env_id: str, service_name: str):
    """Stop a specific service."""
    pass

@router.post("/environments/{env_id}/services/{service_name}/restart")
async def restart_service(env_id: str, service_name: str):
    """Restart a specific service."""
    pass

# ============================================================
# Logs
# ============================================================

@router.get("/environments/{env_id}/services/{service_name}/logs")
async def get_service_logs(
    env_id: str,
    service_name: str,
    tail: int = Query(default=100, ge=1, le=10000),
    follow: bool = Query(default=False),
):
    """Get logs from a service."""
    pass

# ============================================================
# Health Monitoring
# ============================================================

@router.get("/environments/{env_id}/health")
async def get_environment_health(env_id: str):
    """Get health status of all services."""
    pass

@router.post("/environments/{env_id}/verify", response_model=EnvironmentVerification)
async def verify_environment(env_id: str):
    """Run verification checks on all services."""
    pass

@router.get("/environments/{env_id}/services/{service_name}/health")
async def get_service_health(env_id: str, service_name: str):
    """Get health status of a specific service."""
    pass

# ============================================================
# Configuration Import/Export
# ============================================================

@router.get("/environments/{env_id}/export")
async def export_environment(env_id: str, format: str = Query(default="yaml")):
    """Export environment config for sharing."""
    pass

@router.post("/environments/import", status_code=201)
async def import_environment(config: dict):
    """Import environment from config."""
    pass

# ============================================================
# Service Registry
# ============================================================

@router.get("/registry/services")
async def list_available_services(
    category: Optional[str] = None,
    tags: Optional[List[str]] = Query(default=None),
):
    """List available service types."""
    pass

@router.get("/registry/services/{service_type}")
async def get_service_definition(service_type: str):
    """Get definition of a service type."""
    pass

# ============================================================
# Templates
# ============================================================

@router.get("/templates")
async def list_templates(category: Optional[str] = None):
    """List available environment templates."""
    pass

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a template configuration."""
    pass

@router.post("/templates/{template_id}/instantiate", status_code=201)
async def instantiate_template(template_id: str, name: str):
    """Create an environment from a template."""
    pass

# ============================================================
# WebSocket for real-time updates
# ============================================================

@router.websocket("/ws/environments/{env_id}")
async def environment_websocket(websocket: WebSocket, env_id: str):
    """WebSocket for real-time environment updates."""
    pass
```

## API Response Formats

```json
// GET /api/v1/environments
{
  "data": [
    {
      "id": "my-mern-project",
      "name": "my-mern-project",
      "description": "MERN stack with Redis",
      "status": "running",
      "serviceCount": 3,
      "createdAt": "2026-08-30T10:00:00Z",
      "updatedAt": "2026-08-30T10:05:00Z"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 50,
    "offset": 0
  }
}

// POST /api/v1/environments
// Request:
{
  "metadata": {
    "name": "my-mern-project",
    "description": "MERN stack with Redis"
  },
  "spec": {
    "services": {
      "node": {
        "type": "runtime",
        "image": "node:20-alpine",
        "ports": ["3000:3000"],
        "env": {"NODE_ENV": "development"}
      }
    }
  }
}
// Response: 201 Created
{
  "id": "my-mern-project",
  "status": "draft",
  "createdAt": "2026-08-30T10:00:00Z"
}

// WebSocket Event
{
  "type": "step_completed",
  "data": {
    "stepId": "start_node",
    "stepType": "start_container",
    "stepIndex": 3,
    "totalSteps": 5,
    "message": "Container 'envman_node' started",
    "duration_ms": 1200
  },
  "timestamp": "2026-08-30T10:02:30Z"
}
```

---

# Part 6: Implementation Roadmap

## Phase 1: Core Infrastructure (Weeks 1-4)

### Goal
Networking, volumes, config persistence, and universal service support.

### Files to Create/Modify

```
backend/
├── app/
│   ├── models/
│   │   ├── environment.py          # MODIFY: Expand to full schema
│   │   ├── service.py              # CREATE: Service instance model
│   │   ├── config.py               # CREATE: Universal config schema
│   │   ├── step.py                 # MODIFY: Add new step types
│   │   ├── plan.py                 # MODIFY: Enhanced plan model
│   │   └── verification.py         # CREATE: Verification result model
│   ├── engine/
│   │   ├── planner.py              # MODIFY: Support all service types
│   │   ├── executor.py             # MODIFY: Add volume/network/volume steps
│   │   ├── verifier.py             # MODIFY: Plugin-based verification
│   │   ├── coordinator.py          # MODIFY: Enhanced orchestration
│   │   ├── networking.py           # CREATE: Network management
│   │   ├── lifecycle.py            # CREATE: Full lifecycle management
│   │   ├── port_checker.py         # CREATE: Port conflict detection
│   │   ├── verifier_plugins/
│   │   │   ├── __init__.py
│   │   │   ├── postgres.py         # CREATE
│   │   │   ├── redis.py            # CREATE
│   │   │   ├── mongodb.py          # CREATE
│   │   │   ├── node.py             # CREATE
│   │   │   └── generic.py          # CREATE: HTTP/TCP/generic checks
│   │   └── state.py                # MODIFY: Enhanced state tracking
│   ├── registry/
│   │   ├── __init__.py
│   │   ├── schema.py               # CREATE: Service definition schema
│   │   ├── services.py             # CREATE: Complete service registry
│   │   └── templates.py            # CREATE: Pre-built templates
│   ├── api/
│   │   ├── routes.py               # MODIFY: Full REST API
│   │   ├── ws.py                   # MODIFY: Enhanced WebSocket
│   │   └── deps.py                 # CREATE: Dependency injection
│   ├── storage/
│   │   ├── db.py                   # CREATE: SQLite persistence
│   │   └── repository.py           # CREATE: Data access layer
│   └── core/
│       ├── config.py               # CREATE: App configuration
│       └── platform.py             # CREATE: Platform detection

frontend/
├── src/
│   ├── components/
│   │   ├── configure/
│   │   │   ├── ConfigureScreen.jsx # MODIFY: Dynamic service selection
│   │   │   ├── ServicePicker.jsx   # CREATE: Service type picker
│   │   │   ├── ServiceConfig.jsx   # CREATE: Per-service configuration
│   │   │   └── NetworkConfig.jsx   # CREATE: Network settings
│   │   ├── progress/
│   │   │   ├── ProgressScreen.jsx  # MODIFY: Show all service types
│   │   │   └── StepItem.jsx        # MODIFY: Show step details
│   │   ├── results/
│   │   │   ├── ResultsScreen.jsx   # MODIFY: Show all services
│   │   │   └── ServiceCard.jsx     # MODIFY: Enhanced status display
│   │   └── shared/
│   │       └── ...                 # Reuse existing components
│   ├── hooks/
│   │   ├── useWebSocket.js         # MODIFY: Handle new event types
│   │   └── useEnvironment.js       # CREATE: Environment state management
│   └── api/
│       └── client.js               # CREATE: API client
```

### Database Schema Changes

```sql
-- backend/app/storage/migrations/001_initial.sql

CREATE TABLE environments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    config JSON NOT NULL,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE services (
    id TEXT PRIMARY KEY,
    environment_id TEXT NOT NULL REFERENCES environments(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    image TEXT NOT NULL,
    container_id TEXT,
    status TEXT DEFAULT 'pending',
    config JSON NOT NULL,
    health_check_status TEXT,
    last_health_check TIMESTAMP,
    started_at TIMESTAMP,
    stopped_at TIMESTAMP,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(environment_id, name)
);

CREATE TABLE steps (
    id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    environment_id TEXT NOT NULL REFERENCES environments(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    params JSON NOT NULL,
    depends_on TEXT,
    status TEXT DEFAULT 'pending',
    result JSON,
    error TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE verification_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    environment_id TEXT NOT NULL REFERENCES environments(id) ON DELETE CASCADE,
    service_name TEXT NOT NULL,
    status TEXT NOT NULL,
    checks JSON NOT NULL,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Testing Strategy
- Unit tests for all models (pytest + pydantic)
- Integration tests for planner, executor, verifier
- End-to-end tests with Docker daemon
- Frontend component tests (Vitest + React Testing Library)
- API contract tests (httpx + FastAPI TestClient)

---

## Phase 2: Service Expansion (Weeks 5-8)

### Goal
Add databases, caches, message queues, search engines, storage.

### Files to Create/Modify

```
backend/
├── app/
│   ├── engine/
│   │   └── verifier_plugins/
│   │       ├── mysql.py            # CREATE
│   │       ├── elasticsearch.py    # CREATE
│   │       ├── rabbitmq.py         # CREATE
│   │       ├── kafka.py            # CREATE
│   │       └── minio.py            # CREATE
│   └── registry/
│       └── services.py             # MODIFY: Add all service definitions

frontend/
├── src/
│   └── components/
│       ├── configure/
│       │   ├── ServiceCategory.jsx # CREATE: Category tabs (DB, Cache, etc.)
│       │   └── ServiceVersions.jsx # CREATE: Version selector per service
│       └── templates/
│           ├── TemplateList.jsx    # CREATE: Template browser
│           └── TemplateCard.jsx    # CREATE: Template preview
```

### Additional Testing
- Per-service integration tests
- Health check plugin tests
- Template instantiation tests
- Port conflict detection tests

---

## Phase 3: Developer Experience (Weeks 9-12)

### Goal
Templates, IDE integration, logs, config import/export.

### Files to Create/Modify

```
backend/
├── app/
│   ├── api/
│   │   └── routes.py               # MODIFY: Add template/export endpoints
│   └── registry/
│       └── templates.py            # MODIFY: Add more templates

frontend/
├── src/
│   ├── components/
│   │   ├── logs/
│   │   │   ├── LogViewer.jsx       # CREATE: Unified log view
│   │   │   ├── LogLine.jsx         # CREATE: Individual log line
│   │   │   └── LogFilter.jsx       # CREATE: Filter by service/stream
│   │   ├── editor/
│   │   │   ├── ConfigEditor.jsx    # CREATE: YAML/JSON config editor
│   │   │   └── ConfigPreview.jsx   # CREATE: Live preview of changes
│   │   └── templates/
│   │       ├── TemplateGallery.jsx # CREATE: Template browsing
│   │       └── TemplateBuilder.jsx # CREATE: Custom template creation
│   └── hooks/
│       └── useLogs.js              # CREATE: Log streaming hook
```

### New API Endpoints
- `GET /api/v1/environments/{id}/logs/stream` (WebSocket)
- `POST /api/v1/environments/{id}/export`
- `POST /api/v1/environments/import`
- `GET /api/v1/templates`
- `POST /api/v1/templates/{id}/instantiate`

---

## Phase 4: Collaboration (Weeks 13-16)

### Goal
Sharing, team workspaces, configuration sync.

### Files to Create/Modify

```
backend/
├── app/
│   ├── models/
│   │   └── team.py                 # CREATE: Team/workspace model
│   ├── api/
│   │   └── routes.py               # MODIFY: Team endpoints
│   └── storage/
│       └── migrations/
│           └── 002_teams.sql       # CREATE: Team schema

frontend/
├── src/
│   ├── components/
│   │   ├── teams/
│   │   │   ├── TeamSettings.jsx    # CREATE: Team management
│   │   │   └── SharedEnvironments.jsx # CREATE: Shared env list
│   │   └── sharing/
│   │       ├── ShareDialog.jsx     # CREATE: Share environment
│   │       └── Permissions.jsx     # CREATE: Access control
```

### Database Schema Changes
```sql
CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE team_members (
    team_id TEXT REFERENCES teams(id),
    user_id TEXT,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shared_environments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    environment_id TEXT REFERENCES environments(id),
    team_id TEXT REFERENCES teams(id),
    shared_by TEXT,
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Phase 5: Advanced Features (Weeks 17-24)

### Goal
Scaling, monitoring, cloud deployment, AI-powered setup.

### Files to Create/Modify

```
backend/
├── app/
│   ├── engine/
│   │   ├── scaler.py               # CREATE: Service scaling
│   │   ├── monitor.py              # CREATE: Resource monitoring
│   │   └── cloud.py                # CREATE: Cloud deployment
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── config_generator.py     # CREATE: AI config generation
│   │   └── nlp_parser.py           # CREATE: Natural language parsing
│   └── api/
│       └── routes.py               # MODIFY: Scaling/monitoring endpoints

frontend/
├── src/
│   ├── components/
│   │   ├── monitoring/
│   │   │   ├── ResourceChart.jsx   # CREATE: CPU/memory charts
│   │   │   └── ServiceMetrics.jsx  # CREATE: Per-service metrics
│   │   ├── ai/
│   │   │   ├── NaturalLanguageInput.jsx # CREATE: "I need MERN with Redis"
│   │   │   └── ConfigSuggestions.jsx    # CREATE: AI suggestions
│   │   └── scaling/
│   │       ├── ScaleControls.jsx   # CREATE: Scale up/down
│   │       └── ReplicaList.jsx     # CREATE: List replicas
```

### New Capabilities
- Horizontal scaling for stateless services
- Resource monitoring (CPU, memory, network)
- Cloud deployment (AWS, GCP, Azure)
- AI-powered configuration from natural language
- Environment snapshots and restore
- Dependency graph visualization

---

# Part 7: Technical Differentiators

## 1. AI-Powered Setup

```python
# backend/app/ai/config_generator.py

class ConfigGenerator:
    """Generate environment configs from natural language."""

    def __init__(self):
        self.service_patterns = {
            "mern": ["node", "mongodb", "redis"],
            "mean": ["node", "mongodb", "nginx"],
            "lamp": ["php", "mysql", "nginx"],
            "python web": ["python", "postgres", "redis"],
            "microservices": ["node", "redis", "rabbitmq", "nginx"],
        }

    async def generate_from_description(self, description: str) -> EnvironmentConfig:
        """Convert natural language to environment config.

        Examples:
        - "I need a MERN stack with Redis for caching"
        - "Python FastAPI with Postgres and Redis"
        - "Java Spring Boot with MySQL and RabbitMQ"
        """
        # Parse description to identify services
        identified_services = self._parse_services(description)

        # Resolve versions based on "latest" or specific requirements
        resolved_services = self._resolve_versions(identified_services)

        # Generate port mappings
        port_assignments = self._assign_ports(resolved_services)

        # Create environment config
        return self._build_config(description, resolved_services, port_assignments)

    def _parse_services(self, description: str) -> List[str]:
        """Extract service names from description."""
        services = []
        desc_lower = description.lower()

        # Check for common stack patterns
        for pattern, stack_services in self.service_patterns.items():
            if pattern in desc_lower:
                services.extend(stack_services)

        # Check for explicit service mentions
        service_keywords = {
            "postgres": "postgres", "postgresql": "postgres",
            "mysql": "mysql",
            "mongo": "mongodb", "mongodb": "mongodb",
            "redis": "redis",
            "rabbitmq": "rabbitmq", "rabbit": "rabbitmq",
            "elasticsearch": "elasticsearch", "elastic": "elasticsearch",
            "kafka": "kafka",
            "nginx": "nginx",
            "node": "node", "nodejs": "node", "nextjs": "node",
            "python": "python", "fastapi": "python", "django": "python",
            "java": "java", "spring": "java",
            "ruby": "ruby", "rails": "ruby",
        }

        for keyword, service in service_keywords.items():
            if keyword in desc_lower and service not in services:
                services.append(service)

        return services

    def _assign_ports(self, services: List[str]) -> Dict[str, int]:
        """Assign ports avoiding conflicts."""
        port_map = {}
        next_port = {
            "runtime": 3000,
            "database": 5432,
            "cache": 6379,
            "queue": 5672,
            "search": 9200,
            "proxy": 80,
        }

        for service in services:
            category = self._get_service_category(service)
            base_port = next_port.get(category, 8000)

            # Find available port
            while base_port in port_map.values():
                base_port += 1

            port_map[service] = base_port

        return port_map
```

## 2. Dependency Graph Visualization

```python
# backend/app/engine/graph.py

class DependencyGraph:
    """Build and visualize service dependency graphs."""

    def __init__(self, config: EnvironmentConfig):
        self.config = config
        self.adjacency: Dict[str, List[str]] = {}
        self._build_graph()

    def _build_graph(self):
        """Build adjacency list from service dependencies."""
        for name, service in self.config.spec.services.items():
            self.adjacency[name] = list(service.dependsOn.keys())

    def topological_sort(self) -> List[str]:
        """Determine correct startup order."""
        visited = set()
        order = []

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            for dep in self.adjacency.get(node, []):
                dfs(dep)
            order.append(node)

        for service in self.adjacency:
            dfs(service)

        return order

    def get_dependency_tree(self) -> Dict:
        """Get tree structure for visualization."""
        tree = {}
        for name, deps in self.adjacency.items():
            tree[name] = {
                "dependencies": deps,
                "dependents": [
                    s for s, d in self.adjacency.items() if name in d
                ],
            }
        return tree

    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for dep in self.adjacency.get(node, []):
                if dep not in visited:
                    dfs(dep, path)
                elif dep in rec_stack:
                    cycle_start = path.index(dep)
                    cycles.append(path[cycle_start:] + [dep])

            path.pop()
            rec_stack.remove(node)

        for service in self.adjacency:
            if service not in visited:
                dfs(service, [])

        return cycles
```

## 3. Smart Port Allocation

```python
# backend/app/engine/port_allocator.py

class PortAllocator:
    """Automatically assign ports to avoid conflicts."""

    COMMON_PORTS = {
        "node": [3000, 3001, 8080],
        "python": [8000, 8080, 5000],
        "postgres": [5432],
        "mysql": [3306],
        "mongodb": [27017],
        "redis": [6379],
        "elasticsearch": [9200],
        "rabbitmq": [5672, 15672],
        "kafka": [9092],
        "nginx": [80, 443],
        "grafana": [3000],
        "prometheus": [9090],
    }

    def __init__(self):
        self.allocated: Dict[int, str] = {}

    def allocate(self, service_name: str, preferred_port: Optional[int] = None) -> int:
        """Find an available port for a service."""
        if preferred_port:
            if self._is_available(preferred_port):
                self.allocated[preferred_port] = service_name
                return preferred_port
            # Find next available in range
            for offset in range(1, 10):
                candidate = preferred_port + offset
                if self._is_available(candidate):
                    self.allocated[candidate] = service_name
                    return candidate

        # Use common ports for service type
        common = self.COMMON_PORTS.get(service_name, [8000])
        for port in common:
            if self._is_available(port):
                self.allocated[port] = service_name
                return port

        # Fallback to ephemeral range
        for port in range(49152, 65535):
            if self._is_available(port):
                self.allocated[port] = service_name
                return port

        raise NoPortAvailableError(service_name)

    def _is_available(self, port: int) -> bool:
        """Check if port is available on the system."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return True
            except OSError:
                return False

    def release(self, port: int):
        """Release an allocated port."""
        self.allocated.pop(port, None)

    def get_allocation_map(self) -> Dict[str, int]:
        """Get service -> port mapping."""
        return {service: port for port, service in self.allocated.items()}
```

## 4. Environment Snapshots

```python
# backend/app/engine/snapshot.py

class SnapshotManager:
    """Save and restore entire environment state."""

    async def create_snapshot(self, env_id: str) -> Dict:
        """Save current environment state."""
        env = self.environments[env_id]

        snapshot = {
            "id": f"snapshot_{datetime.now().isoformat()}",
            "environmentId": env_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "config": env["config"].model_dump(),
            "services": {},
        }

        # Save container states
        for name, service in env["services"].items():
            if service.get("container_id"):
                # Export container configuration
                inspect_result = await run_command([
                    "docker", "inspect", service["container_id"]
                ])
                if inspect_result["code"] == 0:
                    snapshot["services"][name] = {
                        "containerConfig": json.loads(inspect_result["stdout"])[0],
                        "state": service["state"],
                    }

        # Save volume data (optional, for named volumes)
        for vol_name in env["config"].spec.volumes:
            # Create volume backup
            pass

        return snapshot

    async def restore_snapshot(self, snapshot: Dict) -> str:
        """Restore environment from snapshot."""
        config = EnvironmentConfig(**snapshot["config"])
        env_id = await self.create_environment(config)

        # Restore services in dependency order
        for name, service_state in snapshot["services"].items():
            await self.start_service(env_id, name)

        return env_id
```

## 5. Live Log Aggregation

```python
# backend/app/engine/log_aggregator.py

class LogAggregator:
    """Aggregate logs from multiple services into unified view."""

    def __init__(self):
        self.log_buffers: Dict[str, deque] = {}
        self.subscribers: List[WebSocket] = []
        self.streaming = False

    async def start_streaming(self, env_id: str, services: List[str]):
        """Start streaming logs from all services."""
        self.streaming = True

        for service_name in services:
            container_name = f"envman_{service_name}"
            asyncio.create_task(
                self._stream_service_logs(service_name, container_name)
            )

    async def _stream_service_logs(self, service_name: str, container_name: str):
        """Stream logs from a single service."""
        import subprocess

        cmd = [
            "docker", "logs",
            "--follow",
            "--tail", "100",
            "--timestamps",
            container_name,
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        while self.streaming:
            # Read stdout
            line = await process.stdout.readline()
            if line:
                log_line = {
                    "service": service_name,
                    "stream": "stdout",
                    "line": line.decode().strip(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await self._broadcast_log(log_line)

            # Read stderr
            line = await process.stderr.readline()
            if line:
                log_line = {
                    "service": service_name,
                    "stream": "stderr",
                    "line": line.decode().strip(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await self._broadcast_log(log_line)

    async def _broadcast_log(self, log_line: Dict):
        """Send log line to all subscribers."""
        message = json.dumps({"type": "log_line", "data": log_line})

        dead = []
        for ws in self.subscribers:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.subscribers.remove(ws)

    def get_logs(self, service_name: str, tail: int = 100) -> List[Dict]:
        """Get recent logs from buffer."""
        buffer = self.log_buffers.get(service_name, deque())
        return list(buffer)[-tail:]
```

## 6. Resource Monitoring

```python
# backend/app/engine/monitor.py

class ResourceMonitor:
    """Monitor CPU, memory, network usage per service."""

    async def get_service_stats(self, container_name: str) -> Dict:
        """Get resource usage for a container."""
        result = await run_command([
            "docker", "stats",
            container_name,
            "--no-stream",
            "--format",
            "{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}"
        ])

        if result["code"] != 0:
            return {"error": result["stderr"]}

        parts = result["stdout"].split("|")
        return {
            "cpu_percent": parts[0] if len(parts) > 0 else "N/A",
            "memory_usage": parts[1] if len(parts) > 1 else "N/A",
            "memory_percent": parts[2] if len(parts) > 2 else "N/A",
            "network_io": parts[3] if len(parts) > 3 else "N/A",
            "block_io": parts[4] if len(parts) > 4 else "N/A",
        }

    async def get_environment_stats(self, env_id: str) -> Dict:
        """Get resource usage for all services."""
        env = self.environments[env_id]
        stats = {}

        for name in env["config"].spec.services:
            container_name = f"envman_{name}"
            stats[name] = await self.get_service_stats(container_name)

        return {
            "environmentId": env_id,
            "services": stats,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
```

## 7. One-Click Templates

```python
# backend/app/registry/templates.py

TEMPLATES = {
    "mern": {
        "id": "mern",
        "name": "MERN Stack",
        "description": "MongoDB, Express, React, Node.js",
        "category": "fullstack",
        "services": {
            "node": {
                "type": "runtime",
                "image": "node:20-alpine",
                "ports": ["3000:3000"],
                "volumes": ["./src:/app/src"],
                "env": {"NODE_ENV": "development"},
                "dependsOn": {"mongo": {"condition": "service_healthy"}},
            },
            "mongo": {
                "type": "database",
                "engine": "mongodb",
                "image": "mongo:7",
                "ports": ["27017:27017"],
                "volumes": ["mongo_data:/data/db"],
                "env": {
                    "MONGO_INITDB_ROOT_USERNAME": "admin",
                    "MONGO_INITDB_ROOT_PASSWORD": "password",
                },
            },
            "redis": {
                "type": "cache",
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
                "volumes": ["redis_data:/data"],
            },
        },
        "volumes": {"mongo_data": {}, "redis_data": {}},
        "networks": {"default": {"driver": "bridge"}},
    },
    "python-web": {
        "id": "python-web",
        "name": "Python Web App",
        "description": "FastAPI/Django with Postgres and Redis",
        "category": "backend",
        "services": {
            "python": {
                "type": "runtime",
                "image": "python:3.12-slim",
                "ports": ["8000:8000"],
                "volumes": ["./src:/app/src"],
                "command": ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"],
                "dependsOn": {
                    "postgres": {"condition": "service_healthy"},
                    "redis": {"condition": "service_started"},
                },
            },
            "postgres": {
                "type": "database",
                "image": "postgres:16",
                "ports": ["5432:5432"],
                "volumes": ["pg_data:/var/lib/postgresql/data"],
                "env": {
                    "POSTGRES_USER": "postgres",
                    "POSTGRES_PASSWORD": "postgres",
                    "POSTGRES_DB": "app",
                },
            },
            "redis": {
                "type": "cache",
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
                "volumes": ["redis_data:/data"],
            },
        },
    },
    "java-spring": {
        "id": "java-spring",
        "name": "Java Spring Boot",
        "description": "Spring Boot with MySQL and RabbitMQ",
        "category": "backend",
        "services": {
            "java": {
                "type": "runtime",
                "image": "eclipse-temurin:21-jdk-jammy",
                "ports": ["8080:8080"],
                "volumes": ["./:/app"],
                "command": ["./gradlew", "bootRun"],
                "dependsOn": {
                    "mysql": {"condition": "service_healthy"},
                    "rabbitmq": {"condition": "service_started"},
                },
            },
            "mysql": {
                "type": "database",
                "image": "mysql:8.4",
                "ports": ["3306:3306"],
                "volumes": ["mysql_data:/var/lib/mysql"],
                "env": {
                    "MYSQL_ROOT_PASSWORD": "root",
                    "MYSQL_DATABASE": "app",
                },
            },
            "rabbitmq": {
                "type": "message_broker",
                "image": "rabbitmq:3.13-management",
                "ports": ["5672:5672", "15672:15672"],
                "volumes": ["rabbitmq_data:/var/lib/rabbitmq"],
            },
        },
    },
    "data-science": {
        "id": "data-science",
        "name": "Data Science",
        "description": "Python with Jupyter, Postgres, and MinIO",
        "category": "data",
        "services": {
            "python": {
                "type": "runtime",
                "image": "python:3.12-slim",
                "ports": ["8888:8888"],
                "volumes": ["./notebooks:/notebooks", "./data:/data"],
                "command": ["jupyter", "notebook", "--ip=0.0.0.0", "--allow-root"],
                "dependsOn": {"postgres": {"condition": "service_started"}},
            },
            "postgres": {
                "type": "database",
                "image": "postgres:16",
                "ports": ["5432:5432"],
                "volumes": ["pg_data:/var/lib/postgresql/data"],
            },
            "minio": {
                "type": "storage",
                "image": "minio/minio:latest",
                "ports": ["9000:9000", "9001:9001"],
                "volumes": ["minio_data:/data"],
                "command": ["server", "/data", "--console-address", ":9001"],
            },
        },
    },
    "microservices": {
        "id": "microservices",
        "name": "Microservices",
        "description": "Node.js microservices with Redis and RabbitMQ",
        "category": "architecture",
        "services": {
            "api-gateway": {
                "type": "proxy",
                "image": "nginx:1.27-alpine",
                "ports": ["80:80"],
                "volumes": ["./nginx.conf:/etc/nginx/conf.d/default.conf"],
                "dependsOn": {"user-service": {"condition": "service_started"}},
            },
            "user-service": {
                "type": "runtime",
                "image": "node:20-alpine",
                "ports": ["3001:3000"],
                "volumes": ["./services/user:/app"],
                "env": {"SERVICE_NAME": "user-service", "REDIS_URL": "redis://redis:6379"},
                "dependsOn": {"redis": {"condition": "service_started"}},
            },
            "order-service": {
                "type": "runtime",
                "image": "node:20-alpine",
                "ports": ["3002:3000"],
                "volumes": ["./services/order:/app"],
                "env": {
                    "SERVICE_NAME": "order-service",
                    "REDIS_URL": "redis://redis:6379",
                    "RABBITMQ_URL": "amqp://rabbitmq:5672",
                },
                "dependsOn": {
                    "redis": {"condition": "service_started"},
                    "rabbitmq": {"condition": "service_started"},
                },
            },
            "redis": {
                "type": "cache",
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
            },
            "rabbitmq": {
                "type": "message_broker",
                "image": "rabbitmq:3.13-management",
                "ports": ["5672:5672", "15672:15672"],
            },
        },
    },
}
```

---

# Summary: Key Technical Decisions

## Architecture Principles

1. **Plugin-based verification** - Easy to add new service types without modifying core
2. **Declarative config** - YAML/JSON config that describes desired state
3. **Event-driven updates** - WebSocket for real-time progress
4. **Docker-native** - Use Docker's networking, volumes, and health checks
5. **Type-safe models** - Pydantic for validation, TypeScript for frontend

## Competitive Advantages over Existing Tools

| Feature | Docker Compose | Devbox | Dev Containers | EnvMan |
|---------|---------------|--------|----------------|--------|
| GUI | ❌ CLI only | ❌ CLI only | ⚠️ VS Code only | ✅ Standalone GUI |
| Service Registry | ❌ Manual | ❌ Limited | ❌ Manual | ✅ 25+ services |
| Health Verification | ⚠️ Basic | ❌ None | ❌ None | ✅ Deep checks |
| Port Auto-assign | ❌ Manual | ❌ N/A | ❌ Manual | ✅ Smart allocation |
| Templates | ❌ Manual | ❌ Limited | ✅ Templates | ✅ One-click |
| AI Config Gen | ❌ | ❌ | ❌ | ✅ Natural language |
| Snapshots | ❌ | ❌ | ❌ | ✅ Save/restore |
| Log Aggregation | ⚠️ Basic | ❌ | ❌ | ✅ Unified view |
| Resource Monitoring | ❌ | ❌ | ❌ | ✅ Per-service |

## Success Metrics

- **Setup time**: < 60 seconds for full environment
- **Verification accuracy**: 100% (if EnvMan says it works, it works)
- **Service support**: 25+ services in Phase 1
- **Config generation**: < 5 seconds from natural language
- **Log latency**: < 100ms from service to UI
- **UI responsiveness**: < 16ms frame time (60fps)

---

*This specification provides the complete technical blueprint for transforming EnvMan from a simple Docker GUI wrapper into a category-defining developer environment platform.*
