#!/usr/bin/env python3
"""Create and retain durable memory for isolated CEO-led projects."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


FUNCTIONAL_TEAMS = (
    {
        "function": "discovery",
        "lead_profile": "terra_discovery",
        "executor_profile": "luna_researcher",
        "responsibility": "problem framing, research, options, and decision criteria",
    },
    {
        "function": "delivery",
        "lead_profile": "terra_delivery",
        "executor_profile": "luna_builder",
        "responsibility": "implementation planning, focused delivery, and integration evidence",
    },
    {
        "function": "assurance",
        "lead_profile": "terra_assurance",
        "executor_profile": "luna_verifier",
        "responsibility": "independent verification, risk assessment, and release readiness",
    },
)


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def timestamp(value):
    return value.isoformat().replace("+00:00", "Z")


def project_id(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value):
        raise argparse.ArgumentTypeError("use lowercase letters, digits, and hyphens")
    return value


def memory_root(value):
    return Path(value).expanduser().resolve()


def active_root(root):
    return root / "active"


def manifest_path(root, identifier):
    return active_root(root) / identifier / "manifest.json"


def read_manifest(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"unknown project: {path.parent.name}")
    except json.JSONDecodeError as error:
        fail(f"invalid manifest at {path}: {error}")


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def project_manifests(root, active_only=False):
    manifests = []
    for path in sorted(active_root(root).glob("*/manifest.json")):
        manifest = read_manifest(path)
        if not active_only or manifest.get("state") == "active":
            manifests.append((path, manifest))
    return manifests


def working_memory(manifest):
    teams = "\n".join(
        f"- {team['function'].title()}: {team['lead_profile']} + {team['executor_profile']} — {team['responsibility']}"
        for team in manifest["functional_teams"]
    )
    return f"""# Isolated Project Memory: {manifest['project_id']}

This is a permanent project record. It has no expiry date and is never moved, archived, or deleted automatically.

## Project charter

Record the user goal, measurable success criteria, and scope boundaries.

## Dedicated CEO ownership

- Agent profile: {manifest['ceo']['agent_profile']}
- Project CEO instance: {manifest['ceo']['instance_id']}
- Project root: {manifest['project_root']}
- Started: {manifest['started_at']}

The CEO owns project-level decisions and this primary memory. Do not reuse this CEO instance for another project.

## Functional teams

{teams}

## Current state

Record the phase, active functional teams, work packages, and blockers.

## CEO decision ledger

Append material decisions with date, evidence, alternatives, risk, owner, and rationale.

## Team reports

Summarize reviewed reports from Discovery, Delivery, and Assurance. Retain source links, changed files, test results, and known limitations.

## Handoffs and assistance

Record explicit user-approved CEO handovers. Other projects and teams may assist only through bounded work; they do not inherit ownership.

## Resume brief

Keep the next CEO session concise: what to read first, what is verified, unresolved questions, and the next safe action.
"""


def command_init(args):
    root = args.memory_root
    active_root(root).mkdir(parents=True, exist_ok=True)
    active_dir = active_root(root) / args.project_id
    if active_dir.exists():
        fail(f"project id already exists: {args.project_id}")

    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.is_dir():
        fail(f"project root is not a directory: {project_root}")
    manifest = {
        "schema_version": 2,
        "project_id": args.project_id,
        "project_root": str(project_root),
        "ceo": {
            "agent_profile": "sol_project_ceo",
            "instance_id": args.ceo_instance_id or f"sol_project_ceo:{args.project_id}",
            "ownership": "project-level direction, phase gates, and primary memory",
        },
        "functional_teams": list(FUNCTIONAL_TEAMS),
        "started_at": timestamp(datetime.now(timezone.utc)),
        "state": "active",
    }
    active_dir.mkdir(parents=True)
    write_json(active_dir / "manifest.json", manifest)
    (active_dir / "WORKING_MEMORY.md").write_text(working_memory(manifest), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def command_status(args):
    projects = []
    for path, manifest in project_manifests(args.memory_root):
        projects.append(
            {
                "project_id": manifest["project_id"],
                "state": manifest.get("state"),
                "ceo_instance_id": manifest["ceo"]["instance_id"],
                "project_root": manifest["project_root"],
                "working_memory": str(path.parent / "WORKING_MEMORY.md"),
                "functional_teams": [team["function"] for team in manifest["functional_teams"]],
            }
        )
    print(json.dumps({"projects": projects}, indent=2))


def command_complete(args):
    path = manifest_path(args.memory_root, args.project_id)
    manifest = read_manifest(path)
    if manifest.get("state") != "active":
        fail(f"project is not active: {args.project_id}")
    manifest["state"] = "completed"
    manifest["completed_at"] = timestamp(datetime.now(timezone.utc))
    write_json(path, manifest)
    print(json.dumps({
        "project_id": args.project_id,
        "state": "completed",
        "working_memory": str(path.parent / "WORKING_MEMORY.md"),
        "memory_retained": True,
    }, indent=2))


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--memory-root", type=memory_root, default=memory_root("~/.codex/project-memory-isolated"))
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", parents=[common])
    init.add_argument("--project-id", type=project_id, required=True)
    init.add_argument("--project-root", required=True)
    init.add_argument("--ceo-instance-id")
    init.set_defaults(handler=command_init)

    status = commands.add_parser("status", parents=[common])
    status.set_defaults(handler=command_status)

    complete = commands.add_parser("complete", parents=[common])
    complete.add_argument("--project-id", type=project_id, required=True)
    complete.set_defaults(handler=command_complete)
    return parser


def main():
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
