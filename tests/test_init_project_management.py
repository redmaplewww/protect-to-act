import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "protect-to-act" / "scripts" / "init_project_management.py"
EXPECTED_FILES = (
    "PROJECT_OVERVIEW.md",
    "PROJECT_PROGRESS.md",
    "PROJECT_VERSIONS.md",
    "PROJECT_FEATURES.md",
    "PROJECT_ACCEPTANCE.md",
)


def load_module():
    spec = importlib.util.spec_from_file_location("init_project_management", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载初始化脚本：{SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cli(project_root: Path, script_path: Path = SCRIPT_PATH) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, str(script_path), "--project-root", str(project_root)],
        capture_output=True,
        check=False,
        encoding="utf-8",
        env=environment,
    )


def make_isolated_script(root: Path, missing_template: str | None = None) -> Path:
    skill_root = root / "protect-to-act"
    script_dir = skill_root / "scripts"
    template_dir = skill_root / "assets" / "templates"
    script_dir.mkdir(parents=True)
    template_dir.mkdir(parents=True)
    script_copy = script_dir / SCRIPT_PATH.name
    script_copy.write_bytes(SCRIPT_PATH.read_bytes())
    for filename in EXPECTED_FILES:
        if filename != missing_template:
            (template_dir / filename).write_text(f"# {filename}\n", encoding="utf-8")
    return script_copy


class InitializeProjectManagementTests(unittest.TestCase):
    def test_creates_five_templates_in_empty_project(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = module.initialize(root)
            management_dir = root / ".protect-to-act"

            self.assertEqual(result, {"created": list(EXPECTED_FILES), "skipped": []})
            self.assertEqual({path.name for path in management_dir.iterdir()}, set(EXPECTED_FILES))
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

            self.assertEqual(result, {"created": [], "skipped": list(EXPECTED_FILES)})
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

            self.assertEqual(
                result,
                {
                    "created": [name for name in EXPECTED_FILES if name != "PROJECT_PROGRESS.md"],
                    "skipped": ["PROJECT_PROGRESS.md"],
                },
            )
            self.assertEqual(existing.read_text(encoding="utf-8"), "保留此内容\n")

    def test_rejects_file_as_project_root(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            project_file = Path(temp_dir) / "not-a-directory"
            project_file.write_text("x", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "项目根路径不是目录"):
                module.initialize(project_file)

    def test_preflights_every_template_before_creating_management_directory(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script_path = make_isolated_script(root, missing_template="PROJECT_ACCEPTANCE.md")
            module.__file__ = str(script_path)
            project_root = root / "project"
            project_root.mkdir()

            with self.assertRaisesRegex(FileNotFoundError, "PROJECT_ACCEPTANCE.md"):
                module.initialize(project_root)

            self.assertFalse((project_root / ".protect-to-act").exists())

    def test_preflights_template_readability_before_project_mutation(self):
        module = load_module()
        original_open = Path.open

        def reject_acceptance_template(path, mode="r", *args, **kwargs):
            if path.name == "PROJECT_ACCEPTANCE.md" and mode == "rb":
                raise PermissionError("injected unreadable template")
            return original_open(path, mode, *args, **kwargs)

        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            Path, "open", reject_acceptance_template
        ):
            root = Path(temp_dir)
            with self.assertRaisesRegex(PermissionError, "injected unreadable template"):
                module.initialize(root)

            self.assertFalse((root / ".protect-to-act").exists())

    def test_rejects_management_path_that_is_a_regular_file(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".protect-to-act").write_text("collision", encoding="utf-8")

            with self.assertRaisesRegex(OSError, "管理路径"):
                module.initialize(root)

    def test_rejects_directory_at_template_destination(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            collision = root / ".protect-to-act" / "PROJECT_OVERVIEW.md"
            collision.mkdir(parents=True)

            with self.assertRaisesRegex(OSError, "PROJECT_OVERVIEW.md"):
                module.initialize(root)

    def test_rejects_symlink_at_template_destination(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            management_dir = root / ".protect-to-act"
            management_dir.mkdir()
            collision = management_dir / "PROJECT_OVERVIEW.md"
            original_is_symlink = Path.is_symlink

            def report_collision_as_symlink(path):
                return path == collision or original_is_symlink(path)

            with mock.patch.object(Path, "is_symlink", report_collision_as_symlink):
                with self.assertRaisesRegex(OSError, "符号链接"):
                    module.initialize(root)
            self.assertFalse(collision.exists())

    def test_exclusive_create_preserves_file_created_during_race(self):
        module = load_module()
        original_open = Path.open
        injected = False

        def racing_open(path, mode="r", *args, **kwargs):
            nonlocal injected
            if path.name == "PROJECT_OVERVIEW.md" and mode == "xb" and not injected:
                injected = True
                with original_open(path, "wb") as racing_file:
                    racing_file.write(b"racer-content")
            return original_open(path, mode, *args, **kwargs)

        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(Path, "open", racing_open):
            root = Path(temp_dir)
            result = module.initialize(root)
            overview = root / ".protect-to-act" / "PROJECT_OVERVIEW.md"

            self.assertTrue(injected, "initializer must create destinations with Path.open('xb')")
            self.assertEqual(overview.read_bytes(), b"racer-content")
            self.assertEqual(result["skipped"], ["PROJECT_OVERVIEW.md"])

    def test_removes_new_destination_when_copying_fails(self):
        module = load_module()

        def fail_after_partial_copy(source, destination):
            destination.write(b"partial")
            raise OSError("injected copy failure")

        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            module.shutil, "copyfileobj", side_effect=fail_after_partial_copy
        ):
            root = Path(temp_dir)
            with self.assertRaisesRegex(OSError, "injected copy failure"):
                module.initialize(root)

            self.assertFalse((root / ".protect-to-act" / "PROJECT_OVERVIEW.md").exists())


class InitializerCliTests(unittest.TestCase):
    def test_cli_success_emits_deterministic_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_cli(Path(temp_dir))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), {"created": list(EXPECTED_FILES), "skipped": []})

    def test_cli_error_is_nonzero_and_emits_no_success_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_file = Path(temp_dir) / "not-a-directory"
            project_file.write_text("x", encoding="utf-8")
            result = run_cli(project_file)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("初始化失败", result.stderr)

    def test_cli_rejects_destination_collision_without_success_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".protect-to-act" / "PROJECT_OVERVIEW.md").mkdir(parents=True)
            result = run_cli(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("PROJECT_OVERVIEW.md", result.stderr)

    def test_cli_missing_template_fails_before_project_mutation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script_path = make_isolated_script(root, missing_template="PROJECT_ACCEPTANCE.md")
            project_root = root / "project"
            project_root.mkdir()
            result = run_cli(project_root, script_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("PROJECT_ACCEPTANCE.md", result.stderr)
            self.assertFalse((project_root / ".protect-to-act").exists())

    def test_concurrent_cli_runs_create_each_file_exactly_once(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            environment = os.environ.copy()
            environment["PYTHONUTF8"] = "1"
            command = [sys.executable, str(SCRIPT_PATH), "--project-root", str(root)]
            processes = [
                subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    env=environment,
                )
                for _ in range(8)
            ]
            results = [process.communicate(timeout=30) for process in processes]

            for process, (stdout, stderr) in zip(processes, results):
                self.assertEqual(process.returncode, 0, stderr)
                self.assertEqual(stderr, "")
                self.assertEqual(set(json.loads(stdout)), {"created", "skipped"})
            reports = [json.loads(stdout) for stdout, _ in results]
            created = [filename for report in reports for filename in report["created"]]
            self.assertEqual(sorted(created), sorted(EXPECTED_FILES))
            self.assertEqual(
                {path.name for path in (root / ".protect-to-act").iterdir()}, set(EXPECTED_FILES)
            )


if __name__ == "__main__":
    unittest.main()
