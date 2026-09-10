# Control startup and shutdown order in Compose | Docker Docs

> Source: https://docs.docker.com/compose/how-tos/startup-order/
> Cached: 2026-09-10T08:35:00.646Z

---

Home
/
Manuals
/
Docker Compose
/
How-tos
/
Control startup order# Control startup and shutdown order in Compose

Ask Gordon

Copy Markdown

View MarkdownTable of contents
- Control startup
- Example
- Reference information

You can control the order of service startup and shutdown with the
depends_on attribute. Compose always starts and stops
containers in dependency order, where dependencies are determined by
`depends_on`, `links`, `volumes_from`, and `network_mode: "service:..."`.For example, if your application needs to access a database and both services are started with `docker compose up`, there is a chance this will fail since the application service might start before the database service and won't find a database able to handle its SQL statements.

## Control startup

On startup, Compose does not wait until a container is "ready", only until it's running. This can cause issues if, for example, you have a relational database system that needs to start its own services before being able to handle incoming connections.

The solution for detecting the ready state of a service is to use the `condition` attribute with one of the following options:

- `service_started`
- `service_healthy`. This specifies that a dependency is expected to be “healthy”, which is defined with `healthcheck`, before starting a dependent service.
- `service_completed_successfully`. This specifies that a dependency is expected to run to successful completion before starting a dependent service.

## Example

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
services:
  web:
    build: .
    depends_on:
      db:
        condition: service_healthy
        restart: true
      redis:
        condition: service_started
  redis:
    image: redis
  db:
    image: postgres:18
    healthcheck:
      test: [&#34;CMD-SHELL&#34;, &#34;pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}&#34;]
      interval: 10s
      retries: 5
      start_period: 30s
      timeout: 10s
```

Compose creates services in dependency order. `db` and `redis` are created before `web`.

Compose waits for healthchecks to pass on dependencies marked with `service_healthy`. `db` is expected to be "healthy" (as indicated by `healthcheck`) before `web` is created.

`restart: true` ensures that if `db` is updated or restarted due to an explicit Compose operation, for example `docker compose restart`, the `web` service is also restarted automatically, ensuring it re-establishes connections or dependencies correctly.

The healthcheck for the `db` service uses the `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}` command to check if the PostgreSQL database is ready. The service is retried every 10 seconds, up to 5 times.

Compose also removes services in dependency order. `web` is removed before `db` and `redis`.

## Reference information

- `depends_on`
- `healthcheck`