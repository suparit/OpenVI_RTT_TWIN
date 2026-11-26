# AGENTS.md — AI Coder Operational Rules for `OpenVI_TR1100_CELL_TWIN`

Welcome, AI Coding Agent (VS Code + Cline, Claude Code, Cursor, Windsurf, or Codex).
This repository follows the **Machine-as-Code** and **Engineering Pattern Language (EPL)** architecture (`DG-2026-097` & `DG-2026-100`). Read and obey every invariant below before creating or modifying any specification, CAD script, mechanical test, or 3D WebGL file.

---

## 1. Repository Directory Topology

```text
OpenVI_TR1100_CELL_TWIN/
├── AGENTS.md                                  # Primary entrypoint & rules for all AI Coder Agents
├── bootstrap_machine_repo.py                  # One-click local scaffold & file verifier/generator
├── 00_specs/
│   ├── CELL_CONSTANTS.json                    # Single Source of Truth for datums, dimensions & catalog ratings
│   └── DG-2026-100_Machine_as_Code_Spec.md    # Full architecture blueprint of this repository
├── 01_catalog_parts/                          # Level 1: Standard catalog part cards (Part No., price, ratings)
│   ├── MISUMI_CJHB75.md                       # Heavy-duty swivel caster, blue MC nylon Ø75 mm (H = 106 mm)
│   ├── MISUMI_C-AJPJ16-148.md                 # S45C leveling mount M16x2.0, stud L = 148 mm
│   └── WEISS_TR1100_30_F.md                   # Hollow-center rotary ring indexer, 30 st x 12 deg CW, 1.18 s
├── 02_patterns/                               # Level 2: Reusable Engineering Pattern Language (PATTERN_DNA) cards
│   ├── PAT_BASE_CORNER_CASTER_LEVELER_01.md   # 4x identical symmetric corner caster + leveler plate pattern
│   └── PAT_MOTION_HOLLOW_ROTARY_RING_01.md    # Stationary inner-island probe mounting inside Ø800 mm bore
├── 03_assembly_layers/                        # Level 3: Bottom-up human assembly sequence (L01 -> L05)
│   ├── L01_foundation_and_leveling.md         # Floor Z=0, 4x corner plates, CJHB75 casters & C-AJPJ16-148 feet
│   ├── L02_base_frame_and_dp2_pocket.md       # 80x80 mm aluminum base grid, 45-deg braces & DP2 motor pocket
│   └── L03_deck_and_tr1100_ring.md            # Z=850 mm deck plate & Ø1000/Ø800x25 mm 30-station ring
├── 04_cad_distiller/                          # Autodesk Fusion 360 exporter & distilled binary .stl meshes
│   └── fusion_ai_exporter_v2_webgl.py         # Exports cached world-mm JSON, joints, RGBA & low-poly .stl
└── 05_tests_and_webgl/                        # Automated mechanical unit tests & standalone 3D WebGL twins
    └── verify_machine_repo.py                 # Pure Python 3 stdlib mechanical invariant test suite
```

---

## 2. Coordinate System & Unit Invariants

1. **World Coordinate Frame (Right-Handed, Z-Up):**
   - `Z = 0.0 mm` is the **Factory Floor Datum** (`floor_z_mm`). `+Z` points vertically UP.
   - `+X` points RIGHT toward the green outfeed belt conveyor and stainless hopper.
   - `-Y` points FRONT toward the operator service hatch and sloped red reject chute.
   - *(Note on Fusion 360 screenshots: if a CAD view shows `Y-Up`, transform `(X_cad, -Z_cad, Y_cad) -> (X, Y, Z)` when mapping to this Z-Up world frame.)*
2. **Engineering Units:**
   - All JSON and Markdown specs strictly use **`mm`, `deg`, `kg`, `s`, `N`, `Nm`**.
   - Convert `mm * 0.001 -> meters` **ONLY** inside the WebGL vertex/matrix rendering layer.
3. **Rotary Ring Indexing Direction (`CW`):**
   - `TR1100-30-F-DP2-MP1` indexes **Clockwise (CW)** when viewed from `+Z` top-down (`-12.0 deg` around `+Z` per step in `1.18 s`, with `~0.10 s` E-Stop braking ramp).

---

## 3. Bottom-Up Datum Chain (Zero Magic Z Numbers)

Never hardcode arbitrary Z elevations in upper assembly layers. Every layer imports its lower datum from `00_specs/CELL_CONSTANTS.json`:
- **Transport Mode (`jack_stroke_mm = 0.0`):** `C-AJPJ16-148` leveling pads are retracted; all 4 `MISUMI CJHB75` blue nylon wheels rest on `Z = 0.0 mm`; under-frame sits at `Z = 106.0 mm`.
- **Stationary Operating Mode (`jack_stroke_mm = +9.0`):** `C-AJPJ16-148` feet press against `Z = 0.0 mm`, lifting `under_frame_stationary_z_mm` to **`115.0 mm`** so all 4 `CJHB75` wheels float **`9.0 mm`** clear of the floor (eliminating caster sway under `23.11 Nm` peak ring indexing torque).
- **Tabletop Deck Datum:** Lower frame columns span from `115.0 mm` up to `deck_top_z_mm = 850.0 mm`.

---

## 4. Zero-Dependency WebGL & Resource Safety Gate

- **Standalone HTML5 Only:** Every `.html` twin in `05_tests_and_webgl/` must run offline from `file://` or a local static server with **zero external CDN scripts** (pure Vanilla JS + CSS3 + Native WebGL). All code comments in C/JS/Python technical kernels should be clear and concise.
- **GPU Polygon Budget:** Total scene triangles `<= 120,000`. Repeated parts (`4x` corner assemblies, `30x` dial fixtures) must reuse a single VBO via instanced transforms.
- **Deep Physics Main Gate:** Default mode MUST be `MODE 0: GATE OFF` (`<= 1.5 ms/frame` kinematic motion). When `MODE 1: GATE ON` is active, enforce an automatic circuit breaker that trips back to `GATE OFF` if frame time exceeds `20.0 ms` for `15` consecutive frames.

---

## 5. Mandatory Verification Workflow

Whenever you edit `00_specs/CELL_CONSTANTS.json`, catalog ratings, or assembly layer offsets, run:

```bash
python 05_tests_and_webgl/verify_machine_repo.py
```

All 5 mechanical invariants (caster float clearance, M16 stud thread reserve, 3-wheel uneven-floor transport safety factor, 4-foot stationary safety factor, and 30-station chord clearance) must output `[PASS]` before finishing your task.

---

## 6. Projector Safety Check & IP Hygiene

- **Harvest Knowledge, Not Confidential Data:** Never store customer names, proprietary UUT product geometry, internal factory KPIs/yields, credentials, or personal contact details in any file.
- Represent workpieces strictly as generic dummy blocks (`UUT_DUMMY`) and reference only public standard catalog parts (MISUMI, WEISS, IEC/ISO standards).
