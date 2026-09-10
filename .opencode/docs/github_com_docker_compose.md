# GitHub - docker/compose: Define and run multi-container applications with Docker · GitHub

> Source: https://github.com/docker/compose
> Cached: 2026-09-10T08:35:21.635Z

---

# Table of Contents

[](#table-of-contents)

- [Docker Compose](#docker-compose)

[Where to get Docker Compose](#where-to-get-docker-compose)

- [Windows and macOS](#windows-and-macos)

- [Linux](#linux)

- [Quick Start](#quick-start)

- [Contributing](#contributing)

- [Legacy](#legacy)

# Docker Compose

[](#docker-compose)
[](https://github.com/docker/compose/releases/latest)
[](https://pkg.go.dev/github.com/docker/compose/v5)
[](https://github.com/docker/compose/actions?query=workflow%3Aci)
[](https://codecov.io/gh/docker/compose)
[](https://api.securityscorecards.dev/projects/github.com/docker/compose)
[](/docker/compose/blob/main/logo.png?raw=true)
Docker Compose is a tool for running multi-container applications on Docker
defined using the [Compose file format](https://compose-spec.io).
A Compose file is used to define how one or more containers that make up
your application are configured.
Once you have a Compose file, you can create and start your application with a
single command: `docker compose up`.
> 
**Note**: About Docker Swarm
Docker Swarm used to rely on the legacy compose file format but did not adopt the compose specification
so is missing some of the recent enhancements in the compose syntax. After
[acquisition by Mirantis](https://www.mirantis.com/software/swarm/) swarm isn't maintained by Docker Inc, and
as such some Docker Compose features aren't accessible to swarm users.

# Where to get Docker Compose

[](#where-to-get-docker-compose)
### Windows and macOS

[](#windows-and-macos)
Docker Compose is included in
[Docker Desktop](https://www.docker.com/products/docker-desktop/)
for Windows and macOS.
### Linux

[](#linux)
You can download Docker Compose binaries from the
[release page](https://github.com/docker/compose/releases) on this repository.
Rename the relevant binary for your OS to `docker-compose` and copy it to `$HOME/.docker/cli-plugins`

Or copy it into one of these folders to install it system-wide:

- `/usr/local/lib/docker/cli-plugins` OR `/usr/local/libexec/docker/cli-plugins`

- `/usr/lib/docker/cli-plugins` OR `/usr/libexec/docker/cli-plugins`

(might require making the downloaded file executable with `chmod +x`)

## Quick Start

[](#quick-start)
Using Docker Compose is a three-step process:

Define your app's environment with a `Dockerfile` so it can be
reproduced anywhere.
Define the services that make up your app in `compose.yaml` so
they can be run together in an isolated environment.
Lastly, run `docker compose up` and Compose will start and run your entire
app.

A Compose file looks like this:

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/code
  redis:
    image: redis
## Contributing

[](#contributing)
Want to help develop Docker Compose? Check out our
[contributing documentation](/docker/compose/blob/main/CONTRIBUTING.md).
If you find an issue, please report it on the
[issue tracker](https://github.com/docker/compose/issues/new/choose).
## Legacy

[](#legacy)
The Python version of Compose is available under the `v1` [branch](https://github.com/docker/compose/tree/v1).