# Suggested Blueprints (starter stacks users want; map to EnvMan templates)
Sources: DDEV web focus (https://ddev.readthedocs.io/en/stable/); Dev Containers quickstarts Node/Python (https://code.visualstudio.com/docs/devcontainers/containers); Codespaces prebuild-worthy stacks (https://docs.github.com/en/codespaces); EnvMan existing mern/python-web.

1. **mern** (have): node:20 + mongo:7 + redis:7 — add health: redis PING, mongo `mongosh --eval db.runCommand({ping:1})`.
2. **python-web** (have): python:3.12 + postgres:16 + redis:7 — pg_isready gate (https://docs.docker.com/compose/how-tos/startup-order/).
3. **laravel/mysql** (ask): php:8.3 + mysql:8 + redis — mysqladmin ping; MYSQL_ALLOW_EMPTY_PASSWORD dev-only flag.
4. **kafka-streaming**: apache/kafka KRaft + kafdrop/ui — broker-api-versions gate, 60s start_period.
5. **elastic-search**: elasticsearch:9 single-node (`discovery.type=single-node`, 1-4GB) + kibana — curl TLS gate (https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic).
6. **pg-vector-ai**: postgres:16-pgvector + redis + python worker — pg_isready + extension `CREATE EXTENSION vector`.
7. **next-supabase**: node + postgres + postgrest/gotrue/studio (Supabase 17-min provision anecdote https://orbstack.dev/ — prebuild this).
Each blueprint: compose + devcontainer.json + seed data + one-click Verify (service_healthy chain).
