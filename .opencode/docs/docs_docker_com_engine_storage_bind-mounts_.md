# Bind mounts | Docker Docs

> Source: https://docs.docker.com/engine/storage/bind-mounts/
> Cached: 2026-09-10T08:35:30.460Z

---

Home
/
Manuals
/
Docker Engine
/
Storage
/
Bind mounts# Bind mounts

Ask Gordon

Copy Markdown

View MarkdownTable of contents
- When to use bind mounts
- Bind-mounting over existing data
- Considerations and constraints
- Syntax

- Options for --mount
- Options for --volume

- Start a container with a bind mount

- Mount into a non-empty directory on the container

- Use a read-only bind mount
- Recursive mounts
- Configure bind propagation
- Configure the SELinux label
- Use a bind mount with Docker Compose
- Next steps

When you use a bind mount, a file or directory on the host machine is mounted
from the host into a container. By contrast, when you use a volume, a new
directory is created within Docker's storage directory on the host machine.
Docker creates and maintains this storage location, but containers access it
directly using standard filesystem operations.## When to use bind mounts

Bind mounts are appropriate for the following types of use case:

Sharing source code or build artifacts between a development environment on
the Docker host and a container.When you want to create or generate files in a container and persist the
files onto the host's filesystem.Sharing configuration files from the host machine to containers. This is how
Docker provides DNS resolution to containers by default, by mounting
`/etc/resolv.conf` from the host machine into each container.
Bind mounts are also available for builds: you can bind mount source code from
the host into the build container to test, lint, or compile a project.## Bind-mounting over existing data

If you bind mount file or directory into a directory in the container in which
files or directories exist, the pre-existing files are obscured by the mount.
This is similar to if you were to save files into `/mnt` on a Linux host, and
then mounted a USB drive into `/mnt`. The contents of `/mnt` would be obscured
by the contents of the USB drive until the USB drive was unmounted.With containers, there's no straightforward way of removing a mount to reveal
the obscured files again. Your best option is to recreate the container without
the mount.## Considerations and constraints

Bind mounts have write access to files on the host by default.

One side effect of using bind mounts is that you can change the host
filesystem via processes running in a container, including creating,
modifying, or deleting important system files or directories. This capability
can have security implications. For example, it may affect non-Docker
processes on the host system.You can use the `readonly` or `ro` option to prevent the container from
writing to the mount.Bind mounts are created to the Docker daemon host, not the client.

If you're using a remote Docker daemon, you can't create a bind mount to
access files on the client machine in a container.For Docker Desktop, the daemon runs inside a Linux VM, not directly on the
native host. Docker Desktop has built-in mechanisms that transparently handle
bind mounts, allowing you to share native host filesystem paths with
containers running in the virtual machine.Containers with bind mounts are strongly tied to the host.

Bind mounts rely on the host machine's filesystem having a specific directory
structure available. This reliance means that containers with bind mounts may
fail if run on a different host without the same directory structure.
## Syntax

To create a bind mount, you can use either the `--mount` or `--volume` flag.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run --mount type=bind,src=<host-path>,dst=<container-path>
$ docker run --volume <host-path>:<container-path>

```

In general, `--mount` is preferred. The main difference is that the `--mount`
flag is more explicit and supports all the available options.If you use `--volume` to bind-mount a file or directory that does not yet
exist on the Docker host, Docker automatically creates the directory on the
host for you. It's always created as a directory. If the Docker daemon doesn't
have permission to create the source directory, create it before starting the
container.By default, `--mount` does not automatically create a directory if the specified mount
path does not exist on the host. Instead, it produces an error:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run --mount type=bind,src=/dev/noexist,dst=/mnt/foo alpine
docker: Error response from daemon: invalid mount config for type &#34;bind&#34;: bind source path does not exist: /dev/noexist.

```

You can use the `bind-create-src` option to automatically create the source directory
on the host if it doesn't exist:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run --mount type=bind,src=/home/user/mydir,dst=/mnt/foo,bind-create-src alpine

```

### Options for --mount

The `--mount` flag consists of multiple key-value pairs, separated by commas
and each consisting of a `<key>=<value>` tuple. The order of the keys isn't
significant.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run --mount type=bind,src=<host-path>,dst=<container-path>[,<key>=<value>...]

```

Valid options for `--mount type=bind` include:

OptionDescription`source`, `src`The location of the file or directory on the host. This can be an absolute or relative path.`destination`, `dst`, `target`The path where the file or directory is mounted in the container. Must be an absolute path.`readonly`, `ro`If present, causes the bind mount to be mounted into the container as read-only.`bind-propagation`If present, changes the bind propagation.`bind-create-src`Automatically creates the source directory on the host if it doesn't exist. By default, `--mount` produces an error if the source path doesn't exist on the daemon.Example]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run --mount type=bind,src=.,dst=/project,ro,bind-propagation=rshared

```

### Options for --volume

The `--volume` or `-v` flag consists of three fields, separated by colon
characters (`:`). The fields must be in the correct order.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -v <host-path>:<container-path>[:opts]

```

The first field is the path on the host to bind mount into the container. The
second field is the path where the file or directory is mounted in the
container.The third field is optional, and is a comma-separated list of options. Valid
options for `--volume` with a bind mount include:OptionDescription`readonly`, `ro`If present, causes the bind mount to be mounted into the container as read-only.`z`, `Z`Configures SELinux labeling. See Configure the SELinux label`rprivate` (default)Sets bind propagation to `rprivate` for this mount. See Configure bind propagation.`private`Sets bind propagation to `private` for this mount. See Configure bind propagation.`rshared`Sets bind propagation to `rshared` for this mount. See Configure bind propagation.`shared`Sets bind propagation to `shared` for this mount. See Configure bind propagation.`rslave`Sets bind propagation to `rslave` for this mount. See Configure bind propagation.`slave`Sets bind propagation to `slave` for this mount. See Configure bind propagation.Example]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -v .:/project:ro,rshared

```

## Start a container with a bind mount

Consider a case where you have a directory `source` and that when you build the
source code, the artifacts are saved into another directory, `source/target/`.
You want the artifacts to be available to the container at `/app/`, and you
want the container to get access to a new build each time you build the source
on your development host. Use the following command to bind-mount the `target/`
directory into your container at `/app/`. Run the command from within the
`source` directory. The `$(pwd)` sub-command expands to the current working
directory on Linux or macOS hosts.
If you're on Windows, see also
Path conversions on Windows.The following `--mount` and `-v` examples produce the same result. You can't
run them both unless you remove the `devtest` container after running the first
one.
`--mount`

`-v`]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -d \
  -it \
  --name devtest \
  --mount type=bind,source=&#34;$(pwd)&#34;/target,target=/app \
  nginx:latest

```

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -d \
  -it \
  --name devtest \
  -v &#34;$(pwd)&#34;/target:/app \
  nginx:latest

```

Use `docker inspect devtest` to verify that the bind mount was created
correctly. Look for the `Mounts` section:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
&#34;Mounts&#34;: [
    {
        &#34;Type&#34;: &#34;bind&#34;,
        &#34;Source&#34;: &#34;/tmp/source/target&#34;,
        &#34;Destination&#34;: &#34;/app&#34;,
        &#34;Mode&#34;: &#34;&#34;,
        &#34;RW&#34;: true,
        &#34;Propagation&#34;: &#34;rprivate&#34;
    }
],
```

This shows that the mount is a `bind` mount, it shows the correct source and
destination, it shows that the mount is read-write, and that the propagation is
set to `rprivate`.Stop and remove the container:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker container rm -fv devtest

```

### Mount into a non-empty directory on the container

If you bind-mount a directory into a non-empty directory on the container, the
directory's existing contents are obscured by the bind mount. This can be
beneficial, such as when you want to test a new version of your application
without building a new image. However, it can also be surprising and this
behavior differs from that of volumes.This example is contrived to be extreme, but replaces the contents of the
container's `/usr/` directory with the `/tmp/` directory on the host machine. In
most cases, this would result in a non-functioning container.The `--mount` and `-v` examples have the same end result.

`--mount`

`-v`]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -d \
  -it \
  --name broken-container \
  --mount type=bind,source=/tmp,target=/usr \
  nginx:latest

docker: Error response from daemon: oci runtime error: container_linux.go:262:
starting container process caused &#34;exec: \&#34;nginx\&#34;: executable file not found in $PATH&#34;.

```

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -d \
  -it \
  --name broken-container \
  -v /tmp:/usr \
  nginx:latest

docker: Error response from daemon: oci runtime error: container_linux.go:262:
starting container process caused &#34;exec: \&#34;nginx\&#34;: executable file not found in $PATH&#34;.

```

The container is created but does not start. Remove it:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker container rm broken-container

```

## Use a read-only bind mount

For some development applications, the container needs to
write into the bind mount, so changes are propagated back to the
Docker host. At other times, the container only needs read access.This example modifies the previous one, but mounts the directory as a read-only
bind mount, by adding `ro` to the (empty by default) list of options, after the
mount point within the container. Where multiple options are present, separate
them by commas.The `--mount` and `-v` examples have the same result.

`--mount`

`-v`]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -d \
  -it \
  --name devtest \
  --mount type=bind,source=&#34;$(pwd)&#34;/target,target=/app,readonly \
  nginx:latest

```

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker run -d \
  -it \
  --name devtest \
  -v &#34;$(pwd)&#34;/target:/app:ro \
  nginx:latest

```

Use `docker inspect devtest` to verify that the bind mount was created
correctly. Look for the `Mounts` section:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
&#34;Mounts&#34;: [
    {
        &#34;Type&#34;: &#34;bind&#34;,
        &#34;Source&#34;: &#34;/tmp/source/target&#34;,
        &#34;Destination&#34;: &#34;/app&#34;,
        &#34;Mode&#34;: &#34;ro&#34;,
        &#34;RW&#34;: false,
        &#34;Propagation&#34;: &#34;rprivate&#34;
    }
],
```

Stop and remove the container:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker container rm -fv devtest

```

## Recursive mounts

When you bind mount a path that itself contains mounts, those submounts are
also included in the bind mount by default. This behavior is configurable,
using the `bind-recursive` option for `--mount`. This option is only supported
with the `--mount` flag, not with `-v` or `--volume`.If the bind mount is read-only, the Docker Engine makes a best-effort attempt
at making the submounts read-only as well. This is referred to as recursive
read-only mounts. Recursive read-only mounts require Linux kernel version 5.12
or later. If you're running an older kernel version, submounts are
automatically mounted as read-write by default. Attempting to set submounts to
be read-only on a kernel version earlier than 5.12, using the
`bind-recursive=readonly` option, results in an error.Supported values for the `bind-recursive` option are:

ValueDescription`enabled` (default)Read-only mounts are made recursively read-only if kernel is v5.12 or later. Otherwise, submounts are read-write.`disabled`Submounts are ignored (not included in the bind mount).`writable`Submounts are read-write.`readonly`Submounts are read-only. Requires kernel v5.12 or later.## Configure bind propagation

Bind propagation defaults to `rprivate` for both bind mounts and volumes. It is
only configurable for bind mounts, and only on Linux host machines. Bind
propagation is an advanced topic and many users never need to configure it.Bind propagation refers to whether or not mounts created within a given
bind-mount can be propagated to replicas of that mount. Consider
a mount point `/mnt`, which is also mounted on `/tmp`. The propagation settings
control whether a mount on `/tmp/a` would also be available on `/mnt/a`. Each
propagation setting has a recursive counterpoint. In the case of recursion,
consider that `/tmp/a` is also mounted as `/foo`. The propagation settings
control whether `/mnt/a` and/or `/tmp/a` would exist.> 
NoteMount propagation doesn't work with Docker Desktop.

Propagation settingDescription`shared`Sub-mounts of the original mount are exposed to repl

... [Content truncated]