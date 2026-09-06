# mysql - Official Image | Docker Hub

> Source: https://hub.docker.com/_/mysql
> Cached: 2026-09-06T08:00:59.045Z

---

[](/)Search Docker Hub

K- Help
- System theme
- Docker Suite
Go back
- Help
- System theme
- Docker Suite

[Sign in](/login)[Sign up](https://app.docker.com/signup)
- [Explore](/search)
- /
- [Official Images](/search?badges=official)
- /
mysql

## mysql

Docker Official Image•1B+

•**10K+**MySQL is a widely used, open-source relational database management system (RDBMS).

[Databases & storage](/categories/databases-and-storage)[Overview](/_/mysql)[Tags](/_/mysql/tags)# mysql Docker official image overview

### [⁠](#quick-reference)Quick reference

**Maintained by**:

[the Docker Community and the MySQL Team⁠](https://github.com/docker-library/mysql)

**Where to get help**:

[the Docker Community Slack⁠](https://dockr.ly/comm-slack), [Server Fault⁠](https://serverfault.com/help/on-topic), [Unix & Linux⁠](https://unix.stackexchange.com/help/on-topic), or [Stack Overflow⁠](https://stackoverflow.com/help/on-topic)

### [⁠](#supported-tags-and-respective-dockerfile-links)Supported tags and respective `Dockerfile` links

[`26.7.0`, `26.7`, `26`, `innovation`, `latest`, `26.7.0-oraclelinux9`, `26.7-oraclelinux9`, `26-oraclelinux9`, `innovation-oraclelinux9`, `oraclelinux9`, `26.7.0-oracle`, `26.7-oracle`, `26-oracle`, `innovation-oracle`, `oracle`⁠](https://github.com/docker-library/mysql/blob/288e46ff450920468d5a1fcb618d359068704c3d/innovation/Dockerfile.oracle)

[`9.7.2`, `9.7`, `9`, `lts`, `9.7.2-oraclelinux9`, `9.7-oraclelinux9`, `9-oraclelinux9`, `lts-oraclelinux9`, `9.7.2-oracle`, `9.7-oracle`, `9-oracle`, `lts-oracle`⁠](https://github.com/docker-library/mysql/blob/55e1d05e12ac954be18a3114d7c177ad957e435b/9.7/Dockerfile.oracle)

[`8.4.11`, `8.4`, `8`, `8.4.11-oraclelinux9`, `8.4-oraclelinux9`, `8-oraclelinux9`, `8.4.11-oracle`, `8.4-oracle`, `8-oracle`⁠](https://github.com/docker-library/mysql/blob/01f90d87012e46cd174073bba02d64e9fc693ed3/8.4/Dockerfile.oracle)

### [⁠](#quick-reference-cont)Quick reference (cont.)

**Where to file issues**:

[https://github.com/docker-library/mysql/issues⁠](https://github.com/docker-library/mysql/issues?q=is:issue+is:pr)

**Supported architectures**: ([more info⁠](https://github.com/docker-library/official-images#architectures-other-than-amd64))

[`amd64`⁠](https://hub.docker.com/r/amd64/mysql/), [`arm64v8`⁠](https://hub.docker.com/r/arm64v8/mysql/)

**Published image artifact details**:

[repo-info repo&#x27;s `repos/mysql/` directory⁠](https://github.com/docker-library/repo-info/blob/master/repos/mysql) ([history⁠](https://github.com/docker-library/repo-info/commits/master/repos/mysql))

(image metadata, transfer size, etc)

**Image updates**:

[official-images repo&#x27;s `library/mysql` label⁠](https://github.com/docker-library/official-images/issues?q=label%3Alibrary%2Fmysql)

[official-images repo&#x27;s `library/mysql` file⁠](https://github.com/docker-library/official-images/blob/master/library/mysql) ([history⁠](https://github.com/docker-library/official-images/commits/master/library/mysql))

**Source of this description**:

[docs repo&#x27;s `mysql/` directory⁠](https://github.com/docker-library/docs/tree/master/mysql) ([history⁠](https://github.com/docker-library/docs/commits/master/mysql))

### [⁠](#what-is-mysql)What is MySQL?

MySQL is the world&#x27;s most popular open source database. With its proven performance, reliability and ease-of-use, MySQL has become the leading database choice for web-based applications, covering the entire range from personal projects and websites, via e-commerce and information services, all the way to high profile web properties including Facebook, Twitter, YouTube, Yahoo! and many more.

For more information and related downloads for MySQL Server and other MySQL products, please visit [www.mysql.com⁠](http://www.mysql.com).

### [⁠](#how-to-use-this-image)How to use this image

#### [⁠](#start-a-mysql-server-instance)Start a `mysql` server instance

Starting a MySQL instance is simple:

```
$ docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:tag

```

Copy
... where `some-mysql` is the name you want to assign to your container, `my-secret-pw` is the password to be set for the MySQL root user and `tag` is the tag specifying the MySQL version you want. See the list above for relevant tags.

#### [⁠](#connect-to-mysql-from-the-mysql-command-line-client)Connect to MySQL from the MySQL command line client

The following command starts another `mysql` container instance and runs the `mysql` command line client against your original `mysql` container, allowing you to execute SQL statements against your database instance:

```
$ docker run -it --network some-network --rm mysql mysql -hsome-mysql -uexample-user -p

```

Copy
... where `some-mysql` is the name of your original `mysql` container (connected to the `some-network` Docker network).

This image can also be used as a client for non-Docker or remote instances:

```
$ docker run -it --rm mysql mysql -hsome.mysql.host -usome-mysql-user -p

```

Copy
More information about the MySQL command line client can be found in the [MySQL documentation⁠](http://dev.mysql.com/doc/en/mysql.html)

#### [⁠](#-via-docker-compose)... via [`docker compose`⁠](https://github.com/docker/compose)

Example `compose.yaml` for `mysql`:

```
# Use root/example as user/password credentials

services:

  db:
    image: mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: example
    # (this is just an example, not intended to be a production configuration)

```

Copy
Run `docker compose up`, wait for it to initialize completely, and visit `http://localhost:8080` or `http://host-ip:8080` (as appropriate).

#### [⁠](#container-shell-access-and-viewing-mysql-logs)Container shell access and viewing MySQL logs

The `docker exec` command allows you to run commands inside a Docker container. The following command line will give you a bash shell inside your `mysql` container:

```
$ docker exec -it some-mysql bash

```

Copy
The log is available through Docker&#x27;s container log:

```
$ docker logs some-mysql

```

Copy
#### [⁠](#using-a-custom-mysql-configuration-file)Using a custom MySQL configuration file

The default configuration for MySQL varies depending on the base image:

**Oracle-based images (default):** The default configuration is located at `/etc/my.cnf`, which may `!includedir` additional directories such as `/etc/mysql/conf.d`.

**Debian-based MySQL 8 images:** The default configuration can be found in `/etc/mysql/my.cnf`, which may `!includedir` additional directories such as `/etc/mysql/conf.d`.

Please inspect the relevant files and directories within the `mysql` image itself for more details.

If `/my/custom/config-file.cnf` is the path and name of your custom configuration file, you can start your `mysql` container like this (note that only the directory path of the custom config file is used in this command):

```
$ docker run --name some-mysql -v /my/custom:/etc/mysql/conf.d -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:tag

```

Copy
This will start a new container `some-mysql` where the MySQL instance uses the combined startup settings from the default configuration file and `/etc/mysql/conf.d/config-file.cnf`, with settings from the latter taking precedence.

##### [⁠](#configuration-without-a-cnf-file)Configuration without a `cnf` file

Many configuration options can be passed as flags to `mysqld`. This will give you the flexibility to customize the container without needing a `cnf` file. For example, if you want to change the default encoding and collation for all tables to use UTF-8 (`utf8mb4`) just run the following:

```
$ docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:tag --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

```

Copy
If you would like to see a complete list of available options, just run:

```
$ docker run -it --rm mysql:tag --verbose --help

```

Copy
#### [⁠](#environment-variables)Environment Variables

When you start the `mysql` image, you can adjust the configuration of the MySQL instance by passing one or more environment variables on the `docker run` command line. Do note that none of the variables below will have any effect if you start the container with a data directory that already contains a database: any pre-existing database will always be left untouched on container startup.

See also [https://dev.mysql.com/doc/refman/5.7/en/environment-variables.html⁠](https://dev.mysql.com/doc/refman/5.7/en/environment-variables.html) for documentation of environment variables which MySQL itself respects (especially variables like `MYSQL_HOST`, which is known to cause issues when used with this image).

##### [⁠](#mysql_root_password)`MYSQL_ROOT_PASSWORD`

This variable is mandatory and specifies the password that will be set for the MySQL `root` superuser account. In the above example, it was set to `my-secret-pw`.

##### [⁠](#mysql_database)`MYSQL_DATABASE`

This variable is optional and allows you to specify the name of a database to be created on image startup. If a user/password was supplied (see below) then that user will be granted superuser access ([corresponding to `GRANT ALL`⁠](https://dev.mysql.com/doc/refman/en/creating-accounts.html)) to this database.

##### [⁠](#mysql_user-mysql_password)`MYSQL_USER`, `MYSQL_PASSWORD`

These variables are optional, used in conjunction to create a new user and to set that user&#x27;s password. This user will be granted superuser permissions (see above) for the database specified by the `MYSQL_DATABASE` variable. Both variables are required for a user to be created.

Do note that there is no need to use this mechanism to create the root superuser, that user gets created by default with the password specified by the `MYSQL_ROOT_PASSWORD` variable.

##### [⁠](#mysql_allow_empty_password)`MYSQL_ALLOW_EMPTY_PASSWORD`

This is an optional variable. Set to a non-empty value, like `yes`, to allow the container to be started with a blank password for the root user. *NOTE*: Setting this variable to `yes` is not recommended unless you really know what you are doing, since this will leave your MySQL instance completely unprotected, allowing anyone to gain complete superuser access.

##### [⁠](#mysql_random_root_password)`MYSQL_RANDOM_ROOT_PASSWORD`

This is an optional variable. Set to a non-empty value, like `yes`, to generate a random initial password for the root user (using `openssl`). The generated root password will be printed to stdout (`GENERATED ROOT PASSWORD: .....`).

##### [⁠](#mysql_onetime_password)`MYSQL_ONETIME_PASSWORD`

Sets root (*not* the user specified in `MYSQL_USER`!) user as expired once init is complete, forcing a password change on first login. Any non-empty value will activate this setting. *NOTE*: This feature is supported on MySQL 5.6+ only. Using this option on MySQL 5.5 will throw an appropriate error during initialization.

##### [⁠](#mysql_initdb_skip_tzinfo)`MYSQL_INITDB_SKIP_TZINFO`

By default, the entrypoint script automatically loads the timezone data needed for the `CONVERT_TZ()` function. If it is not needed, any non-empty value disables timezone loading.

#### [⁠](#docker-secrets)Docker Secrets

As an alternative to passing sensitive information via environment variables, `_FILE` may be appended to the previously listed environment variables, causing the initialization script to load the values for those variables from files present in the container. In particular, this can be used to load passwords from Docker secrets stored in `/run/secrets/<secret_name>` files. For example:

```
$ docker run --name some-mysql -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/mysql-root -d mysql:tag

```

Copy
Currently, this is only supported for `MYSQL_ROOT_PASSWORD`, `MYSQL_ROOT_HOST`, `MYSQL_DATABASE`, `MYSQL_USER`, and `MYSQL_PASSWORD`.

### [⁠](#initializing-a-fresh-instance)Initializing a fresh instance

When a container is started for the first time, a new database with the specified name will be created and initialized with the provided configuration variables. Furthermore, it will execute files with extensions `.sh`, `.sql`, `.sql.gz`, `.sql.bz2`, `.sql.xz`, and `.sql.zst` that are found in `/docker-entrypoint-initdb.d`. Files will be executed in alphabetical order. When parsing `.sh` files without the execute bit set, they are `source`d rather than executed.

You can easily populate your `mysql` services by [mounting a SQL dump into that directory⁠](https://docs.docker.com/storage/bind-mounts/) and provide [custom images⁠](https://docs.docker.com/reference/dockerfile/) with contributed data. SQL files will be imported by default to the database specified by the `MYSQL_DATABASE` variable.

### [⁠](#caveats)Caveats

#### [⁠](#where-to-store-data)Where to Store Data

Important note: There are several ways to store data used by applications that run in Docker containers. We encourage users of the `mysql` images to familiarize themselves with the options available, including:

- Let Docker manage the storage of your database data [by writing the database files to disk on the host system using its own internal volume management⁠](https://docs.docker.com/storage/volumes/). This is the default and is easy and fairly transparent to the user. The downside is that the files may be hard to locate for tools and applications that run directly on the host system, i.e. outside containers.

- Create a data directory on the host system (outside the container) and [mount this to a directory visible from inside the container⁠](https://docs.docker.com/storage/bind-mounts/). This places the database files in a known location on the host system, and makes it easy for tools and applications on the host system to access the files. The downside is that the user needs to make sure that the directory exists, and that e.g. directory permissions and other security mechanisms on the host system are set up correctly.

The Docker documentation is a good starting point for understanding the different storage options and variations, and there are multiple blogs and forum postings that discuss and give advice in this area. We will simply show the basic procedure here for the latter option above:

Create a data directory on a suitable volume on your host system, e.g. `/my/own/datadir`.

Start your `mysql` container like this:

```
$ docker run --name some-mysql -v /my/own/datadir:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:tag

```

Copy

The `-v /my/own/datadir:/var/lib/mysql` part of the command mounts the `/my/own/datadir` directory from the underlying host system as `/var/lib/mysql` inside the container, where MySQL by default will write its data files.

#### [⁠](#no-connections-until-mysql-init-completes)No connections until MySQL init completes

If there is no database initialized when the container starts, then a default database will be created. While this is the expected behavior, this means that it will not accept incoming connections 

... [Content truncated]