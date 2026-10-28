# Linka

**Linka** is an open-source decentralized social network focused on freedom, compatibility and customization.

Unlike traditional social platforms, Linka allows anyone to host their own server, create custom clients, modify algorithms and adapt the platform for different devices — from modern desktops to legacy hardware and lightweight systems.

> Connect through any device, any client, any server.

---

# Features

- Decentralized servers
- Open-source backend
- Lightweight architecture
- Customizable algorithms
- External client support
- SDK for bots and integrations
- Legacy device compatibility
- Desktop client
- Android client (LinkaLite)
- Designed for low-resource hardware

---

# Linka Ecosystem

## Linka
Main decentralized social platform. 
*(Backend built with: ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat&logo=sqlite&logoColor=white))*

## LinkaLite
Ultra-light Android client focused on:
- old Android devices
- low RAM usage
- lightweight WebView rendering
- legacy compatibility

## Linka Qt
Desktop multi-platform client using C++ and Qt:
*(Built with: ![C++](https://img.shields.io/badge/C++-00599C?style=flat&logo=c%2B%2B&logoColor=white) ![Qt](https://img.shields.io/badge/Qt-41CD52?style=flat&logo=qt&logoColor=white))*
- Windows
- Linux
- macOS
- Android

## LinkaSDK
SDK for:
- bots
- custom clients
- integrations
- automation

---

# Philosophy

Linka was created with one main idea:

> Social networks should not depend on a single company, platform or device.

The project focuses on:
- openness
- modularity
- accessibility
- compatibility
- simplicity

---

# Development setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
git clone https://github.com/luizgustavo76/Linka.git
cd Linka
uv sync --all-packages --frozen
uv run linka-backend
```

The API runs at `http://127.0.0.1:5000`; check `/meta` to confirm startup.
Python 3.12 is selected automatically. SQLite state is created in `apps/backend/DB`.
Optional configuration starts with `apps/backend/backend.env.example`.

Applications live under `apps/backend` and `apps/linka_lite`; Python SDKs and bots live under `packages` in a shared uv workspace. AutoModerator still starts automatically when configured. Android uses its own Gradle build.

See [CONTRIBUTING.md](CONTRIBUTING.md) for package boundaries, configuration, bot setup, local-state migration, Android development and checks.

---

# Project Status

Linka is currently under active development.

Current focus:
- stability
- security
- messaging system
- notifications
- lightweight clients
- SDK improvements

---

# Roadmap

- [x] Authentication system
- [x] Notifications
- [x] Messaging system
- [x] Lightweight Android client
- [ ] Groups
- [ ] Better feed design
- [ ] Media upload system
- [ ] Advanced SDK

---

# Contributing

Anyone can contribute to Linka.

Ideas, pull requests, forks and custom clients are welcome.

---

# Official Links

## Repository
https://github.com/luizgustavo76/Linka

## Documentation
https://luizgustavo76.github.io/Linka/documentation/docs.html

---

# Author

Luiz Gustavo

Backend and desktop developer focused on lightweight and multi-platform systems.

---

# License

This project is open-source.
read the LICENSE.txt, is a AGpl-3.0
