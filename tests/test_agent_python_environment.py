"""Regression checks for the documented project-local agent Python setup."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MISE = shutil.which("mise")


@unittest.skipUnless(MISE, "mise is required for agent Python environment tests")
class AgentPythonEnvironmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="agent-python-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "project"
        self.project.mkdir()
        shutil.copy2(ROOT / "mise.toml", self.project / "mise.toml")
        shutil.copy2(ROOT / "requirements-agent.txt", self.project / "requirements-agent.txt")
        self.env = os.environ.copy()
        self.env["MISE_CONFIG_DIR"] = str(self.base / "mise-config")
        self.env["MISE_STATE_DIR"] = str(self.base / "mise-state")
        self.env["MISE_CACHE_DIR"] = str(self.base / "mise-cache")
        self.env["UV_CACHE_DIR"] = str(self.base / "uv-cache")

    def run_mise(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [MISE or "mise", *args],
            cwd=self.project,
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_prepare_creates_pinned_environment_and_explicit_invocation_uses_it(self) -> None:
        prepared = self.run_mise("run", "python:prepare")
        self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)

        for command in ("python", "python3"):
            with self.subTest(command=command):
                invocation = self.run_mise(
                    "exec",
                    "--",
                    command,
                    "-c",
                    "import sys, yaml; print(sys.executable); print(sys.prefix); print(sys.version.split()[0]); print(yaml.__version__)",
                )
                self.assertEqual(invocation.returncode, 0, invocation.stdout + invocation.stderr)
                lines = invocation.stdout.strip().splitlines()
                self.assertIn(str(self.project / ".venv" / "bin" / command), lines[0])
                self.assertEqual(str((self.project / ".venv").resolve()), str(Path(lines[1]).resolve()))
                self.assertEqual("3.11.16", lines[2])
                self.assertEqual("6.0.3", lines[3])

    def test_existing_path_is_preserved_and_reported(self) -> None:
        environment = self.project / ".venv"
        environment.mkdir()
        sentinel = environment / "operator-owned.txt"
        sentinel.write_text("preserve this environment\n", encoding="utf-8")

        result = self.run_mise("run", "python:prepare")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("existing .venv is incomplete or incompatible", result.stderr)
        self.assertEqual("preserve this environment\n", sentinel.read_text(encoding="utf-8"))
        self.assertEqual([sentinel], list(environment.iterdir()))


if __name__ == "__main__":
    unittest.main()
