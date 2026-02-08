# Contracts — Rust A* Core

- **astar.openapi.yaml** — OpenAPI 3.1 definition that mirrors the CLI/Python operations. `POST /astar/v1/find-path` represents the tuple-returning API, while `POST /astar/v1/profile` captures viztracer workflow steps.

> These contracts provide a stable schema for external orchestration (automation, services) even though the current implementation is a CLI + Python package.
