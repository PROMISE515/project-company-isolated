"""End-to-end coverage for isolated project memory lifecycle."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
TOOL = REPOSITORY / ".agents" / "skills" / "project-company-isolated" / "scripts" / "isolated_project_memory.py"


class IsolatedProjectMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary_directory.name)
        self.memory_root = self.base / "memory"
        self.project_root = self.base / "workspace"
        self.project_root.mkdir()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_tool(self, *arguments, expected_returncode=0):
        result = subprocess.run(
            [sys.executable, str(TOOL), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, expected_returncode, result.stderr)
        return result

    def test_create_status_extend_and_archive(self):
        created = json.loads(
            self.run_tool(
                "init",
                "--memory-root",
                str(self.memory_root),
                "--project-id",
                "billing-redesign",
                "--project-root",
                str(self.project_root),
                "--retention-days",
                "30",
            ).stdout
        )
        self.assertEqual(created["ceo"]["instance_id"], "sol_project_ceo:billing-redesign")
        self.assertEqual([team["function"] for team in created["functional_teams"]], ["discovery", "delivery", "assurance"])

        status = json.loads(self.run_tool("status", "--memory-root", str(self.memory_root)).stdout)
        self.assertEqual(status["active_projects"][0]["project_id"], "billing-redesign")

        self.run_tool(
            "extend",
            "--memory-root",
            str(self.memory_root),
            "--project-id",
            "billing-redesign",
            "--days",
            "7",
        )
        self.run_tool(
            "archive",
            "--memory-root",
            str(self.memory_root),
            "--project-id",
            "billing-redesign",
            expected_returncode=2,
        )
        archived = json.loads(
            self.run_tool(
                "archive",
                "--memory-root",
                str(self.memory_root),
                "--project-id",
                "billing-redesign",
                "--confirm",
            ).stdout
        )
        self.assertTrue(Path(archived["archive_path"]).joinpath("PROJECT_MEMORY.md").is_file())


if __name__ == "__main__":
    unittest.main()
