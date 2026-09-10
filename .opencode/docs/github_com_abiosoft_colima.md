# GitHub - abiosoft/colima: Container runtimes on macOS (and Linux) with minimal setup · GitHub

> Source: https://github.com/abiosoft/colima
> Cached: 2026-09-10T08:35:31.092Z

---

[](/abiosoft/colima/blob/main/colima.png)

## Colima - container runtimes on macOS (and Linux) with minimal setup.

[](#colima---container-runtimes-on-macos-and-linux-with-minimal-setup)
[](https://github.com/abiosoft/colima/actions/workflows/go.yml)
[](https://github.com/abiosoft/colima/actions/workflows/linux-integration.yml)
[](https://github.com/abiosoft/colima/actions/workflows/macos-integration.yml)
[](https://goreportcard.com/report/github.com/abiosoft/colima)
[](/abiosoft/colima/blob/main/colima.gif)

**Website & Documentation:** [colima.run](https://colima.run) | [colima.run/docs](https://colima.run/docs/)

## Features

[](#features)
Support for Intel and Apple Silicon macOS, and Linux

- Simple CLI interface with sensible defaults

- Automatic Port Forwarding

- Volume mounts

- Multiple instances

Support for multiple container runtimes

- [Docker](https://docker.com) (with optional Kubernetes)

- [Containerd](https://containerd.io) (with optional Kubernetes)

- [Incus](https://linuxcontainers.org/incus) (containers and virtual machines)

- GPU accelerated containers for AI workloads

## Getting Started

[](#getting-started)
### Installation

[](#installation)
Colima is available on Homebrew, MacPorts, Nix and [Mise](http://github.com/jdx/mise). Check [here](/abiosoft/colima/blob/main/docs/INSTALL.md) for other installation options.

# Homebrew
brew install colima

# MacPorts
sudo port install colima

# Nix
nix-env -iA nixpkgs.colima

# Mise
mise use -g colima@latest

Or stay on the bleeding edge (only Homebrew)

```
brew install --HEAD colima

```

## Usage

[](#usage)
Start Colima with defaults

```
colima start

```

For more usage options

```
colima --help
colima start --help

```

Or use a config file

```
colima start --edit

```

## Runtimes

[](#runtimes)
On initial startup, Colima initiates with a user specified runtime that defaults to Docker.

### Docker

[](#docker)
Docker client is required for Docker runtime. Installable with `brew install docker`.

```
colima start
docker run hello-world
docker ps

```

You can use the `docker` client on macOS after `colima start` with no additional setup.

### Containerd

[](#containerd)
`colima start --runtime containerd` starts and setup Containerd. You can use `colima nerdctl` to interact with
Containerd using [nerdctl](https://github.com/containerd/nerdctl).
```
colima start --runtime containerd
nerdctl run hello-world
nerdctl ps

```

It is recommended to run `colima nerdctl install` to install `nerdctl` alias script in $PATH.

### Kubernetes

[](#kubernetes)
kubectl is required for Kubernetes. Installable with `brew install kubectl`.

To enable Kubernetes, start Colima with `--kubernetes` flag.

```
colima start --kubernetes
kubectl run caddy --image=caddy
kubectl get pods

```

#### Interacting with Image Registry

[](#interacting-with-image-registry)
For Docker runtime, images built or pulled with Docker are accessible to Kubernetes.

For Containerd runtime, images built or pulled in the `k8s.io` namespace are accessible to Kubernetes.

### Incus

[](#incus)
**Requires v0.7.0**

Incus client is required for Incus runtime. Installable with brew `brew install incus`.

`colima start --runtime incus` starts and setup Incus.

```
colima start --runtime incus
incus launch images:alpine/edge
incus list

```

You can use the `incus` client on macOS after `colima start` with no additional setup.

**Note:** Running virtual machines on Incus is only supported on m3 or newer Apple Silicon devices.

### AI Models (GPU Accelerated)

[](#ai-models-gpu-accelerated)
**Requires v0.10.0, Apple Silicon and macOS 13+**

Colima supports GPU accelerated containers for AI workloads using the `krunkit` VM type.

**Note:** To use krunkit with colima, ensure it is installed.  Please follow their [installation instructions](https://github.com/containers/krunkit#installation)

Setup and use a model.

```
colima start --runtime docker --vm-type krunkit
colima model run gemma3

```

Colima supports two model runner backends:

- **Docker Model Runner** (default) — supports [Docker AI Registry](https://hub.docker.com/u/ai) and [HuggingFace](https://huggingface.co).

- **Ramalama** — supports [HuggingFace](https://huggingface.co) and [Ollama](https://ollama.com) registries.

The default registry is the Docker AI Registry. Models can be run by name without a prefix:

colima model run gemma3
colima model run llama3.2
# HuggingFace (Docker Model Runner)
colima model run hf.co/microsoft/Phi-3-mini-4k-instruct-gguf
# Ollama (requires ramalama runner)
colima model run ollama://gemma3 --runner ramalama
See the [AI Workloads documentation](https://colima.run/docs/ai/) for more details.

### Customizing the VM

[](#customizing-the-vm)
The default VM created by Colima has 2 CPUs, 2GiB memory and 100GiB storage.

The VM can be customized either by passing additional flags to `colima start`.
e.g. `--cpu`, `--memory`, `--disk`, `--runtime`.
Or by editing the config file with `colima start --edit`.
**NOTE**: Disk size can be increased after the VM is created.

#### Customization Examples

[](#customization-examples)

create VM with 1CPU, 2GiB memory and 10GiB storage.

```
colima start --cpu 1 --memory 2 --disk 10

```

modify an existing VM to 4CPUs and 8GiB memory.

```
colima stop
colima start --cpu 4 --memory 8

```

create VM with Rosetta 2 emulation. Requires v0.5.3 and macOS >= 13 (Ventura) on Apple Silicon.

```
colima start --vm-type=vz --vz-rosetta

```

## Project Goal

[](#project-goal)
To provide container runtimes on macOS with minimal setup.

## What is with the name?

[](#what-is-with-the-name)
Colima means Containers on [Lima](https://github.com/lima-vm/lima).

Since Lima is aka Linux Machines. By transitivity, Colima can also mean Containers on Linux Machines.

## And the Logo?

[](#and-the-logo)
The logo was contributed by [Daniel Hodvogner](https://github.com/dhodvogner). Check [this issue](https://github.com/abiosoft/colima/issues/781) for more.

## Troubleshooting and FAQs

[](#troubleshooting-and-faqs)
Check [here](/abiosoft/colima/blob/main/docs/FAQ.md) for Frequently Asked Questions, or visit the [online FAQ](https://colima.run/docs/faq/) for a searchable version.

## How to Contribute?

[](#how-to-contribute)
Check [here](/abiosoft/colima/blob/main/docs/CONTRIBUTE.md) for the instructions on contributing to the project.

## Community

[](#community)

- [GitHub Discussions](https://github.com/abiosoft/colima/discussions)

- [GitHub Issues](https://github.com/abiosoft/colima/issues)

- [Announcements](https://colima.run/announcements/)

`#colima` channel in the CNCF Slack

- New account: [https://slack.cncf.io/](https://slack.cncf.io/)

- Login: [https://cloud-native.slack.com/](https://cloud-native.slack.com/)

## License

[](#license)
MIT

## Sponsoring the Project

[](#sponsoring-the-project)
If you (or your company) are benefiting from the project and would like to support the contributors, kindly sponsor.

- [Github Sponsors](https://github.com/sponsors/abiosoft)

- [Buy me a coffee](https://www.buymeacoffee.com/abiosoft)

- [Patreon](https://patreon.com/colima)

[](https://macstadium.com)