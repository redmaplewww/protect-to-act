#!/usr/bin/env python3
"""安全初始化项目的 .protect-to-act 管理目录。"""

from __future__ import annotations

import argparse
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
    management_dir = project_root / ".protect-to-act"
    management_dir.mkdir(parents=True, exist_ok=True)

    report: dict[str, list[str]] = {"created": [], "skipped": []}
    for filename in TEMPLATE_NAMES:
        source = template_dir / filename
        if not source.is_file():
            raise FileNotFoundError(f"缺少 Skill 模板：{source}")
        destination = management_dir / filename
        if destination.exists():
            report["skipped"].append(filename)
            continue
        shutil.copyfile(source, destination)
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
