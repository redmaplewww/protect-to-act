import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "protect-to-act" / "scripts" / "init_project_management.py"
EXPECTED_FILES = {
    "PROJECT_OVERVIEW.md",
    "PROJECT_PROGRESS.md",
    "PROJECT_VERSIONS.md",
    "PROJECT_FEATURES.md",
    "PROJECT_ACCEPTANCE.md",
}


def load_module():
    spec = importlib.util.spec_from_file_location("init_project_management", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载初始化脚本：{SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InitializeProjectManagementTests(unittest.TestCase):
    def test_creates_five_templates_in_empty_project(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = module.initialize(root)
            management_dir = root / ".protect-to-act"

            self.assertEqual(set(result["created"]), EXPECTED_FILES)
            self.assertEqual(result["skipped"], [])
            self.assertEqual({path.name for path in management_dir.iterdir()}, EXPECTED_FILES)
            for filename in EXPECTED_FILES:
                self.assertTrue((management_dir / filename).read_text(encoding="utf-8").startswith("# "))

    def test_second_run_preserves_existing_content(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            module.initialize(root)
            overview = root / ".protect-to-act" / "PROJECT_OVERVIEW.md"
            overview.write_text("用户自定义内容\n", encoding="utf-8")

            result = module.initialize(root)

            self.assertEqual(result["created"], [])
            self.assertEqual(set(result["skipped"]), EXPECTED_FILES)
            self.assertEqual(overview.read_text(encoding="utf-8"), "用户自定义内容\n")

    def test_partial_directory_only_adds_missing_files(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            management_dir = root / ".protect-to-act"
            management_dir.mkdir()
            existing = management_dir / "PROJECT_PROGRESS.md"
            existing.write_text("保留此内容\n", encoding="utf-8")

            result = module.initialize(root)

            self.assertEqual(set(result["created"]), EXPECTED_FILES - {"PROJECT_PROGRESS.md"})
            self.assertEqual(result["skipped"], ["PROJECT_PROGRESS.md"])
            self.assertEqual(existing.read_text(encoding="utf-8"), "保留此内容\n")

    def test_rejects_file_as_project_root(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            project_file = Path(temp_dir) / "not-a-directory"
            project_file.write_text("x", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "项目根路径不是目录"):
                module.initialize(project_file)


if __name__ == "__main__":
    unittest.main()
