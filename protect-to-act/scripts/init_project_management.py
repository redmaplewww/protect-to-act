#!/usr/bin/env python3
"""安全初始化项目的 .protect-to-act 管理目录。"""

from __future__ import annotations

import argparse
import io
import json
import shutil
from pathlib import Path


TEMPLATE_NAMES = (
    "PROJECT_OVERVIEW.md",
    "PROJECT_PROGRESS.md",
    "PROJECT_VERSIONS.md",
    "PROJECT_FEATURES.md",
    "PROJECT_ACCEPTANCE.md",
)


def initialize(project_root: Path) -> dict[str, list[str]]:
    """复制缺失模板；绝不覆盖已有文件。"""
    project_root = Path(project_root).expanduser().resolve()
    if not project_root.exists():
        raise ValueError(f"项目根路径不存在：{project_root}")
    if not project_root.is_dir():
        raise ValueError(f"项目根路径不是目录：{project_root}")

    template_dir = Path(__file__).resolve().parent.parent / "assets" / "templates"
    templates: list[tuple[str, bytes]] = []
    for filename in TEMPLATE_NAMES:
        source = template_dir / filename
        if source.is_symlink() or not source.is_file():
            raise FileNotFoundError(f"缺少或不是常规文件的 Skill 模板：{source}")
        with source.open("rb") as source_file:
            templates.append((filename, source_file.read()))

    management_dir = project_root / ".protect-to-act"
    if management_dir.is_symlink():
        raise OSError(f"管理路径不得是符号链接：{management_dir}")
    if management_dir.exists() and not management_dir.is_dir():
        raise OSError(f"管理路径不是目录：{management_dir}")
    try:
        management_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        if management_dir.is_symlink() or not management_dir.is_dir():
            raise OSError(f"管理路径不是安全的目录：{management_dir}")

    report: dict[str, list[str]] = {"created": [], "skipped": []}
    for filename, template_content in templates:
        destination = management_dir / filename
        if destination.is_symlink():
            raise OSError(f"目标路径不得是符号链接：{destination}")
        if destination.exists():
            if not destination.is_file():
                raise OSError(f"目标路径不是常规文件：{destination}")
            report["skipped"].append(filename)
            continue

        try:
            destination_file = destination.open("xb")
        except FileExistsError:
            if destination.is_symlink():
                raise OSError(f"并发创建的目标路径是符号链接：{destination}")
            if not destination.is_file():
                raise OSError(f"并发创建的目标路径不是常规文件：{destination}")
            report["skipped"].append(filename)
            continue

        try:
            with destination_file:
                shutil.copyfileobj(io.BytesIO(template_content), destination_file)
        except BaseException:
            try:
                destination.unlink()
            except FileNotFoundError:
                pass
            raise
        report["created"].append(filename)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化 .protect-to-act 项目管理文档，不覆盖已有文件。")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="项目根目录；默认使用当前工作目录。",
    )
    args = parser.parse_args()
    try:
        report = initialize(args.project_root)
    except (ValueError, FileNotFoundError, OSError) as error:
        parser.exit(1, f"初始化失败：{error}\n")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
