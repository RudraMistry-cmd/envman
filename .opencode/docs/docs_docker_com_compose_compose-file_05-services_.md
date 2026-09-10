# Define services in Docker Compose | Docker Docs

> Source: https://docs.docker.com/compose/compose-file/05-services/#healthcheck
> Cached: 2026-09-10T08:35:11.836Z

---

Home
/
Reference
/
Compose file reference
/
Services# Define services in Docker Compose

Ask Gordon

Copy Markdown

View MarkdownTable of contents
- Examples

- Simple example
- Advanced example

- Attributes

- `annotations`
- `attach`
- `build`
- `blkio_config`

- `cpu_count`
- `cpu_percent`
- `cpu_shares`
- `cpu_period`
- `cpu_quota`
- `cpu_rt_runtime`
- `cpu_rt_period`
- `cpus`
- `cpuset`
- `cap_add`
- `cap_drop`
- `cgroup`
- `cgroup_parent`
- `command`
- `configs`

- `container_name`
- `credential_spec`

- `depends_on`

- `deploy`
- `develop`
- `device_cgroup_rules`
- `devices`
- `dns`
- `dns_opt`
- `dns_search`
- `domainname`
- `driver_opts`
- `entrypoint`
- `env_file`

- `environment`
- `expose`
- `extends`

- `external_links`
- `extra_hosts`

- `gpus`
- `group_add`
- `healthcheck`
- `hostname`
- `image`
- `init`
- `ipc`
- `isolation`
- `labels`
- `label_file`
- `links`
- `logging`
- `mac_address`
- `mem_limit`
- `mem_reservation`
- `mem_swappiness`
- `memswap_limit`
- `models`

- `network_mode`
- `networks`

- `oom_kill_disable`
- `oom_score_adj`
- `pid`
- `pids_limit`
- `platform`
- `ports`

- `post_start`
- pre_start
- `pre_stop`
- `privileged`
- `profiles`
- `provider`

- `pull_policy`
- `read_only`
- `restart`
- `runtime`
- `scale`
- `secrets`

- `security_opt`
- `shm_size`
- `stdin_open`
- `stop_grace_period`
- `stop_signal`
- `storage_opt`
- `sysctls`
- `tmpfs`
- `tty`
- `ulimits`
- `use_api_socket`
- `user`
- `userns_mode`
- `uts`
- `volumes`

- `volumes_from`
- `working_dir`

A service is an abstract definition of a computing resource within an application which can be scaled or replaced
independently from other components. Services are backed by a set of containers, run by the platform
according to replication requirements and placement constraints. As services are backed by containers, they are defined
by a Docker image and set of runtime arguments. All containers within a service are identically created with these
arguments.A Compose file must declare a `services` top-level element as a map whose keys are string representations of service names,
and whose values are service definitions. A service definition contains the configuration that is applied to each
service container.Each service may also include a `build` section, which defines how to create the Docker image for the service.
Compose supports building Docker images using this service definition. If not used, the `build` section is ignored and the Compose file is still considered valid. Build support is an optional aspect of the Compose Specification, and is
described in detail in the Compose Build Specification documentation.Each service defines runtime constraints and requirements to run its containers. The `deploy` section groups
these constraints and lets the platform adjust the deployment strategy to best match containers' needs with
available resources. Deploy support is an optional aspect of the Compose Specification, and is
described in detail in the Compose Deploy Specification documentation.
If not implemented the `deploy` section is ignored and the Compose file is still considered valid.## Examples

### Simple example

The following example demonstrates how to define two simple services, set their images, map ports, and configure basic environment variables using Docker Compose.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
services:
  web:
    image: nginx:latest
    ports:
      - &#34;8080:80&#34;

  db:
    image: postgres:18
    environment:
      POSTGRES_USER: example
      POSTGRES_DB: exampledb
```

### Advanced example

In the following example, the `proxy` service uses the Nginx image, mounts a local Nginx configuration file into the container, exposes port `80` and depends on the `backend` service.

The `backend` service builds an image from the Dockerfile located in the `backend` directory that is set to build at stage `builder`.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
services:
  proxy:
    image: nginx
    volumes:
      - type: bind
        source: ./proxy/nginx.conf
        target: /etc/nginx/conf.d/default.conf
        read_only: true
    ports:
      - 80:80
    depends_on:
      - backend

  backend:
    build:
      context: backend
      target: builder
```

For more example Compose files, explore the Awesome Compose samples.

## Attributes

### `annotations`

`annotations` defines annotations for the container. `annotations` can use either an array or a map.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
annotations:
  com.example.foo: bar
```

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
annotations:
  - com.example.foo=bar
```

### `attach`

Requires:
Docker Compose 2.20.0 and later
When `attach` is defined and set to `false` Compose does not collect service logs,
until you explicitly request it to.The default service configuration is `attach: true`.

### `build`

`build` specifies the build configuration for creating a container image from source, as defined in the Compose Build Specification.

### `blkio_config`

`blkio_config` defines a set of configuration options to set block I/O limits for a service.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
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
```

#### `device_read_bps`, `device_write_bps`

Set a limit in bytes per second for read / write operations on a given device.
Each item in the list must have two keys:
- `path`: Defines the symbolic path to the affected device.
- `rate`: Either as an integer value representing the number of bytes or as a string expressing a byte value.

#### `device_read_iops`, `device_write_iops`

Set a limit in operations per second for read / write operations on a given device.
Each item in the list must have two keys:
- `path`: Defines the symbolic path to the affected device.
- `rate`: As an integer value representing the permitted number of operations per second.

#### `weight`

Modify the proportion of bandwidth allocated to a service relative to other services.
Takes an integer value between 10 and 1000, with 500 being the default.#### `weight_device`

Fine-tune bandwidth allocation by device. Each item in the list must have two keys:

- `path`: Defines the symbolic path to the affected device.
- `weight`: An integer value between 10 and 1000.

### `cpu_count`

`cpu_count` defines the number of usable CPUs for service container.

### `cpu_percent`

`cpu_percent` defines the usable percentage of the available CPUs.

### `cpu_shares`

`cpu_shares` defines, as integer value, a service container's relative CPU weight versus other containers.

### `cpu_period`

`cpu_period` configures CPU CFS (Completely Fair Scheduler) period when a platform is based
on Linux kernel.### `cpu_quota`

`cpu_quota` configures CPU CFS (Completely Fair Scheduler) quota when a platform is based
on Linux kernel.### `cpu_rt_runtime`

`cpu_rt_runtime` configures CPU allocation parameters for platforms with support for real-time scheduler. It can be either
an integer value using microseconds as unit or a duration.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
 cpu_rt_runtime: '400ms'
 cpu_rt_runtime: '95000'
```

### `cpu_rt_period`

`cpu_rt_period` configures CPU allocation parameters for platforms with support for real-time scheduler. It can be either
an integer value using microseconds as unit or a duration.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
 cpu_rt_period: '1400us'
 cpu_rt_period: '11000'
```

### `cpus`

`cpus` define the number of (potentially virtual) CPUs to allocate to service containers. This is a fractional number.
`0.000` means no limit.When set, `cpus` must be consistent with the `cpus` attribute in the Deploy Specification.

### `cpuset`

`cpuset` defines the explicit CPUs in which to permit execution. Can be a range `0-3` or a list `0,1`

### `cap_add`

`cap_add` specifies additional container capabilities
as strings.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
cap_add:
  - ALL
```

### `cap_drop`

`cap_drop` specifies container capabilities to drop
as strings.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
cap_drop:
  - NET_ADMIN
  - SYS_ADMIN
```

### `cgroup`

Requires:
Docker Compose 2.15.0 and later
`cgroup` specifies the cgroup namespace to join. When unset, it is the container runtime's decision to
select which cgroup namespace to use, if supported.
- `host`: Runs the container in the Container runtime cgroup namespace.
- `private`: Runs the container in its own private cgroup namespace.

### `cgroup_parent`

`cgroup_parent` specifies an optional parent cgroup for the container.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
cgroup_parent: m-executor-abcd
```

### `command`

`command` overrides the default command declared by the container image, for example by Dockerfile's `CMD`.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
command: bundle exec thin -p 3000
```

If the value is `null`, the default command from the image is used.

If the value is `[]` (empty list) or `''` (empty string), the default command declared by the image is ignored, or in other words overridden to be empty.

> 
NoteUnlike the `CMD` instruction in a Dockerfile, the `command` field doesn't automatically run within the context of the
`SHELL` instruction defined in the image. If your `command` relies on shell-specific features, such as environment variable expansion, you need to explicitly run it within a shell. For example:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
command: /bin/sh -c 'echo &#34;hello $$HOSTNAME&#34;'
```

The value can also be a list, similar to the
exec-form syntax
used by the
Dockerfile.### `configs`

`configs` let services adapt their behaviour without the need to rebuild a Docker image.
Services can only access configs when explicitly granted by the `configs` attribute. Two different syntax variants are supported.Compose reports an error if `config` doesn't exist on the platform or isn't defined in the
`configs` top-level element in the Compose file.There are two syntaxes defined for configs: a short syntax and a long syntax.

You can grant a service access to multiple configs, and you can mix long and short syntax.

#### Short syntax

The short syntax variant only specifies the config name. This grants the
container access to the config and mounts it as files into a service’s container’s filesystem. The location of the mount point within the container defaults to `/<config_name>` in Linux containers, and `C:\<config-name>` in Windows containers.The following example uses the short syntax to grant the `redis` service
access to the `my_config` and `my_other_config` configs. The value of
`my_config` is set to the contents of the file `./my_config.txt`, and
`my_other_config` is defined as an external resource, which means that it has
already been defined in the platform. If the external config does not exist,
the deployment fails.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
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
```

#### Long syntax

The long syntax provides more granularity in how the config is created within the service's task containers.

- `source`: The name of the config as it exists in the platform.
`target`: The path and name of the file to be mounted in the service's
task containers. Defaults to `/<source>` if not specified.`uid` and `gid`: The numeric uid or gid that owns the mounted config file
within the service's task containers.`mode`: The permissions for the file that is mounted within the service's
task containers, in octal notation. Default value is world-readable (`0444`).
Writable bit must be ignored. The executable bit can be set.
The following example sets the name of `my_config` to `redis_config` within the
container, sets the mode to `0440` (group-readable) and sets the user and group
to `103`. The `redis` service does not have access to the `my_other_config`
config.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
services:
  redis:
    image: redis:latest
    configs:
      - source: my_config
        target: /redis_config
        uid: &#34;103&#34;
        gid: &#34;103&#34;
        mode: 0440
configs:
  my_config:
    external: true
  my_other_config:
    external: true
```

### `container_name`

`container_name` is a string that specifies a custom container name, rather than a name generated by default.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
container_name: my-web-container
```

Compose does not scale a service beyond one container if the Compose file specifies a
`container_name`. Attempting to do so results in an error.`container_name` follows the regex format of `[a-zA-Z0-9][a-zA-Z0-9_.-]+`

### `credential_spec`

`credential_spec` configures the credential spec for a managed service account.

If you have services that use Windows containers, you can use `file:` and
`registry:` protocols for `credential_spec`. Compose also supports additional
protocols for custom use-cases.The `credential_spec` must be in the format `file://<filename>` or `registry://<value-name>`.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
credential_spec:
  file: my-credential-spec.json
```

When using `registry:`, the credential spec is read from the Windows registry on
the daemon's host. A registry value with the given name must be located in:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Virtualization\Containers\CredentialSpecs
```

The following example loads the credential spec from a value named `my-credential-spec`
in the registry:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
credential_spec:
  registry: my-credential-spec
```

#### Example gMSA configuration

When configuring a gMSA credential spec for a service, you only need

... [Content truncated]