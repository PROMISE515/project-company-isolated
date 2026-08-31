---
name: project-company-isolated
description: "Launch and operate one isolated CEO-led project company per project, with permanent dedicated project memory and discovery, delivery, and assurance Terra-Luna functional teams. Use only when the user explicitly invokes $project-company-isolated or asks for a dedicated CEO and functional teams for one substantial project; do not use for small tasks or portfolio-style shared-CEO project management."
---

# Isolated Project Company

Use this mode when each project needs its own CEO context, decisions, and memory. `sol_project_ceo` is a role template; create a separate CEO task or thread for each project and never reuse that instance for another project.

## Start an isolated project

1. Ask for the project id and project root.
2. Run `scripts/isolated_project_memory.py init` with the memory root `~/.codex/project-memory-isolated`, project id, and project root.
3. Launch a dedicated `sol_project_ceo` task for that project. It owns the new `WORKING_MEMORY.md` and must read it before every phase gate.
4. Let the CEO activate functional teams only as needed:
   - Discovery: `terra_discovery` with `luna_researcher`
   - Delivery: `terra_delivery` with `luna_builder`
   - Assurance: `terra_assurance` with `luna_verifier`
5. Keep functional reports compact. The CEO records material decisions, evidence, ownership boundaries, and a resume brief in primary memory.

## Isolation and authority

- One project has one CEO instance, one primary memory record, and one decision ledger. Do not share them with another project.
- Functional Terra leads own their assigned workstream; paired Lunas are bounded executors. The CEO alone owns cross-functional decisions and the primary working memory.
- Do not launch all teams by default. Use parallel teams only when their work is independent and the speed benefit justifies the additional token cost.
- Do not transfer CEO or project ownership without an explicit user-approved handover recorded in primary memory.

## Permanent project memory

Project memory has no countdown, retention period, expiry date, scheduled check, automatic archive, or automatic deletion. Do not create an automation for project memory management.

When the user explicitly says the project is complete, run `scripts/isolated_project_memory.py complete --project-id <id>`. This changes only the project state; the CEO's `manifest.json` and `WORKING_MEMORY.md` remain in their existing directory for later continuation.
