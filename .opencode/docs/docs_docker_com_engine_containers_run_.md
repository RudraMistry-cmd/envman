# Running containers | Docker Docs

> Source: https://docs.docker.com/engine/containers/run/
> Cached: 2026-09-10T08:35:11.707Z

---

Home
/
Manuals
/
Docker Engine
/
Containers
/
Running containers# Running containers

Ask Gordon

Copy Markdown

View MarkdownTable of contents
- General form

- Image references

- Options
- Commands and arguments

- Foreground and background
- Container identification
- Container networking
- Filesystem mounts

- Volume mounts
- Bind mounts

- Exit status

- 125
- 126
- 127
- Other exit codes

- Runtime constraints on resources

- User memory constraints
- Swappiness constraint
- CPU share constraint
- CPU period constraint
- Cpuset constraint
- CPU quota constraint
- Block IO bandwidth (Blkio) constraint

- Additional groups
- Runtime privilege and Linux capabilities
- Overriding image defaults

- Default command and options
- Default entrypoint
- Exposed ports
- Environment variables
- Healthchecks
- User
- Working directory

Docker runs processes in isolated containers. A container is a process
which runs on a host. The host may be local or remote. When you
execute `docker run`, the container process that runs is isolated in
that it has its own file system, its own networking, and its own
isolated process tree separate from the host.This page details how to use the `docker run` command to run containers.

## General form

A `docker run` command takes the following form:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run [OPTIONS] IMAGE[:TAG|@DIGEST] [COMMAND] [ARG...]

```

The `docker run` command must specify an image reference
to create the container from.### Image references

The image reference is the name and version of the image. You can use the image
reference to create or run a container based on an image.
- `docker run IMAGE[:TAG][@DIGEST]`
- `docker create IMAGE[:TAG][@DIGEST]`

An image tag is the image version, which defaults to `latest` when omitted. Use
the tag to run a container from specific version of an image. For example, to
run version `24.04` of the `ubuntu` image: `docker run ubuntu:24.04`.#### Image digests

Images using the v2 or later image format have a content-addressable identifier
called a digest. As long as the input used to generate the image is unchanged,
the digest value is predictable.The following example runs a container from the `alpine` image with the
`sha256:9cacb71397b640eca97488cf08582ae4e4068513101088e9f96c9814bfda95e0` digest:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run alpine@sha256:9cacb71397b640eca97488cf08582ae4e4068513101088e9f96c9814bfda95e0 date

```

### Options

`[OPTIONS]` let you configure options for the container. For example, you can
give the container a name (`--name`), or run it as a background process (`-d`).
You can also set options to control things like resource constraints and
networking.### Commands and arguments

You can use the `[COMMAND]` and `[ARG...]` positional arguments to specify
commands and arguments for the container to run when it starts up. For example,
you can specify `sh` as the `[COMMAND]`, combined with the `-i` and `-t` flags,
to start an interactive shell in the container (if the image you select has an
`sh` executable on `PATH`).]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -it IMAGE sh

```

> 
NoteDepending on your Docker system configuration, you may be
required to preface the `docker run` command with `sudo`. To avoid
having to use `sudo` with the `docker` command, your system
administrator can create a Unix group called `docker` and add users to
it. For more information about this configuration, refer to the Docker
installation documentation for your operating system.

## Foreground and background

When you start a container, the container runs in the foreground by default.
If you want to run the container in the background instead, you can use the
`--detach` (or `-d`) flag. This starts the container without occupying your
terminal window.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -d <IMAGE>

```

While the container runs in the background, you can interact with the container
using other CLI commands. For example, `docker logs` lets you view the logs for
the container, and `docker attach` brings it to the foreground.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -d nginx
0246aa4d1448a401cabd2ce8f242192b6e7af721527e48a810463366c7ff54f1
$ docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS        PORTS     NAMES
0246aa4d1448   nginx     &#34;/docker-entrypoint.…&#34;   2 seconds ago   Up 1 second   80/tcp    pedantic_liskov
$ docker logs -n 5 0246aa4d1448
2023/11/06 15:58:23 [notice] 1#1: start worker process 33
2023/11/06 15:58:23 [notice] 1#1: start worker process 34
2023/11/06 15:58:23 [notice] 1#1: start worker process 35
2023/11/06 15:58:23 [notice] 1#1: start worker process 36
2023/11/06 15:58:23 [notice] 1#1: start worker process 37
$ docker attach 0246aa4d1448
^C
2023/11/06 15:58:40 [notice] 1#1: signal 2 (SIGINT) received, exiting
...

```

For more information about `docker run` flags related to foreground and
background modes, see:
- `docker run --detach`: run container in background
- `docker run --attach`: attach to `stdin`, `stdout`, and `stderr`
- `docker run --tty`: allocate a pseudo-tty
- `docker run --interactive`: keep `stdin` open even if not attached

For more information about re-attaching to a background container, see
`docker attach`.## Container identification

You can identify a container in three ways:

Identifier typeExample valueUUID long identifier`f78375b1c487e03c9438c729345e54db9d20cfa2ac1fc3494b6eb60872e74778`UUID short identifier`f78375b1c487`Name`evil_ptolemy`The UUID identifier is a random ID assigned to the container by the daemon.

The daemon generates a random string name for containers automatically. You can
also define a custom name using the `--name` flag.
Defining a `name` can be a handy way to add meaning to a container. If you
specify a `name`, you can use it when referring to the container in a
user-defined network. This works for both background and foreground Docker
containers.A container identifier is not the same thing as an image reference. The image
reference specifies which image to use when you run a container. You can't run
`docker exec nginx:alpine sh` to open a shell in a container based on the
`nginx:alpine` image, because `docker exec` expects a container identifier
(name or ID), not an image.While the image used by a container is not an identifier for the container, you
find out the IDs of containers using an image by using the `--filter` flag. For
example, the following `docker ps` command gets the IDs of all running
containers based on the `nginx:alpine` image:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker ps -q --filter ancestor=nginx:alpine

```

For more information about using filters, see
Filtering.## Container networking

Containers have networking enabled by default, and they can make outgoing
connections. If you're running multiple containers that need to communicate
with each other, you can create a custom network and attach the containers to
the network.When multiple containers are attached to the same custom network, they can
communicate with each other using the container names as a DNS hostname. The
following example creates a custom network named `my-net`, and runs two
containers that attach to the network.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker network create my-net
$ docker run -d --name web --network my-net nginx:alpine
$ docker run --rm -it --network my-net busybox
/ # ping web
PING web (172.18.0.2): 56 data bytes
64 bytes from 172.18.0.2: seq=0 ttl=64 time=0.326 ms
64 bytes from 172.18.0.2: seq=1 ttl=64 time=0.257 ms
64 bytes from 172.18.0.2: seq=2 ttl=64 time=0.281 ms
^C
--- web ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.257/0.288/0.326 ms

```

For more information about container networking, see Networking
overview## Filesystem mounts

By default, the data in a container is stored in an ephemeral, writable
container layer. Removing the container also removes its data. If you want to
use persistent data with containers, you can use filesystem mounts to store the
data persistently on the host system. Filesystem mounts can also let you share
data between containers and the host.Docker supports two main categories of mounts:

- Volume mounts
- Bind mounts

Volume mounts are great for persistently storing data for containers, and for
sharing data between containers. Bind mounts, on the other hand, are for
sharing data between a container and the host.You can add a filesystem mount to a container using the `--mount` flag for the
`docker run` command.The following sections show basic examples of how to create volumes and bind
mounts. For more in-depth examples and descriptions, refer to the section of
the storage section in the documentation.### Volume mounts

To create a volume mount:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run --mount source=<VOLUME_NAME>,target=[PATH] [IMAGE] [COMMAND...]

```

The `--mount` flag takes two parameters in this case: `source` and `target`.
The value for the `source` parameter is the name of the volume. The value of
`target` is the mount location of the volume inside the container. Once you've
created the volume, any data you write to the volume is persisted, even if you
stop or remove the container:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run --rm --mount source=my_volume,target=/foo busybox \
  echo &#34;hello, volume!&#34; > /foo/hello.txt
$ docker run --mount source=my_volume,target=/bar busybox
  cat /bar/hello.txt
hello, volume!

```

The `target` must always be an absolute path, such as `/src/docs`. An absolute
path starts with a `/` (forward slash). Volume names must start with an
alphanumeric character, followed by `a-z0-9`, `_` (underscore), `.` (period) or
`-` (hyphen).### Bind mounts

To create a bind mount:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -it --mount type=bind,source=[PATH],target=[PATH] busybox

```

In this case, the `--mount` flag takes three parameters. A type (`bind`), and
two paths. The `source` path is the location on the host that you want to
bind mount into the container. The `target` path is the mount destination
inside the container.By default, bind mounts require the source path to exist on the daemon host. If the
source path doesn't exist, an error is returned. To create the source path on
the daemon host if it doesn't exist, use the `bind-create-src` option:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -it --mount type=bind,source=[PATH],target=[PATH],bind-create-src busybox

```

Bind mounts are read-write by default, meaning that you can both read and write
files to and from the mounted location from the container. Changes that you
make, such as adding or editing files, are reflected on the host filesystem:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -it --mount type=bind,source=.,target=/foo busybox
/ # echo &#34;hello from container&#34; > /foo/hello.txt
/ # exit
$ cat hello.txt
hello from container

```

## Exit status

The exit code from `docker run` gives information about why the container
failed to run or why it exited. The following sections describe the meanings of
different container exit codes values.### 125

Exit code `125` indicates that the error is with Docker daemon itself.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run --foo busybox; echo $?

flag provided but not defined: --foo
See 'docker run --help'.
125

```

### 126

Exit code `126` indicates that the specified contained command can't be invoked.
The container command in the following example is: `/etc`.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run busybox /etc; echo $?

docker: Error response from daemon: Container command '/etc' could not be invoked.
126

```

### 127

Exit code `127` indicates that the contained command can't be found.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run busybox foo; echo $?

docker: Error response from daemon: Container command 'foo' not found or does not exist.
127

```

### Other exit codes

Any exit code other than `125`, `126`, and `127` represent the exit code of the
provided container command.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run busybox /bin/sh -c 'exit 3'
$ echo $?
3

```

## Runtime constraints on resources

The operator can also adjust the performance parameters of the
container:OptionDescription`-m`, `--memory=""`Memory limit (format: `<number>[<unit>]`). Number is a positive integer. Unit can be one of `b`, `k`, `m`, or `g`. Minimum is 6M.`--memory-swap=""`Total memory limit (memory + swap, format: `<number>[<unit>]`). Number is a positive integer. Unit can be one of `b`, `k`, `m`, or `g`.`--memory-reservation=""`Memory soft limit (format: `<number>[<unit>]`). Number is a positive integer. Unit can be one of `b`, `k`, `m`, or `g`.`-c`, `--cpu-shares=0`CPU shares (relative weight)`--cpus=0.000`Number of CPUs. Number is a fractional number. 0.000 means no limit.`--cpu-period=0`Limit the CPU CFS (Completely Fair Scheduler) period`--cpuset-cpus=""`CPUs in which to allow execution (0-3, 0,1)`--cpuset-mems=""`Memory nodes (MEMs) in which to allow execution (0-3, 0,1). Only effective on NUMA systems.`--cpu-quota=0`Limit the CPU CFS (Completely Fair Scheduler) quota`--cpu-rt-period=0`Limit the CPU real-time period. In microseconds. Requires parent cgroups be set and cannot be higher than parent. Also check rtprio ulimits.`--cpu-rt-runtime=0`Limit the CPU real-time runtime. In microseconds. Requires parent cgroups be set and cannot be higher than parent. Also check rtprio ulimits.`--blkio-weight=0`Block IO weight (relative weight) accepts a weight value between 10 and 1000.`--blkio-weight-device=""`Block IO weight (relative device weight, format: `DEVICE_NAME:WEIGHT`)`--device-read-bps=""`Limit read rate from a device (format: `<device-path>:<number>[<unit>]`). Number is a positive integer. Unit can be one of `kb`, `mb`, or `gb`.`--device-write-bps=""`Limit write rate to a device (format: `<device-path>:<number>[<unit>]`). Number is a positive integer. Unit can be one of `kb`, `mb`, or `gb`.`--device-read-iops=""`Limit read rate (IO per second) from a 

... [Content truncated]