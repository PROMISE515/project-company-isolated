"""End-to-end coverage for isolated persistent project memory."""

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

    def test_create_status_and_complete_without_moving_memory(self):
        created = json.loads(self.run_tool(
            "init", "--memory-root", str(self.memory_root), "--project-id", "billing-redesign",
            "--project-root", str(self.project_root),
        ).stdout)
        self.assertEqual(created["ceo"]["instance_id"], "sol_project_ceo:billing-redesign")
        self.assertNotIn("archive_due_at", created)
        self.assertEqual([team["function"] for team in created["functional_teams"]], ["discovery", "delivery", "assurance"])

        status = json.loads(self.run_tool("status", "--memory-root", str(self.memory_root)).stdout)
        self.assertEqual(status["projects"][0]["state"], "active")

        completed = json.loads(self.run_tool(
            "complete", "--memory-root", str(self.memory_root), "--project-id", "billing-redesign"
        ).stdout)
        self.assertTrue(completed["memory_retained"])
        self.assertTrue(Path(completed["working_memory"]).is_file())
        status = json.loads(self.run_tool("status", "--memory-root", str(self.memory_root)).stdout)
        self.assertEqual(status["projects"][0]["state"], "completed")


if __name__ == "__main__":
    unittest.main()
