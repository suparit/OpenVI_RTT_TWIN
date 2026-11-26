#!/usr/bin/env python3
"""
step_dissector.py — Zero-Dependency ISO-10303-21 STEP to JSON DNA Distiller
Project: OpenVI_TR1100_CELL_TWIN (DG-2026-103 STEP_TO_TWIN_PLAYBOOK)

Pure Python 3 standard library (no numpy/pip packages required).
Distills large .step / .stp / .step.txt files (2 MB - 200+ MB) into a compact,
IP-sanitized `_step_dna.json` (~10-30 KB) ready to attach in any New Chat or
upload via the Google Drive MCP Pipeline without hitting context limits.

Usage:
    py step_dissector.py MyAssembly.step
    py step_dissector.py MyPart.step -o custom_dna.json
"""

from __future__ import annotations
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import re
import sys

ISO_TAP_TABLE = [
    (2.459, "M3x0.5"),
    (3.242, "M4x0.7"),
    (4.134, "M5x0.8"),
    (4.917, "M6x1.0"),
    (6.647, "M8x1.25"),
    (8.376, "M10x1.5"),
    (10.106, "M12x1.75"),
    (13.835, "M16x2.0"),
    (17.294, "M20x2.5"),
    (20.752, "M24x3.0"),
]

SENSITIVE_RE = re.compile(r"(customer|client|secret|serial|uut|proprietary)", re.IGNORECASE)
REF_RE = re.compile(r"#(\d+)")


def sanitize_label(raw: str, fallback: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.\- ()]+", "_", (raw or "").strip())
    if not clean or SENSITIVE_RE.search(clean):
        return fallback
    return clean[:72]


def match_iso_tap(dia_mm: float, tol: float = 0.065) -> str | None:
    for ref_d, name in ISO_TAP_TABLE:
        if abs(dia_mm - ref_d) <= tol:
            return name
    return None


def vec_norm(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def vec_dot(a: list[float], b: list[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec_cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def mat4_mul(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    out = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            out[i][j] = sum(A[i][k] * B[k][j] for k in range(4))
    return out


def mat4_inv_rigid(M: list[list[float]]) -> list[list[float]]:
    # Inverse of rigid 4x4 homogeneous matrix [R | t; 0 0 0 1] -> [R^T | -R^T t]
    R_T = [[M[j][i] for j in range(3)] for i in range(3)]
    t = [M[0][3], M[1][3], M[2][3]]
    inv_t = [-sum(R_T[i][k] * t[k] for k in range(3)) for i in range(3)]
    return [
        [R_T[0][0], R_T[0][1], R_T[0][2], inv_t[0]],
        [R_T[1][0], R_T[1][1], R_T[1][2], inv_t[1]],
        [R_T[2][0], R_T[2][1], R_T[2][2], inv_t[2]],
        [0.0, 0.0, 0.0, 1.0],
    ]


def classify_archetype(surf_counts: dict[str, int], distinct_levels: list[int]) -> str:
    if surf_counts.get("B_SPLINE_SURFACE", 0) > 0:
        return "SHELL_OR_LOWPOLY"
    if surf_counts.get("SPHERICAL_SURFACE", 0) > 0 or surf_counts.get("CONICAL_SURFACE", 0) >= 2:
        return "REVOLVED_LATHE"
    if min(distinct_levels) == 2 and surf_counts.get("PLANE", 0) >= 16:
        return "COMMON_EXTRUSION"
    if surf_counts.get("PLANE", 0) >= 4 and surf_counts.get("CYLINDRICAL_SURFACE", 0) >= 2:
        return "PERFORATED_PLATE"
    return "PRIMITIVE_SOLID"


def dissect_step_file(filepath: Path) -> dict:
    raw_text = filepath.read_text(encoding="utf-8", errors="ignore")
    if "DATA;" not in raw_text:
        raise ValueError(f"Invalid STEP file (missing DATA; section): {filepath}")

    data_sec = raw_text.split("DATA;", 1)[1].split("ENDSEC;", 1)[0]
    entities: dict[int, str] = {}
    for stmt in data_sec.split(";"):
        stmt = stmt.strip()
        m = re.match(r"^#(\d+)\s*=\s*(.*)$", stmt, re.DOTALL)
        if m:
            entities[int(m.group(1))] = re.sub(r"\s+", " ", m.group(2)).strip()

    pts: dict[int, list[float]] = {}
    dirs: dict[int, list[float]] = {}
    prod_defs: dict[int, str] = {}
    colours: list[dict] = []

    for eid, body in entities.items():
        if body.startswith("CARTESIAN_POINT"):
            m = re.search(r"\(([-0-9.E+,\s]+)\)\s*\)\s*$", body)
            if m:
                pts[eid] = [float(x) * 1000.0 for x in m.group(1).split(",")]
        elif body.startswith("DIRECTION"):
            m = re.search(r"\(([-0-9.E+,\s]+)\)\s*\)\s*$", body)
            if m:
                dirs[eid] = [float(x) for x in m.group(1).split(",")]
        elif body.startswith("PRODUCT("):
            m = re.match(r"PRODUCT\('([^']*)',\s*'([^']*)'", body)
            if m:
                prod_defs[eid] = sanitize_label(m.group(2), f"PART_{eid}")
        elif body.startswith("COLOUR_RGB"):
            m = re.match(r"COLOUR_RGB\('([^']*)',\s*([^,]+),\s*([^,]+),\s*([^)]+)\)", body)
            if m:
                colours.append({
                    "id": eid,
                    "rgb_255": [
                        round(float(m.group(2)) * 255),
                        round(float(m.group(3)) * 255),
                        round(float(m.group(4)) * 255),
                    ],
                })

    def axis_to_mat4(ax_id: int) -> list[list[float]]:
        refs = re.findall(r"\$|#\d+", entities[ax_id])
        p = pts.get(int(refs[0][1:]), [0.0, 0.0, 0.0])
        z = [0.0, 0.0, 1.0] if len(refs) < 2 or refs[1] == "$" else dirs.get(int(refs[1][1:]), [0.0, 0.0, 1.0])
        x = [1.0, 0.0, 0.0] if len(refs) < 3 or refs[2] == "$" else dirs.get(int(refs[2][1:]), [1.0, 0.0, 0.0])
        z = vec_norm(z)
        dot_xz = vec_dot(x, z)
        x = vec_norm([x[0] - dot_xz * z[0], x[1] - dot_xz * z[1], x[2] - dot_xz * z[2]])
        y = vec_cross(z, x)
        return [
            [x[0], y[0], z[0], p[0]],
            [x[1], y[1], z[1], p[1]],
            [x[2], y[2], z[2], p[2]],
            [0.0, 0.0, 0.0, 1.0],
        ]

    # Parse Assembly Transforms (ITEM_DEFINED_TRANSFORMATION)
    transforms_out = []
    for eid, body in entities.items():
        if body.startswith("ITEM_DEFINED_TRANSFORMATION"):
            refs = [int(r[1:]) for r in REF_RE.findall(body)]
            if len(refs) >= 2 and refs[0] in entities and refs[1] in entities:
                M_from = axis_to_mat4(refs[0])
                M_to = axis_to_mat4(refs[1])
                T = mat4_mul(M_to, mat4_inv_rigid(M_from))
                transforms_out.append({
                    "eid": eid,
                    "translation_mm": [round(T[0][3], 3), round(T[1][3], 3), round(T[2][3], 3)],
                    "rotation_3x3": [[round(T[r][c], 4) for c in range(3)] for r in range(3)],
                })

    # Build entity reference graph to isolate each MANIFOLD_SOLID_BREP
    adj = {eid: [int(x) for x in REF_RE.findall(body)] for eid, body in entities.items()}

    def collect_subgraph(root_id: int) -> set[int]:
        visited: set[int] = set()
        stack = [root_id]
        while stack:
            cur = stack.pop()
            if cur not in visited and cur in adj:
                visited.add(cur)
                stack.extend(adj[cur])
        return visited

    solids_out = []
    for idx, (eid, body) in enumerate(sorted(entities.items())):
        if not body.startswith("MANIFOLD_SOLID_BREP"):
            continue
        m_name = re.match(r"MANIFOLD_SOLID_BREP\('([^']*)'", body)
        solid_name = sanitize_label(m_name.group(1) if m_name else "", f"Solid_{idx + 1:02d}")
        sub = collect_subgraph(eid)

        v_coords: list[list[float]] = []
        surf_counts: dict[str, int] = defaultdict(int)
        cyl_features = defaultdict(list)

        for sid in sub:
            sb = entities[sid]
            stype = sb.split("(", 1)[0].strip()
            if "B_SPLINE_SURFACE" in sb:
                surf_counts["B_SPLINE_SURFACE"] += 1
            elif stype in ("PLANE", "CYLINDRICAL_SURFACE", "CONICAL_SURFACE", "TOROIDAL_SURFACE", "SPHERICAL_SURFACE"):
                surf_counts[stype] += 1

            if sb.startswith("VERTEX_POINT"):
                r_ids = REF_RE.findall(sb)
                if r_ids and int(r_ids[0]) in pts:
                    v_coords.append(pts[int(r_ids[0])])
            elif sb.startswith("CIRCLE"):
                r_ids = REF_RE.findall(sb)
                if r_ids and int(r_ids[0]) in entities:
                    try:
                        r_mm = float(sb.split(",")[-1].rstrip(") ")) * 1000.0
                        M_ax = axis_to_mat4(int(r_ids[0]))
                        ox, oy, oz = round(M_ax[0][3], 3), round(M_ax[1][3], 3), round(M_ax[2][3], 3)
                        dia = round(2.0 * r_mm, 3)
                        cyl_features[dia].append([ox, oy, oz])
                    except ValueError:
                        pass

        if not v_coords:
            continue

        xs = [p[0] for p in v_coords]
        ys = [p[1] for p in v_coords]
        zs = [p[2] for p in v_coords]
        bmin = [round(min(xs), 3), round(min(ys), 3), round(min(zs), 3)]
        bmax = [round(max(xs), 3), round(max(ys), 3), round(max(zs), 3)]
        span = [round(bmax[i] - bmin[i], 3) for i in range(3)]
        distinct_lvls = [
            len({round(x, 2) for x in xs}),
            len({round(y, 2) for y in ys}),
            len({round(z, 2) for z in zs}),
        ]

        diameters_summary = []
        for dia in sorted(cyl_features.keys()):
            centers = sorted({tuple(c) for c in cyl_features[dia]})
            tap = match_iso_tap(dia)
            entry = {
                "dia_mm": dia,
                "circle_count": len(centers),
                "sample_centers_mm": [list(c) for c in centers[:16]],
            }
            if tap:
                entry["iso_tap_match"] = tap
            diameters_summary.append(entry)

        solids_out.append({
            "solid_eid": eid,
            "name": solid_name,
            "recommended_archetype": classify_archetype(surf_counts, distinct_lvls),
            "vertex_count": len(v_coords),
            "local_bbox_mm": {"min": bmin, "max": bmax, "size": span},
            "distinct_coord_levels_xyz": distinct_lvls,
            "surfaces": dict(surf_counts),
            "circle_diameters": diameters_summary[:30],
        })

    return {
        "schema": "OPENVI_STEP_DNA_v1.0",
        "source_filename": sanitize_label(filepath.name, "sanitized_part.step"),
        "source_size_kb": round(filepath.stat().st_size / 1024.0, 1),
        "total_step_entities": len(entities),
        "product_names": list(prod_defs.values())[:30],
        "colours_rgb": colours,
        "assembly_transforms_count": len(transforms_out),
        "assembly_transforms": transforms_out[:40],
        "solid_count": len(solids_out),
        "solids": solids_out,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Distill ISO-10303-21 STEP file into compact _step_dna.json")
    parser.add_argument("step_file", type=Path, help="Input .step / .stp / .step.txt file")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output .json path")
    args = parser.parse_args()

    src: Path = args.step_file
    if not src.exists():
        print(f"[ERROR] File not found: {src}", file=sys.stderr)
        return 1

    out_path = args.output or src.with_name(f"{src.stem}_step_dna.json")
    report = dissect_step_file(src)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out_kb = out_path.stat().st_size / 1024.0
    ratio = (1.0 - out_kb / max(0.1, report["source_size_kb"])) * 100.0
    print(f"[OK] Distilled {src.name} ({report['source_size_kb']:.1f} KB, {report['total_step_entities']} entities)")
    print(f"  -> Solids found: {report['solid_count']}")
    for s in report["solids"]:
        sz = s["local_bbox_mm"]["size"]
        print(f"     * #{s['solid_eid']} {s['name']}: {sz[0]} x {sz[1]} x {sz[2]} mm [{s['recommended_archetype']}]")
    print(f"  -> Saved DNA JSON: {out_path} ({out_kb:.1f} KB, compressed {ratio:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
