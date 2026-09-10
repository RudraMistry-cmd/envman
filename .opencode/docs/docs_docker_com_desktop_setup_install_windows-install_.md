# Install Docker Desktop on Windows | Docker Docs

> Source: https://docs.docker.com/desktop/setup/install/windows-install/
> Cached: 2026-09-10T08:35:05.816Z

---

Home
/
Manuals
/
Docker Desktop
/
Setup
/
Install
/
Windows# Install Docker Desktop on Windows

Ask Gordon

Copy Markdown

View MarkdownTable of contents
- Installation modes
- System requirements
- Install Docker Desktop on Windows

- Install interactively
- Install from the command line

- Start Docker Desktop
- Advanced system configuration and installation options

- WSL: Verification and setup

- Installer flags

- Administrator privileges
- Windows containers

- Where to go next

> **Docker Desktop terms**

Commercial use of Docker Desktop in larger enterprises (more than 250
employees OR more than $10 million USD in annual revenue) requires a paid
subscription.

This page provides download links, system requirements, and step-by-step installation instructions for Docker Desktop on Windows.

[Docker Desktop for Windows - x86_64](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-win-amd64)
[Docker Desktop for Windows - x86_64 on the Microsoft Store](https://apps.microsoft.com/detail/xp8cbj40xlbwkx?hl=en-GB&gl=GB)
[Docker Desktop for Windows - Arm (Early Access)](https://desktop.docker.com/win/main/arm64/Docker%20Desktop%20Installer.exe?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-win-arm64)For checksums, see
Release notes## Installation modes

Docker Desktop supports two installation modes. Per-user installation is recommended for most users and is selected by default in the installer. It does not require administrator privileges to install or update, and the WSL 2 backend it uses covers the needs of the vast majority of Docker Desktop users.

Per-user (recommended)All usersInstall location`%LOCALAPPDATA%\Programs\DockerDesktop``C:\Program Files\Docker\Docker`Registry keysCurrent User (HKCU)Local Machine (HKLM)Admin rights to installNot requiredRequiredAdmin rights to updateNot requiredRequiredLinux containers backendWSL 2 or Docker VMMWSL 2, Hyper-V, or Docker VMMWindows containersNot supportedSupportedSecuritySmaller attack surface; no privileged system service installedRequires privileged system service; broader access to host resourcesFor more information, see Understand permission requirements for Windows.

## System requirements

> 
Tip**Which backend should I use?**

Docker Desktop for Windows supports three backends: WSL 2, Hyper-V, and Docker VMM (Beta). WSL 2 is the default and works for most users without administrator privileges. Hyper-V is only available with all-users installation. Docker VMM is a container-optimized hypervisor that reclaims idle memory and improves file I/O. For more information, see
Virtual Machine Manager.

WSL 2 backend, x86_64

Hyper-V backend, x86_64

WSL 2 backend, Arm (Early Access)
- WSL version 2.1.5 or later. To check your version, see WSL: Verification and setup
- If you intend to use Enhanced Container Isolation, ensure you’re using WSL version 2.6 or later. This is required because ECI depends on a Linux kernel version of at least 6.3.0, and WSL 2.6+ bundles Linux kernel version 6.6.
- Windows 10 64-bit: Enterprise, Pro, or Education version 22H2 (build 19045).
- Windows 11 64-bit: Enterprise, Pro, or Education version 23H2 (build 22631) or higher.
- The Windows Server service (LanmanServer) must be enabled and its start mode set to **Automatic**.
Turn on the WSL 2 feature on Windows. For detailed instructions, refer to the
Microsoft documentation.The following hardware prerequisites are required to successfully run
WSL 2 on Windows 10 or Windows 11:
- 64-bit processor with Second Level Address Translation (SLAT)
- 8GB system RAM
Enable hardware virtualization in BIOS/UEFI. For more information, see
Virtualization.

For more information on setting up WSL 2 with Docker Desktop, see
WSL.> 
NoteDocker only supports Docker Desktop on Windows for those versions of Windows that are still within Microsoft’s servicing timeline. Docker Desktop is not supported on server versions of Windows, such as Windows Server 2019 or Windows Server 2022. For more information on how to run containers on Windows Server, see Microsoft's official documentation.

> 
ImportantTo run Windows containers, you need Windows 10 or Windows 11 Professional or Enterprise edition.
Windows Home or Education editions only allow you to run Linux containers.

Windows 10 64-bit: Enterprise, Pro, or Education version 22H2 (build 19045).

Windows 11 64-bit: Enterprise, Pro, or Education version 23H2 (build 22631) or higher.

The Windows Server service (LanmanServer) must be enabled and its start mode set to **Automatic**.

Turn on Hyper-V and Containers Windows features.

The following hardware prerequisites are required to successfully run Client
Hyper-V on Windows 10:
- 64 bit processor with Second Level Address Translation (SLAT)
- 8GB system RAM
Turn on BIOS/UEFI-level hardware virtualization support in the
BIOS/UEFI settings. For more information, see
Virtualization.

> 
NoteDocker only supports Docker Desktop on Windows for those versions of Windows that are still within Microsoft’s servicing timeline. Docker Desktop is not supported on server versions of Windows, such as Windows Server 2019 or Windows Server 2022. For more information on how to run containers on Windows Server, see Microsoft's official documentation.

> 
ImportantTo run Windows containers, you need Windows 10 or Windows 11 Professional or Enterprise edition.
Windows Home or Education editions only allow you to run Linux containers.

- WSL version 2.1.5 or later. To check your version, see WSL: Verification and setup
- Windows 10 64-bit: Enterprise, Pro, or Education version 22H2 (build 19045).
- Windows 11 64-bit: Enterprise, Pro, or Education version 23H2 (build 22631) or higher.
- The Windows Server service (LanmanServer) must be enabled and its start mode set to **Automatic**.
Turn on the WSL 2 feature on Windows. For detailed instructions, refer to the
Microsoft documentation.The following hardware prerequisites are required to successfully run
WSL 2 on Windows 10 or Windows 11:
- 64-bit processor with Second Level Address Translation (SLAT)
- 8GB system RAM
Enable hardware virtualization in BIOS/UEFI. For more information, see
Virtualization.

> 
ImportantWindows containers are not supported.

Containers and images created with Docker Desktop are shared between all
user accounts on machines where it is installed. This is because all Windows
accounts use the same VM to build and run containers. Note that it is not possible to share containers and images between user accounts when using the Docker Desktop WSL 2 backend.Running Docker Desktop inside a VMware ESXi or Azure VM is supported for Docker Business customers.
It requires enabling nested virtualization on the hypervisor first.
For more information, see
Running Docker Desktop in a VM or VDI environment.## Install Docker Desktop on Windows

### Install interactively

Download the installer using the download button at the top of the page, or from the
release notes.Double-click `Docker Desktop Installer.exe` to run the installer. The installer will ask which installation mode you prefer. Choosing per-user installs to `%LOCALAPPDATA%\Programs\DockerDesktop` and requires no administrator privileges. Choosing all users will prompt for elevation.

> 
NoteIf you want to switch installation mode at a later date, you need to uninstall and reinstall Docker Desktop.

When prompted, select your backend on the Configuration page: **Use WSL 2 instead of Hyper-V** for WSL 2, or leave it unselected for Hyper-V. You can switch to Docker VMM after installation from **Settings** > **General**.

On systems that support only one backend, Docker Desktop automatically selects the available option.

Follow the instructions on the installation wizard to authorize the installer and proceed with the installation.

When the installation is successful, select **Close** to complete the installation process.

Start Docker Desktop.

### Install from the command line

After downloading `Docker Desktop Installer.exe`, run the following command in a terminal to install Docker Desktop to `%LOCALAPPDATA%\Programs\DockerDesktop`.

For per-user installation, run:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ &#34;Docker Desktop Installer.exe&#34; install --user

```

To install for all users on the machine (requires administrator privileges):

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ &#34;Docker Desktop Installer.exe&#34; install

```

If you're using PowerShell you should run it as:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
# Per-user installation (no admin required)
Start-Process 'Docker Desktop Installer.exe' -Wait -ArgumentList 'install', '--user'
 
# All-users installation (run as administrator)
Start-Process 'Docker Desktop Installer.exe' -Wait install
```

If using the Windows Command Prompt:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
# Per-user installation (no admin required)
start /w &#34;&#34; &#34;Docker Desktop Installer.exe&#34; install --user
 
# All-users installation (run as administrator)
start /w &#34;&#34; &#34;Docker Desktop Installer.exe&#34; install
```

If using all-users installation and your administrator account is different to your user account, you must add the user to the **docker-users** group to access features that require higher privileges, such as creating and managing the Hyper-V VM, or using Windows containers:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
$ net localgroup docker-users <user> /add

```

> 
WarningMembership in `docker-users` grants access to the Docker daemon socket, which is equivalent to granting administrative privileges on the host. Only add users who require access to Windows containers or Hyper-V VM management. For Linux containers using the WSL 2 backend, this group membership is not required. See
Protect the Docker daemon socket for more information.

If you're deploying via MDM (such as Intune) and the `docker-users` group isn't populated automatically, see
Why isn't the `docker-users` group populated when the MSI is installed with Intune or another MDM solution?.See the Installer flags section to see what flags the `install` command accepts.

> 
NoteIf you want to switch installation mode at a later date, you need to uninstall and reinstall Docker Desktop.

## Start Docker Desktop

Docker Desktop does not start automatically after installation. To start Docker Desktop:

Search for Docker, and select **Docker Desktop** in the search results.

The Docker menu (

) displays the Docker Subscription Service Agreement.Here’s a summary of the key points:

- Docker Desktop is free for small businesses (fewer than 250 employees AND less than $10 million in annual revenue), personal use, education, and non-commercial open source projects.
- Otherwise, it requires a paid subscription for professional use.
- Paid subscriptions are also required for government entities.
- The Docker Pro, Team, and Business subscriptions include commercial use of Docker Desktop.

Select **Accept** to continue. Docker Desktop starts after you accept the terms.

Note that Docker Desktop won't run if you do not agree to the terms. You can choose to accept the terms at a later date by opening Docker Desktop.

For more information, see Docker Desktop Subscription Service Agreement. It is recommended that you read the FAQs.

> 
TipAs an IT administrator, you can use endpoint management (MDM) software to identify the number of Docker Desktop instances and their versions within your environment. This can provide accurate license reporting, help ensure your machines use the latest version of Docker Desktop, and enable you to
enforce sign-in.
- Intune
- Jamf
- Kandji
- Kolide
- Workspace One

## Advanced system configuration and installation options

### WSL: Verification and setup

If you have chosen to use WSL, first verify that your installed version meets system requirements by running the following command in your terminal:

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
wsl --version

```

If version details do not appear, you are likely using the inbox version of WSL. This version does not support modern capabilities and must be updated.

You can update or install WSL using one of the following methods:

#### Option 1: Install or update WSL via the terminal

- Open PowerShell or Windows Command Prompt in administrator mode.
- Run either the install or update command. You may be prompted to restart your machine. For more information, refer to Install WSL.

]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
wsl --install

wsl --update

```

#### Option 2: Install WSL via the MSI package

If Microsoft Store access is blocked due to security policies:

- Go to the official WSL GitHub Releases page.
- Download the `.msi` installer from the latest stable release (under the Assets drop-down).
- Run the downloaded installer and follow the setup instructions.

### Installer flags

> 
NoteIf you're using PowerShell, you need to use the `ArgumentList` parameter before any flags.
For example:]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);">

```
Start-Process 'Docker Desktop Installer.exe' -Wait -ArgumentList 'install', '--accept-license'
```

#### Installation behavior

- `--user`: Installs Docker Desktop in per-user mode, to `%LOCALAPPDATA%\Programs\DockerDesktop`. No administrator privileges are required. This is the recommended mode for most users. See Installation modes.
- `--quiet`: Suppresses information output when running the installer
- `--accept-license`: Accepts the Docker Subscription Service Agreement now, rather than requiring it to be accepted when the application is first run
- `--installation-dir=<path>`: Changes the default installation location (`C:\Program Files\Docker\Docker`)
- `--backend=<backend name>`: Selects the default backend to use for Docker Desktop, `hyper-v`, `windows` or `wsl-2` (default)
- `--always-run-service`: After installation completes, starts `com.docker.service` and sets the service startup type to Automatic. This circumvents the need for administrator privileges, which are otherwise necessary to start `com.docker.service`. `com.docker.service` is required by Windows containers and Hyper-V backend.

#### Security and access control

- `--allowed-org=<org name>`: Requires the user to sign in and be part of the specified Docker Hub organization when running the application
`--admin-settings`: Automatically creates an `admin-settings.json` file which is used by admins to control certain Docker Desktop settings on client machines within their organization. For more info

... [Content truncated]