# compose-spec/05-services.md at main · compose-spec/compose-spec · GitHub

> Source: https://github.com/compose-spec/compose-spec/blob/main/05-services.md
> Cached: 2026-09-10T08:35:12.445Z

---

# Services top-level element

[](#services-top-level-element)
A service is an abstract definition of a computing resource within an application which can be scaled or replaced
independently from other components. Services are backed by a set of containers, run by the platform
according to replication requirements and placement constraints. As services are backed by containers, they are defined
by a Docker image and set of runtime arguments. All containers within a service are identically created with these
arguments.
A Compose file must declare a `services` top-level element as a map whose keys are string representations of service names,
and whose values are service definitions. A service  definition contains the configuration that is applied to each
service container.
Each service may also include a `build` section, which defines how to create the Docker image for the service.
Compose supports building docker images using this service definition. If not used, the `build` section is ignored and the Compose file is still considered valid. Build support is an optional aspect of the Compose Specification, and is
described in detail in the [Compose Build Specification](/compose-spec/compose-spec/blob/main/build.md) documentation.
Each service defines runtime constraints and requirements to run its containers. The `deploy` section groups
these constraints and allows the platform to adjust the deployment strategy to best match containers' needs with
available resources. Deploy support is an optional aspect of the Compose Specification, and is
described in detail in the [Compose Deploy Specification](/compose-spec/compose-spec/blob/main/deploy.md) documentation.
If not implemented the `deploy` section is ignored and the Compose file is still considered valid.
## annotations

[](#annotations)
`annotations` defines annotations for the container. `annotations` can use either an array or a map.

annotations:
  com.example.foo: bar
annotations:
  - com.example.foo=bar
## attach

[](#attach)
[](https://github.com/docker/compose/releases/v2.20.0)

When `attach` is defined and set to `false` Compose does not collect service logs,
until you explicitly request it to.
The default service configuration is `attach: true`.

## build

[](#build)
`build` specifies the build configuration for creating a container image from source, as defined in the [Compose Build Specification](/compose-spec/compose-spec/blob/main/build.md).

## blkio_config

[](#blkio_config)
`blkio_config` defines a set of configuration options to set block IO limits for a service.

services:
  foo:
    image: busybox
    blkio_config:
       weight: 300
       weight_device:
         - path: /dev/sda
           weight: 400
       device_read_bps:
         - path: /dev/sdb
           rate: '12mb'
       device_read_iops:
         - path: /dev/sdb
           rate: 120
       device_write_bps:
         - path: /dev/sdb
           rate: '1024k'
       device_write_iops:
         - path: /dev/sdb
           rate: 30
### device_read_bps, device_write_bps

[](#device_read_bps-device_write_bps)
Set a limit in bytes per second for read / write operations on a given device.
Each item in the list must have two keys:

- `path`: Defines the symbolic path to the affected device.

- `rate`: Either as an integer value representing the number of bytes or as a string expressing a byte value.

### device_read_iops, device_write_iops

[](#device_read_iops-device_write_iops)
Set a limit in operations per second for read / write operations on a given device.
Each item in the list must have two keys:

- `path`: Defines the symbolic path to the affected device.

- `rate`: As an integer value representing the permitted number of operations per second.

### weight

[](#weight)
Modify the proportion of bandwidth allocated to a service relative to other services.
Takes an integer value between 10 and 1000, with 500 being the default.
### weight_device

[](#weight_device)
Fine-tune bandwidth allocation by device. Each item in the list must have two keys:

- `path`: Defines the symbolic path to the affected device.

- `weight`: An integer value between 10 and 1000.

## cpu_count

[](#cpu_count)
`cpu_count` defines the number of usable CPUs for service container.

## cpu_percent

[](#cpu_percent)
`cpu_percent` defines the usable percentage of the available CPUs.

## cpu_shares

[](#cpu_shares)
`cpu_shares` defines, as integer value, a service container's relative CPU weight versus other containers.

## cpu_period

[](#cpu_period)
`cpu_period` configures CPU CFS (Completely Fair Scheduler) period when a platform is based
on Linux kernel.
## cpu_quota

[](#cpu_quota)
`cpu_quota` configures CPU CFS (Completely Fair Scheduler) quota when a platform is based
on Linux kernel.
## cpu_rt_runtime

[](#cpu_rt_runtime)
`cpu_rt_runtime` configures CPU allocation parameters for platforms with support for realtime scheduler. It can be either
an integer value using microseconds as unit or a [duration](/compose-spec/compose-spec/blob/main/11-extension.md#specifying-durations).
 cpu_rt_runtime: '400ms'
 cpu_rt_runtime: 95000`
## cpu_rt_period

[](#cpu_rt_period)
`cpu_rt_period` configures CPU allocation parameters for platforms with support for realtime scheduler. It can be either
an integer value using microseconds as unit or a [duration](/compose-spec/compose-spec/blob/main/11-extension.md#specifying-durations).
 cpu_rt_period: '1400us'
 cpu_rt_period: 11000`
## cpus

[](#cpus)
`cpus` define the number of (potentially virtual) CPUs to allocate to service containers. This is a fractional number.
`0.000` means no limit.
When both are set, `cpus` must be consistent with the `cpus` attribute in the
[Deploy Specification](/compose-spec/compose-spec/blob/main/deploy.md#cpus)
## cpuset

[](#cpuset)
`cpuset` defines the explicit CPUs in which to allow execution. Can be a range `0-3` or a list `0,1`

## cap_add

[](#cap_add)
`cap_add` specifies additional container [capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
as strings.
cap_add:
  - ALL
## cap_drop

[](#cap_drop)
`cap_drop` specifies container [capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html) to drop
as strings.
cap_drop:
  - NET_ADMIN
  - SYS_ADMIN
## cgroup

[](#cgroup)
[](https://github.com/docker/compose/releases/v2.15.0)

`cgroup` specifies the cgroup namespace to join. When unset, it is the container runtime's decision to
select which cgroup namespace to use, if supported.

- `host`: Runs the container in the Container runtime cgroup namespace.

- `private`: Runs the container in its own private cgroup namespace.

## cgroup_parent

[](#cgroup_parent)
`cgroup_parent` specifies an optional parent [cgroup](https://man7.org/linux/man-pages/man7/cgroups.7.html) for the container.

cgroup_parent: m-executor-abcd
## command

[](#command)
`command` overrides the default command declared by the container image, for example by Dockerfile's `CMD`.

command: bundle exec thin -p 3000
> 
**Note**

Unlike the `CMD` instruction of an image, the [shell-form syntax](https://docs.docker.com/reference/dockerfile/#shell-form) for `command`
does not implicitly run in the context of the [`SHELL` instruction](https://docs.docker.com/reference/dockerfile/#shell).
If you expect the command to rely on features of a shell environment such as environment variables, then ensure the command is run within a shell:

command: /bin/sh -c 'echo "hello $$HOSTNAME"'

The value can also be a list, in a manner similar to the [exec-form syntax](https://docs.docker.com/reference/dockerfile/#exec-form)
used by [Dockerfile](https://docs.docker.com/engine/reference/#cmd).
command: [ "bundle", "exec", "thin", "-p", "3000" ]
If the value is `null`, the default command from the image is used.

If the value is `[]` (empty list) or `''` (empty string), the default command declared by the image is ignored,
i.e. overridden to be empty.
## configs

[](#configs)
Configs allow services to adapt their behaviour without the need to rebuild a Docker image.
Services can only access configs when explicitly granted by the `configs` attribute. Two different syntax variants are supported.
Compose reports an error if `config` doesn't exist on the platform or isn't defined in the
[`configs` top-level element](/compose-spec/compose-spec/blob/main/08-configs.md) in the Compose file.
There are two syntaxes defined for configs. To remain compliant to this specification, an implementation
must support both syntaxes. Implementations must allow use of both short and long syntaxes within the same document.
You can grant a service access to multiple configs, and you can mix long and short syntax.

### Short syntax

[](#short-syntax)
The short syntax variant only specifies the config name. This grants the
container access to the config and mounts it as files into a service’s container’s filesystem. The location of the mount point within the container defaults to `/<config_name>` in Linux containers, and `C:\<config-name>` in Windows containers.
The following example uses the short syntax to grant the `redis` service
access to the `my_config` and `my_other_config` configs. The value of
`my_config` is set to the contents of the file `./my_config.txt`, and
`my_other_config` is defined as an external resource, which means that it has
already been defined in the platform. If the external config does not exist,
the deployment fails.
services:
  redis:
    image: redis:latest
    configs:
      - my_config
      - my_other_config
configs:
  my_config:
    file: ./my_config.txt
  my_other_config:
    external: true
### Long syntax

[](#long-syntax)
The long syntax provides more granularity in how the config is created within the service's task containers.

- `source`: The name of the config as it exists in the platform.

`target`: The path and name of the file to be mounted in the service's
task containers. Defaults to `/<source>` if not specified.
`uid` and `gid`: The numeric UID or GID that owns the mounted config file
within the service's task containers.
`mode`: The [permissions](https://wintelguy.com/permissions-calc.pl) for the file that is mounted within the service's
task containers, in octal notation. Default value is world-readable (`0444`).
Writable bit must be ignored. The executable bit can be set.

> 
**Note**

The `uid`, `gid`, and `mode` attributes are not implemented in Docker Compose when the source
of the config is a [`file`](/compose-spec/compose-spec/blob/main/08-configs.md), as bind-mount used under the hood doesn't allow uid remapping.

The following example sets the name of `my_config` to `redis_config` within the
container, sets the mode to `0440` (group-readable) and sets the user and group
to `103`. The `redis` service does not have access to the `my_other_config`
config.
services:
  redis:
    image: redis:latest
    configs:
      - source: my_config
        target: /redis_config
        uid: "103"
        gid: "103"
        mode: 0440
configs:
  my_config:
    external: true
  my_other_config:
    external: true
## container_name

[](#container_name)
`container_name` is a string that specifies a custom container name, rather than a name generated by default.

container_name: my-web-container
Compose does not scale a service beyond one container if the Compose file specifies a
`container_name`. Attempting to do so results in an error.
`container_name` follows the regex format of `[a-zA-Z0-9][a-zA-Z0-9_.-]+`

## credential_spec

[](#credential_spec)
`credential_spec` configures the credential spec for a managed service account.

If you have services that use Windows containers, you can use `file:` and
`registry:` protocols for `credential_spec`. Compose also supports additional
protocols for custom use-cases.
The `credential_spec` must be in the format `file://<filename>` or `registry://<value-name>`.

credential_spec:
  file: my-credential-spec.json
When using `registry:`, the credential spec is read from the Windows registry on
the daemon's host. A registry value with the given name must be located in:
```
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Virtualization\Containers\CredentialSpecs

```

The following example loads the credential spec from a value named `my-credential-spec`
in the registry:
credential_spec:
  registry: my-credential-spec
### Example gMSA configuration

[](#example-gmsa-configuration)
When configuring a gMSA credential spec for a service, you only need
to specify a credential spec with `config`, as shown in the following example:
services:
  myservice:
    image: myimage:latest
    credential_spec:
      config: my_credential_spec

configs:
  my_credentials_spec:
    file: ./my-credential-spec.json|
## depends_on

[](#depends_on)
`depends_on` expresses startup and shutdown dependencies between services.

### Short syntax

[](#short-syntax-1)
The short syntax variant only specifies service names of the dependencies.
Service dependencies cause the following behaviors:

Compose creates services in dependency order. In the following
example, `db` and `redis` are created before `web`.

Compose removes services in dependency order. In the following
example, `web` is removed before `db` and `redis`.

Simple example:

services:
  web:
    build: .
    depends_on:
      - db
      - redis
  redis:
    image: redis
  db:
    image: postgres
Compose guarantees dependency services have been started before
starting a dependent service.
Compose waits for dependency services to be "ready" before
starting a dependent service.
### Long syntax

[](#long-syntax-1)
The long form syntax enables the configuration of additional fields that can't be
expressed in the short form.

`restart`: When set to `true` Compose restarts this service after it updates the dependency service.
This applies to an explicit restart controlled by a Compose operation, and excludes automated restart by the container runtime
after the container dies. [](https://github.com/docker/compose/releases/v2.17.0)

`condition`: Sets the condition under which dependency is considered satisfied

- `service_started`: An equivalent of the short syntax described above

`service_healthy`: Specifies that a dependency is expected to be "healthy"
(as indicated by [healthcheck](#healthcheck)) before starting a dependent
service.
`service_completed_successfully`: Specifies that a dependency is expected to run
to successful completion before starting a dependent service.

`required`: When set to `false` Compose only warns you when the dependency service isn't started or available. If it's not defined
the default value of `required` is `true`. [](https://github.com/docker/compose/releases/v2.20.0)

Service dependencies cause the following behaviors:

Compose creates services in dependency order. In the following
example, `db` and `redis` are created before `web`.

Compose waits for healthchecks to pass on dependencies
marked with `service_healthy`. In the following example, `db` is expected to
be "

... [Content truncated]