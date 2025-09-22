"""Documentation structure regression tests."""

from pathlib import Path

from django.test import SimpleTestCase

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT_DIR / "docs"


class DocumentationStructureTest(SimpleTestCase):
    def test_docs_index_lists_primary_sections(self) -> None:
        index_path = DOCS_DIR / "index.md"
        self.assertTrue(index_path.exists(), "docs/index.md 파일이 존재해야 합니다.")

        content = index_path.read_text(encoding="utf-8")
        for heading in ("## Guides", "## Operations", "## Process", "## Architecture"):
            self.assertIn(
                heading,
                content,
                msg=f"index.md에 '{heading}' 섹션이 포함되어야 합니다.",
            )

        for link in (
            "guides/admin.md",
            "guides/user.md",
            "operations/environment.md",
            "operations/deployment.md",
            "operations/production_docker.md",
            "process/contributing.md",
            "process/testing_strategy.md",
            "architecture/prd.md",
            "architecture/architecture_decisions.md",
        ):
            self.assertIn(
                link,
                content,
                msg=f"index.md에 '{link}' 링크가 있어야 합니다.",
            )

    def test_docs_primary_directories_exist(self) -> None:
        for folder in ("guides", "operations", "process", "architecture"):
            path = DOCS_DIR / folder
            self.assertTrue(path.is_dir(), f"docs/{folder} 디렉터리가 존재해야 합니다.")

    def test_expected_documents_present(self) -> None:
        expected_files = {
            "guides": {"admin.md", "user.md"},
            "operations": {
                "environment.md",
                "deployment.md",
                "production_docker.md",
            },
            "process": {"contributing.md", "testing_strategy.md"},
            "architecture": {"prd.md", "architecture_decisions.md"},
        }

        for folder, files in expected_files.items():
            for filename in files:
                file_path = DOCS_DIR / folder / filename
                self.assertTrue(
                    file_path.exists(),
                    msg=f"docs/{folder}/{filename} 파일이 존재해야 합니다.",
                )
