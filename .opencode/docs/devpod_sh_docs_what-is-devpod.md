# What is DevPod? | DevPod docs | DevContainers everywhere

> Source: https://devpod.sh/docs/what-is-devpod
> Cached: 2026-09-10T08:35:26.470Z

---

- [](/docs/)
- What is DevPod?

On this page# What is DevPod?

DevPod is a tool used to create reproducible developer environments. Each developer environment runs in a separate container and is specified through a [devcontainer.json](https://containers.dev/). [DevPod providers](/docs/managing-providers/what-are-providers) can create these containers on the local computer, any reachable remote machine, or in a public or private cloud. It&#x27;s also possible to extend DevPod and write your own custom providers.

DevPod
You can think of DevPod as the glue connecting your local IDE to a machine you want to use for development. So depending on your project&#x27;s requirements, you can create a workspace locally on the computer, a powerful cloud machine, or a spare remote computer. Within DevPod, every workspace is managed the same way, which also makes it easy to switch between workspaces that might be hosted somewhere else.

DevPod - Architecture
## Why DevPod?[​](#why-devpod)

DevPod reuses the open [DevContainer standard](https://containers.dev/) to create a consistent developer experience no matter what backend you want to use.

Compared to hosted services such as Github Codespaces, JetBrains Spaces or Google Cloud Workstations, DevPod has the following advantages:

- **Cost savings**: DevPod is usually around 5-10 times cheaper than existing services with comparable feature sets, because it uses bare virtual machines and shuts down unused virtual machines automatically.

- **No vendor lock-in**: Choose whatever cloud provider suits you best, be it the cheapest one or the most powerful, DevPod supports all cloud providers. If you are tired of using a provider, change it with a single command.

- **Local development**: You get the same developer experience also locally, so you don&#x27;t need to rely on a cloud provider at all.

- **Cross IDE support**: VS Code and the full JetBrains suite is supported, all others can be connected through simple SSH.

- **Client-only**: No need to install a server backend, DevPod runs solely on your computer.

- **Open-Source**: DevPod is 100% open-source and extensible. A provider doesn&#x27;t exist? Just create your own.

- **Rich feature set**: DevPod already supports prebuilds, auto inactivity shutdown, git & docker credentials sync and many more features to come.

- **Desktop App**: DevPod comes with an easy-to-use desktop application that abstracts all the complexity away. If you want to build your own integration, DevPod offers a feature-rich CLI as well.

[Edit this page](https://github.com/loft-sh/devpod/edit/main/docs/pages/what-is-devpod.mdx)