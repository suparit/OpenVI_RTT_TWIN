#!/usr/bin/env python3
"""
join_cell_html.py — Automated Child-HTML Cartridge Extractor & Master Joiner
Project: OpenVI_TR1100_CELL_TWIN (DG-2026-101 Child-HTML Joiner Pattern)

Usage:
    py join_cell_html.py            # One-shot join -> DIST_FULL_CELL_TWIN.html
    py join_cell_html.py --watch    # Auto-rejoin whenever any child HTML changes
"""

from __future__ import annotations
import datetime
import re
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
# Support running either from repo root or directly inside 05_tests_and_webgl/
if (SCRIPT_DIR / "05_tests_and_webgl").is_dir() and not (SCRIPT_DIR / "parts").is_dir():
    BASE_DIR = SCRIPT_DIR / "05_tests_and_webgl"
else:
    BASE_DIR = SCRIPT_DIR

PARTS_DIR = BASE_DIR / "parts"
TEMPLATE_FILE = BASE_DIR / "master_shell_template.html"
OUTPUT_FILE = BASE_DIR / "DIST_FULL_CELL_TWIN.html"

CARTRIDGE_RE = re.compile(
    r"/\*\s*<<<BEGIN_OPENVI_PART_CARTRIDGE:\s*([A-Za-z0-9_.-]+)>>>\s*\*/"
    r"(.*?)"
    r"/\*\s*<<<END_OPENVI_PART_CARTRIDGE:\s*\1>>>\s*\*/",
    re.DOTALL,
)

INJECT_PLACEHOLDER = "/* <<<OPENVI_INJECT_ALL_PART_CARTRIDGES_HERE>>> */"


def extract_cartridges() -> tuple[list[dict], list[str]]:
    cartridges = []
    errors = []
    seen_ids = set()

    if not PARTS_DIR.exists():
        errors.append(f"[ERROR] Parts folder not found: {PARTS_DIR}")
        return cartridges, errors

    for html_file in sorted(PARTS_DIR.glob("*.html")):
        text = html_file.read_text(encoding="utf-8")
        matches = list(CARTRIDGE_RE.finditer(text))
        if not matches:
            errors.append(f"[WARN] {html_file.name}: No <<<BEGIN_OPENVI_PART_CARTRIDGE>>> block found.")
            continue

        for m in matches:
            part_id = m.group(1)
            code_body = m.group(2).strip()
            if part_id in seen_ids:
                errors.append(f"[ERROR] Duplicate part ID '{part_id}' in {html_file.name}")
                continue
            seen_ids.add(part_id)
            cartridges.append({
                "part_id": part_id,
                "source_file": html_file.name,
                "lines": len(code_body.splitlines()),
                "code": code_body,
            })
    return cartridges, errors


def build_master_html() -> bool:
    if not TEMPLATE_FILE.exists():
        print(f"[ERROR] Missing template: {TEMPLATE_FILE}")
        return False

    shell_text = TEMPLATE_FILE.read_text(encoding="utf-8")
    if INJECT_PLACEHOLDER not in shell_text:
        print(f"[ERROR] Template missing placeholder: {INJECT_PLACEHOLDER}")
        return False

    cartridges, issues = extract_cartridges()
    for msg in issues:
        print(msg)
    if any(msg.startswith("[ERROR]") for msg in issues):
        return False

    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    joined_blocks = [
        f"// === AUTO-JOINED {len(cartridges)} PART CARTRIDGES AT {stamp} ==="
    ]
    for c in cartridges:
        joined_blocks.append(
            f"\n// --- FROM CHILD FILE: {c['source_file']} "
            f"(ID: {c['part_id']}, {c['lines']} lines) ---\n{c['code']}"
        )

    final_html = shell_text.replace(INJECT_PLACEHOLDER, "\n".join(joined_blocks), 1)
    OUTPUT_FILE.write_text(final_html, encoding="utf-8")
    kb = OUTPUT_FILE.stat().st_size / 1024.0
    print(f"[OK] Built {OUTPUT_FILE.name} ({kb:.1f} KB) from {len(cartridges)} child HTML part(s) @ {stamp}")
    return True


def watch_loop() -> None:
    print(f"Watching {PARTS_DIR} and {TEMPLATE_FILE.name} for changes... (Ctrl+C to stop)")
    last_sig = None
    while True:
        files = [TEMPLATE_FILE] + (sorted(PARTS_DIR.glob("*.html")) if PARTS_DIR.exists() else [])
        sig = tuple((f.name, f.stat().st_mtime_ns) for f in files if f.exists())
        if sig != last_sig:
            build_master_html()
            last_sig = sig
        time.sleep(0.4)


if __name__ == "__main__":
    if "--watch" in sys.argv:
        watch_loop()
    else:
        sys.exit(0 if build_master_html() else 1)
