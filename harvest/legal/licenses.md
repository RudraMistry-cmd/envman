# Legal & Licensing Summary (not legal advice; cites only)

## 1. Docker Desktop Subscription — binding threshold
- Source: https://docs.docker.com/desktop/setup/install/windows-install/ — Quote: "Commercial use in larger enterprises (more than 250 employees OR more than $10M revenue) requires paid subscription."
- Source: https://www.docker.com/pricing/faq/ — Quote: "restricted to <250 employees and <$10M revenue. Government Entities shall not use without purchasing."
- Plans (Dec 2024+): Pro ~$9/mo annual, Team ~$15/u/mo annual, Business + consumption (Build Cloud/Scout/Testcontainers). Personal free with 100 pulls/hr/user; unauth 10/hr/IP.
- EnvMan implication: enterprise rollout MUST NOT assume free Desktop. Support CE/WSL2, Rancher, Podman, Colima, OrbStack; add backend picker + `admin-settings.json` org guardrails.

## 2. Docker Engine / Moby — open
- Engine OSS via Moby (Apache-2.0). FAQ notes "open-source software such as Docker Engine is accessible for all." EnvMan subprocess against Engine/CLI carries no Desktop fee.

## 3. Image licensing — binding per-image
- Official images carry their own licenses (e.g., Postgres, MySQL, Redis source-available changes). Hub pulls subject to rate limits above. Always pin `image:tag@digest` + verify provenance; document DSOS exemption path for OSS.

## 4. Terms touched
- Docker Subscription Service Agreement acceptance on first Desktop start (must Accept or won't run).
- OrbStack/Colima/Podman: separate commercial terms (OrbStack proprietary; Colima MIT; Podman Apache-2.0; DevPod Apache-2.0).

## 5. Action checklist
1. Add license gate in installer (detect >250 emp flow → require subscription proof or alternate backend).
2. Default to Docker CE where possible; log backend + license mode.
3. Cache/mirror base images to avoid Hub throttle in CI.
