#!/usr/bin/env python3
"""Create and maintain durable memory for isolated CEO-led projects."""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
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


def now_utc():
    return datetime.now(timezone.utc)


def timestamp(value):
    return value.isoformat().replace("+00:00", "Z")


def parse_timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def project_id(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value):
        raise argparse.ArgumentTypeError("use lowercase letters, digits, and hyphens")
    return value


def memory_root(value):
    return Path(value).expanduser().resolve()


def active_root(root):
    return root / "active"


def archive_root(root):
    return root / "archive"


def manifest_path(root, identifier):
    return active_root(root) / identifier / "manifest.json"


def read_manifest(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"unknown active project: {path.parent.name}")
    except json.JSONDecodeError as error:
        fail(f"invalid manifest at {path}: {error}")


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def active_manifests(root):
    manifests = []
    for path in sorted(active_root(root).glob("*/manifest.json")):
        manifest = read_manifest(path)
        if manifest.get("state") == "active":
            manifests.append((path, manifest))
    return manifests


def working_memory(manifest):
    teams = "\n".join(
        f"- {team['function'].title()}: {team['lead_profile']} + {team['executor_profile']} — {team['responsibility']}"
        for team in manifest["functional_teams"]
    )
    return f"""# Isolated Project Memory: {manifest['project_id']}

## Project charter

Record the user goal, measurable success criteria, scope boundaries, and retention choice.

## Dedicated CEO ownership

- Agent profile: {manifest['ceo']['agent_profile']}
- Project CEO instance: {manifest['ceo']['instance_id']}
- Project root: {manifest['project_root']}
- Started: {manifest['started_at']}
- Archive due: {manifest['archive_due_at']}

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
    archive_root(root).mkdir(parents=True, exist_ok=True)
    active_dir = active_root(root) / args.project_id
    if active_dir.exists() or (archive_root(root) / args.project_id).exists():
        fail(f"project id already exists: {args.project_id}")

    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.is_dir():
        fail(f"project root is not a directory: {project_root}")
    started = now_utc()
    manifest = {
        "schema_version": 1,
        "project_id": args.project_id,
        "project_root": str(project_root),
        "ceo": {
            "agent_profile": "sol_project_ceo",
            "instance_id": args.ceo_instance_id or f"sol_project_ceo:{args.project_id}",
            "ownership": "project-level direction, phase gates, and primary memory",
        },
        "functional_teams": list(FUNCTIONAL_TEAMS),
        "started_at": timestamp(started),
        "retention_days": args.retention_days,
        "archive_due_at": timestamp(started + timedelta(days=args.retention_days)),
        "state": "active",
        "archive_notice_sent_at": None,
    }
    active_dir.mkdir(parents=True)
    write_json(active_dir / "manifest.json", manifest)
    (active_dir / "WORKING_MEMORY.md").write_text(working_memory(manifest), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def command_status(args):
    active = []
    for _, manifest in active_manifests(args.memory_root):
        active.append(
            {
                "project_id": manifest["project_id"],
                "ceo_instance_id": manifest["ceo"]["instance_id"],
                "project_root": manifest["project_root"],
                "archive_due_at": manifest["archive_due_at"],
                "functional_teams": [team["function"] for team in manifest["functional_teams"]],
            }
        )
    print(json.dumps({"active_projects": active}, indent=2))


def command_due(args):
    current = now_utc()
    due_projects = []
    for path, manifest in active_manifests(args.memory_root):
        notified = manifest.get("archive_notice_sent_at") is not None
        if parse_timestamp(manifest["archive_due_at"]) <= current and (args.include_notified or not notified):
            due_projects.append(
                {
                    "project_id": manifest["project_id"],
                    "ceo_instance_id": manifest["ceo"]["instance_id"],
                    "archive_due_at": manifest["archive_due_at"],
                    "working_memory": str(path.parent / "WORKING_MEMORY.md"),
                }
            )
            if args.mark_notified and not notified:
                manifest["archive_notice_sent_at"] = timestamp(current)
                write_json(path, manifest)
    print(json.dumps({"due_projects": due_projects}, indent=2))


def command_extend(args):
    path = manifest_path(args.memory_root, args.project_id)
    manifest = read_manifest(path)
    if manifest.get("state") != "active":
        fail(f"project is not active: {args.project_id}")
    current = now_utc()
    previous_due = parse_timestamp(manifest["archive_due_at"])
    new_due = max(current, previous_due) + timedelta(days=args.days)
    manifest.setdefault("retention_extensions", []).append(
        {
            "extended_at": timestamp(current),
            "days": args.days,
            "previous_due_at": manifest["archive_due_at"],
            "new_due_at": timestamp(new_due),
        }
    )
    manifest["archive_due_at"] = timestamp(new_due)
    manifest["archive_notice_sent_at"] = None
    write_json(path, manifest)
    print(json.dumps(manifest, indent=2))


def command_archive(args):
    if not args.confirm:
        fail("archiving requires --confirm after the owner has been notified")
    active_dir = active_root(args.memory_root) / args.project_id
    active_manifest = active_dir / "manifest.json"
    manifest = read_manifest(active_manifest)
    if manifest.get("state") != "active":
        fail(f"project is not active: {args.project_id}")
    archive_dir = archive_root(args.memory_root) / args.project_id
    if archive_dir.exists():
        fail(f"archive already exists: {archive_dir}")

    working_file = active_dir / "WORKING_MEMORY.md"
    working_text = working_file.read_text(encoding="utf-8") if working_file.exists() else "No working memory file was found."
    archived_at = timestamp(now_utc())
    archive_dir.mkdir(parents=True)
    archive_text = f"""# Isolated Project Archive: {args.project_id}

## Archive record

- CEO instance: {manifest['ceo']['instance_id']}
- Original project root: {manifest['project_root']}
- Started: {manifest['started_at']}
- Retention window: {manifest['retention_days']} days
- Archive due: {manifest['archive_due_at']}
- Archived: {archived_at}

## Detailed primary memory

{working_text}
"""
    (archive_dir / "PROJECT_MEMORY.md").write_text(archive_text, encoding="utf-8")
    if working_file.exists():
        shutil.copy2(working_file, archive_dir / "WORKING_MEMORY.md")
    manifest["state"] = "archived"
    manifest["archived_at"] = archived_at
    manifest["archive_path"] = str(archive_dir)
    write_json(active_manifest, manifest)
    write_json(archive_dir / "manifest.json", manifest)
    print(json.dumps({"project_id": args.project_id, "archive_path": str(archive_dir)}, indent=2))


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--memory-root", type=memory_root, default=memory_root("~/.codex/project-memory-isolated"))
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", parents=[common])
    init.add_argument("--project-id", type=project_id, required=True)
    init.add_argument("--project-root", required=True)
    init.add_argument("--ceo-instance-id")
    init.add_argument("--retention-days", type=int, default=30)
    init.set_defaults(handler=command_init)

    status = commands.add_parser("status", parents=[common])
    status.set_defaults(handler=command_status)

    due = commands.add_parser("due", parents=[common])
    due.add_argument("--mark-notified", action="store_true")
    due.add_argument("--include-notified", action="store_true")
    due.set_defaults(handler=command_due)

    extend = commands.add_parser("extend", parents=[common])
    extend.add_argument("--project-id", type=project_id, required=True)
    extend.add_argument("--days", type=int, required=True)
    extend.set_defaults(handler=command_extend)

    archive = commands.add_parser("archive", parents=[common])
    archive.add_argument("--project-id", type=project_id, required=True)
    archive.add_argument("--confirm", action="store_true")
    archive.set_defaults(handler=command_archive)
    return parser


def main():
    args = build_parser().parse_args()
    if getattr(args, "retention_days", 30) < 1 or getattr(args, "days", 1) < 1:
        fail("retention and extension days must be at least 1")
    args.handler(args)


if __name__ == "__main__":
    main()
