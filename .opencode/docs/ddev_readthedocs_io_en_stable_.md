# Get Started with DDEV - DDEV Docs

> Source: https://ddev.readthedocs.io/en/stable/
> Cached: 2026-09-10T08:35:26.551Z

---

# Get Started with DDEV[&para;](#get-started-with-ddev)

[DDEV](https://github.com/ddev/ddev) is an open source tool for launching local web development environments in minutes. It supports PHP and Node.js.

These environments can be extended, version controlled, and shared, so you can take advantage of a Docker workflow without Docker experience or bespoke configuration. Projects can be changed, powered down, or removed as easily as they’re started.

## System Requirements[&para;](#system-requirements)

macOSWindows WSL2Traditional WindowsLinuxGitHub Codespaces

### macOS[&para;](#macos)

Runs natively on ARM64 (Apple Silicon) and AMD64 machines.

- macOS Sonoma (14) or higher. This is primarily driven by the available Docker providers.

- RAM: 8GB

- Storage: 256GB

- [OrbStack](https://orbstack.dev/) or [Lima](https://github.com/lima-vm/lima) or [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Rancher Desktop](https://rancherdesktop.io/) or [Colima](https://github.com/abiosoft/colima)

**Next steps:**

*You’ll need a Docker provider on your system before you can install DDEV.*

- Install Docker with [recommended settings](users/install/docker-installation/#macos).

- Install [DDEV for macOS](users/install/ddev-installation/#macos).

- Launch your [first project](users/project/) and start developing. 🚀

### Windows WSL2[&para;](#windows-wsl2)

- RAM: 8GB

- Storage: 256GB

- [Docker CE](https://docs.docker.com/engine/install/ubuntu/) inside WSL2 or [Docker Desktop](https://www.docker.com/products/docker-desktop/) on the Windows side.

- Ubuntu or an Ubuntu-derived distro is recommended, though others may work fine

**Next steps:**

*You’ll need a Docker provider on your system before you can install DDEV.*

- Install [DDEV for Windows](users/install/ddev-installation/#windows).

- Launch your [first project](users/project/) and start developing. 🚀

**WSL2 in Mirrored Mode**

If you&rsquo;re using Windows WSL2 with [&ldquo;Mirrored&rdquo; networking mode](https://learn.microsoft.com/en-us/windows/wsl/networking#mirrored-mode-networking), enable the experimental `hostAddressLoopback=true` setting.

You can do this using the &ldquo;WSL Settings&rdquo; app:

- Networking > Networking mode: set to *Mirrored*

- Networking > Host Address Loopback: turn *On*.

Or by creating/editing the file at `C:\Users\<you>\.wslconfig`:

[](#__codelineno-0-1)[wsl2]
[](#__codelineno-0-2)networkingMode=Mirrored
[](#__codelineno-0-3)
[](#__codelineno-0-4)[experimental]
[](#__codelineno-0-5)hostAddressLoopback=true

**WSL2 in VirtioProxy Mode (Experimental)**

If you&rsquo;re using Windows WSL2 with [&ldquo;VirtioProxy&rdquo; networking mode](https://learn.microsoft.com/en-us/windows/wsl/networking), DDEV supports this mode experimentally. Set your `C:\Users\<you>\.wslconfig`:

[](#__codelineno-1-1)[wsl2]
[](#__codelineno-1-2)networkingMode=VirtioProxy

Then restart WSL with `wsl --shutdown`.

VirtioProxy mode is experimental with significant limitations

VirtioProxy mode has known limitations and is poorly documented by Microsoft. On some machines it works well; on others, the WSL2 distro has no internet access at all, making tools like Composer and npm non-functional.

When it does work: the WSL2 distro and Docker containers cannot make outgoing connections to the Windows host, so a Windows-side IDE cannot receive Xdebug connections. Run your IDE inside WSL2 via WSLg instead:

ddev config global --xdebug-ide-location=wsl2

Accessing DDEV sites from a Windows browser works normally. Run `ddev utility xdebug-diagnose` to check your Xdebug configuration.

If VirtioProxy is required due to a corporate VPN (such as Netskope), see [Special Network Configurations](users/usage/networking/#wsl2-virtioproxy-mode-netskope-and-similar-vpns). Users who can choose their setup may prefer the [Traditional Windows](#traditional-windows) approach instead.

### Traditional Windows[&para;](#traditional-windows)

- Any recent edition of Windows Home or Windows Pro.

- RAM: 8GB

- Storage: 256GB

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) using the WSL2 backend

**Next steps:**

*You’ll need a Docker provider on your system before you can install DDEV.*

- Install Docker with [recommended settings](users/install/docker-installation/#windows).

- Install [DDEV for Windows](users/install/ddev-installation/#windows).

- Launch your [first project](users/project/) and start developing. 🚀

### Linux[&para;](#linux)

Most distros and most versions work fine, on both AMD64 and ARM64 architectures.

- RAM: 8GB

- Storage: 256GB

**Next steps:**

*You’ll need a Docker provider on your system before you can install DDEV.*

- Install Docker with [recommended settings](users/install/docker-installation/#linux).

- Install [DDEV for Linux](users/install/ddev-installation/#linux).

- Launch your [first project](users/project/) and start developing. 🚀

### GitHub Codespaces[&para;](#github-codespaces)

With [GitHub Codespaces](https://github.com/features/codespaces) you don’t install anything; you only need a browser and an internet connection.

**Next steps:**

- Install DDEV within [GitHub Codespaces](users/install/ddev-installation/#github-codespaces).

- Launch your [first project](users/project/) and start developing. 🚀