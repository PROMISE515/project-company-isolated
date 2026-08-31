---
name: project-company-isolated
description: "Launch and operate one isolated CEO-led project company per project, with dedicated project memory and discovery, delivery, and assurance Terra-Luna functional teams. Use only when the user explicitly invokes $project-company-isolated or asks for a dedicated CEO and functional teams for one substantial project; do not use for small tasks or portfolio-style shared-CEO project management."
---

# Isolated Project Company

Use this mode when each project needs its own CEO context, decisions, and memory. `sol_project_ceo` is a role template; create a separate CEO task or thread for each project and never reuse that instance for another project.

## Start an isolated project

1. Ask for the project id, project root, and retention period; default retention is 30 days.
2. Run `scripts/isolated_project_memory.py init` with the memory root `~/.codex/project-memory-isolated`, project id, project root, and retention period.
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

## Archive countdown

At initialization, record the configured archive due date. Create one daily project-specific heartbeat automation when available:

- Run `scripts/isolated_project_memory.py due --mark-notified` against the project memory root.
- On a due project, notify the user and ask whether to extend or archive it. Extend with `extend --project-id <id> --days <n>`.
- Archive only after user confirmation with `archive --project-id <id> --confirm`.

If automations are unavailable, state the due date in the primary memory and do not claim it is monitored.
