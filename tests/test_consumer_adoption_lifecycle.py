"""Preservation checks for consumer-owned files across FarmBoy skill lifecycle."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools import catalog


class ConsumerAdoptionLifecycleTests(unittest.TestCase):
    def test_installRefreshRemove_preservesGuidanceGovernanceReviewAndUnrelatedFiles(self) -> None:
        with tempfile.TemporaryDirectory(prefix="consumer-adoption-lifecycle-") as temporary:
            consumer = Path(temporary)
            owned_files = {
                consumer / "AGENTS.md": "# Consumer instructions\nKeep project-owned guidance.\n",
                consumer / ".specify/memory/constitution.md": "# Consumer constitution\nExisting rules.\n",
                consumer / "specs/example/adoption-review.md": "# Prior adoption review\nLocal evidence.\n",
                consumer / "unrelated/README.md": "Unrelated consumer content.\n",
            }
            for path, contents in owned_files.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(contents, encoding="utf-8")
            before = {path: catalog.digest(path) for path in owned_files}

            package = consumer / "controller-package.zip"
            catalog.package_controller(package)
            digest = catalog.digest(package)
            catalog.install_controller_package(consumer, package, refresh=False, source_digest=digest, catalog_status="snapshot")
            self.assertEqual(before, {path: catalog.digest(path) for path in owned_files})
            catalog.install_controller_package(consumer, package, refresh=True, source_digest=digest, catalog_status="snapshot")
            self.assertEqual(before, {path: catalog.digest(path) for path in owned_files})
            catalog.remove_controller_package(consumer)
            self.assertEqual(before, {path: catalog.digest(path) for path in owned_files})


if __name__ == "__main__":
    unittest.main()
