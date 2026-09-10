# Docker Engine API | Docker Docs

> Source: https://docs.docker.com/engine/api/
> Cached: 2026-09-10T08:45:57.970Z

---

Home
/
Reference
/
API reference
/
Docker Engine API# Docker Engine API

Ask Gordon

Copy Markdown

View MarkdownTable of contents
- View the API reference
- Versioned API and SDK

- Minimum API version
- API version matrix
- Deprecated API versions

Docker provides an API for interacting with the Docker daemon (called the Docker
Engine API), as well as SDKs for Go and Python. The SDKs allow you to efficiently build and
scale Docker apps and solutions. If Go or Python don't work
for you, you can use the Docker Engine API directly.For information about Docker Engine SDKs, see Develop with Docker Engine SDKs.

The Docker Engine API is a RESTful API accessed by an HTTP client such as `wget` or
`curl`, or the HTTP library which is part of most modern programming languages.## View the API reference

You can
view the reference for the latest version of the API
or
choose a specific version.## Versioned API and SDK

The version of the Docker Engine API you should use depends upon the version of
your Docker daemon and Docker client.A given version of the Docker Engine SDK supports a specific version of the
Docker Engine API, as well as all earlier versions. If breaking changes occur,
they are documented prominently.> 
NoteThe Docker daemon and client don't necessarily need to be the same version
at all times. However, keep the following in mind.
If the daemon is newer than the client, the client doesn't know about new
features or deprecated API endpoints in the daemon.If the client is newer than the daemon, the client can request API
endpoints that the daemon doesn't know about.

A new version of the API is released when new features are added. The Docker API
is backward-compatible, so you don't need to update code that uses the API
unless you need to take advantage of new features.To see the highest and lowest version of the API your Docker daemon and client
support, use `docker version`:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ docker version
Client: Docker Engine - Community
 Version:           29.8.0
 API version:       1.56
 ...

Server: Docker Engine - Community
 Engine:
  Version:          29.8.0
  API version:      1.56 (minimum version 1.40)
  ...

```

You can specify the API version to use in any of the following ways:

When using the SDK, use the latest version. At a minimum, use the version
that incorporates the API version with the features you need.When using `curl` directly, specify the version as the first part of the URL.
For instance, if the endpoint is `/containers/` you can use
`/v1.56/containers/`.To force the Docker CLI or the Docker Engine SDKs to use an older version
of the API than the version reported by `docker version`, set the
environment variable `DOCKER_API_VERSION` to the correct version. This works
on Linux, Windows, and macOS clients.]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ DOCKER_API_VERSION=1.55

```

While the environment variable is set, that version of the API is used, even
if the Docker daemon supports a newer version. This environment variable
disables API version negotiation, so you should only use it if you must
use a specific version of the API, or for debugging purposes.The Docker Go SDK allows you to enable API version negotiation, automatically
selects an API version that's supported by both the client and the Docker Engine
that's in use.For the SDKs, you can also specify the API version programmatically as a
parameter to the `client` object. See the
Go constructor
or the
Python SDK documentation for `client`.
### Minimum API version

The Docker Engine API server and client support API-version negotiation. If
a client connects to an older version of the Docker Engine, it negotiates
the highest version of the API supported by both the client and daemon,
downgrading to an older version of the API if necessary.When downgrading to an older API version, features introduced in later API
versions are disabled, and API requests and responses are adjusted for the
API version negotiated.API version negotiation allows tools that have not been upgraded yet to the
latest API version specification to communicate with newer Docker Engines
(and vice versa), but compatibility is "best effort"; while Docker strives
to provide full compatibility, some functionality may not be available.### API version matrix

Docker versionMaximum API versionMinimum API versionChange log29.81.551.40changes29.71.551.40changes29.61.551.40changes29.51.541.40changes29.41.541.40changes29.31.541.40changes29.21.531.44changes29.11.521.44changes29.01.521.44changes28.51.511.24changes28.41.511.24changes28.31.511.24changes28.21.501.24changes28.11.491.24changes28.01.481.24changes27.51.471.24changes27.41.471.24changes27.31.471.24changes27.21.471.24changes27.11.461.24changes27.01.461.24changes26.11.451.24changes26.01.451.24changes25.01.441.24changes24.01.431.12changes23.01.421.12changes20.101.411.12changes19.031.401.12changes### Deprecated API versions

API versions before v1.40 are deprecated and no longer supported by current
versions of the Docker Engine and CLI. You can find archived documentation
for deprecated versions of the API in the code repository on GitHub:Docker versionMaximum API versionMinimum API versionChange log18.091.391.12changes18.061.381.12changes18.051.371.12changes18.041.371.12changes18.031.371.12changes18.021.361.12changes17.121.351.12changes17.111.341.12changes17.101.331.12changes17.091.321.12changes17.071.311.12changes17.061.301.12changes17.051.291.12changes17.041.281.12changes17.03.11.271.12changes17.031.261.12changes1.13.11.261.12changes1.131.251.12changes1.121.241.12changes1.111.231.12changes1.101.221.12changes1.91.211.12changes1.81.201.12changes1.71.191.0changes1.61.181.0changes1.51.171.0changes1.41.161.0changes1.31.151.0changes1.21.141.0changes1.11.131.0changes1.01.121.0changes0.121.121.0changes0.111.111.0changes0.101.101.0changes0.91.101.0changes0.81.91.0changes0.7.11.81.0changes0.71.71.0changes0.6.41.61.0changes0.6.21.51.0changes0.61.41.0changes0.51.31.0changes0.4.11.21.0changes0.3.41.11.0changes0.3.31.01.0changes0.3.2--0.2--0.1--