# Isolated Project Company

A Codex adapter for treating each substantial project as its own agent company: one dedicated Sol CEO instance, one durable project memory, and functional Terra-Luna teams for discovery, delivery, and assurance.

This is intentionally separate from portfolio-style `project-company`. It does not share a CEO or primary memory across projects.

## Install

```bash
mkdir -p "$HOME/.codex/agents" "$HOME/.agents/skills"
for agent in "$PWD"/.codex/agents/*.toml; do
  ln -s "$agent" "$HOME/.codex/agents/"
done
ln -s "$PWD/.agents/skills/project-company-isolated" "$HOME/.agents/skills/project-company-isolated"
```

Restart Codex if necessary, then invoke:

```text
Use $project-company-isolated to start `project-id` in /path/to/project-root with a 30-day retention window.
```

## Functional structure

```text
Dedicated project CEO (Sol)
├── Discovery: Terra + Luna research
├── Delivery: Terra + Luna implementation
└── Assurance: Terra + Luna verification
```

The CEO activates only the functions needed by the project and remains accountable for project-level decisions and primary memory.

## License

MIT. See [LICENSE](LICENSE).
