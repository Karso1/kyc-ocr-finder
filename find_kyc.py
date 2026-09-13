#!/usr/bin/env python3
"""Local KYC OCR finder for macOS.

Uses Homebrew Tesseract and macOS sips. Original documents are never modified.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | {".pdf"}


def normalize(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def tesseract_available() -> bool:
    return shutil.which("tesseract") is not None


def rasterize(source: Path, destination: Path, degrees: int) -> bool:
    """Create a temporary, OCR-ready PNG without changing the source file."""
    command = ["sips", "-s", "format", "png"]
    if degrees:
        command.extend(["-r", str(degrees)])
    command.extend([str(source), "--out", str(destination)])
    result = subprocess.run(command, capture_output=True, text=True)
    return result.returncode == 0 and destination.exists()


def recognize(source: Path, rotations: tuple[int, ...]) -> str:
    best = ""
    for degrees in rotations:
        with tempfile.TemporaryDirectory(prefix="kyc-ocr-") as temporary_dir:
            image = Path(temporary_dir) / "page.png"
            if not rasterize(source, image, degrees):
                continue
            result = subprocess.run(
                ["tesseract", str(image), "stdout", "-l", "eng", "--psm", "11"],
                capture_output=True,
                text=True,
                errors="ignore",
            )
            if len(result.stdout) > len(best):
                best = result.stdout
    return best


def is_match(text: str, identity: str, name_words: tuple[str, ...]) -> bool:
    compact = normalize(text)
    if identity and normalize(identity) in compact:
        return True
    return bool(name_words) and all(normalize(word) in compact for word in name_words)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search local KYC files with Tesseract OCR.")
    parser.add_argument("--root", type=Path, default=Path.home() / "Desktop/upay/kyc", help="KYC root folder")
    parser.add_argument("--id", default="", help="Identity number; hyphens and spaces are ignored")
    parser.add_argument("--name", default="", help="Full name or selected name words")
    parser.add_argument("--workers", type=int, default=4, help="Parallel OCR jobs (default: 4)")
    parser.add_argument("--rotate", action="store_true", help="Try all four rotations; slower but more reliable")
    parser.add_argument("--output", type=Path, default=Path("ocr_matches.txt"), help="Results text file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not tesseract_available():
        print("未找到 tesseract。请先运行：brew install tesseract", file=sys.stderr)
        return 2
    if not args.root.is_dir():
        print(f"找不到 KYC 文件夹：{args.root}", file=sys.stderr)
        return 2
    if not args.id and not args.name:
        print("请至少提供 --id 或 --name。", file=sys.stderr)
        return 2

    files = sorted(path for path in args.root.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS)
    rotations = (0, 90, 180, 270) if args.rotate else (0,)
    name_words = tuple(word for word in args.name.split() if word)
    print(f"将扫描 {len(files)} 份图片/PDF；并行任务：{args.workers}；旋转检测：{'开启' if args.rotate else '关闭'}")

    matches: list[str] = []
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        jobs = {pool.submit(recognize, source, rotations): source for source in files}
        for future in concurrent.futures.as_completed(jobs):
            source = jobs[future]
            completed += 1
            try:
                text = future.result()
            except Exception as error:  # Continue even if an individual file is unreadable.
                print(f"跳过无法读取的文件：{source} ({error})", file=sys.stderr)
                continue
            if is_match(text, args.id, name_words):
                block = f"找到候选：\n{source}\n\nOCR 内容：\n{text.strip()}\n{'-' * 72}\n"
                print("\n" + block)
                matches.append(block)
            if completed % 25 == 0 or completed == len(files):
                print(f"进度：{completed}/{len(files)}；候选：{len(matches)}")

    output = args.output.expanduser().resolve()
    output.write_text("".join(matches) if matches else "未找到匹配结果。\n", encoding="utf-8")
    print(f"\n完成。结果文件：{output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
