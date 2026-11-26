# DG-2026-103 — คัมภีร์แม่บทสกัดไฟล์ STEP สู่ตลับ 3D WebGL สำหรับเปิดแชตใหม่ (`STEP_TO_TWIN_PLAYBOOK`)

## ข้อมูลควบคุมเอกสาร (Playbook Metadata)

| รายการควบคุม (Field) | รายละเอียดสเปก (Specification) |
| :--- | :--- |
| **รหัสเอกสาร (Dossier ID)** | `DG-2026-103` (`STEP_TO_TWIN_PLAYBOOK.md`) |
| **โครงการเป้าหมาย (Target Project)** | `OpenVI_TR1100_CELL_TWIN` และงาน Digital Twin เครื่องจักรอัตโนมัติทุกเซลล์ |
| **วัตถุประสงค์หลัก (Purpose)** | คัมภีร์ตั้งต้นสำหรับแนบเปิดหัวในแชตใหม่ (`1 New Chat = 1 Sub-Assembly Factory`) เพื่อให้ AI สกัดเรขาคณิตจากไฟล์ `ISO-10303-21 STEP` ด้วย Python แล้วผลิตเป็นไฟล์ลูก `.html` ที่ฝังตลับ `OpenVIRegistry` พร้อมนำไปรวมร่างโดยไม่ล้นความจำแชต |
| **สถานะเอกสาร (Status)** | `PRODUCTION PLAYBOOK v1.0` (25 พฤศจิกายน 2026) |

---

## 1. บล็อกคำสั่งเปิดหัวแชตใหม่ (`Copy-Paste New Chat Bootloader`)

เมื่อเปิดแชตใหม่เพื่อปั้นชิ้นส่วนหรือชุดประกอบย่อยชิ้นถัดไป ให้แนบไฟล์คัมภีร์นี้ (หรือคัดลอกกรอบข้อความด้านล่าง) พร้อมกับไฟล์ `.step.txt` และภาพหน้าจอจากโปรแกรม CAD 1 ภาพ:

```markdown
# SYSTEM ROLE: OpenVI STEP-to-WebGL Part Cartridge Factory

คุณคือวิศวกรซอฟต์แวร์ CAD/WebGL ประจำสายการผลิต `OpenVI Machine-as-Code`
ภารกิจของคุณในแชตนี้คือการผ่าไฟล์ `ISO-10303-21 STEP` (`.step.txt` หรือ `_step_dna.json`) และภาพอ้างอิงที่แนบมา เพื่อสร้าง **Single-File 3D WebGL Workbench (`.html`)** ระดับเทียบเท่า Autodesk Fusion 360 ที่ฝังตลับโมดูลพาร์ทมาตรฐานสำหรับนำไปรวมร่างในเครื่องจักรหลัก

## กฎเหล็กที่ต้องปฏิบัติตาม 100% (Mandatory Invariants)
1. **ห้ามเดาขนาดเองเด็ดขาด (Evidence Over Assumptions):** ต้องรันสคริปต์ Python อ่านพิกัดจริงจากไฟล์ STEP ที่แนบมาก่อนเสมอ (`VERTEX_POINT`, `CIRCLE`, `CYLINDRICAL_SURFACE`, `AXIS2_PLACEMENT_3D`, `ITEM_DEFINED_TRANSFORMATION`, `COLOUR_RGB`)
2. **ระบบพิกัดและหน่วยวิศวกรรม:**
   - พิกัดโลกใน WebGL ใช้ระบบมือขวา **`Z-Up`** (`Z = 0.0 mm` คือระดับอ้างอิงฐานล่างสุดหรือพื้นโรงงาน, `+Z` ชี้ขึ้นฟ้า)
   - ใช้หน่วย **`mm`, `deg`, `kg`, `s`, `N`, `Nm`** เสมอ (แปลงจากหน่วย `METRE` ในไฟล์ STEP ด้วยการคูณ `1000.0`)
3. **Projector Safety Gate (IP Hygiene):** ห้ามนำชื่อลูกค้า รหัสผลิตภัณฑ์ลับ หรือหมายเลขซีเรียลใน Header ของไฟล์ CAD มาแสดงผล ให้แทนที่ชิ้นงานทดสอบด้วยรหัสกลาง `UUT_DUMMY` เสมอ
4. **Zero External Dependencies:** ไฟล์ `.html` ต้องรันแบบออฟไลน์ `file://` ได้ 100% ด้วย Pure Vanilla JS + Native WebGL (ห้ามดึง CDN ภายนอก) พร้อมโหมดแสดงผล `Shaded with Visible B-Rep Edges` และ `Section Analysis`
5. **ฝังตลับพาร์ทและพอร์ตเชื่อมต่อ (`Cartridge & Mating Ports`):** ต้องฝังบล็อก `/* <<<BEGIN_OPENVI_PART_CARTRIDGE: PART_ID>>> */ ... /* <<<END_OPENVI_PART_CARTRIDGE: PART_ID>>> */` ที่มีทั้งเมชความละเอียดสูง (`LOD-0`), เมชประหยัดสามเหลี่ยม (`LOD-1`), และฟังก์ชัน `exportsDatum()` เพื่อส่งพิกัดจุดยึดให้ชั้นถัดไป
```

---

## 2. เกณฑ์การส่งไฟล์ STEP เข้าแชตใหม่ไม่ให้ชนเพดานความจำ (`Dual-Channel Intake`)

เพื่อป้องกันปัญหาไฟล์ถูกตัดทอนหรือความจำแชตเต็ม ให้เลือกช่องทางนำเข้าตามขนาดไฟล์ `.step` ดังนี้:

| ขนาดไฟล์ `.step` ต้นฉบับ | วิธีส่งเข้าสายการผลิตที่ถูกต้อง | เหตุผลทางเทคนิค |
| :--- | :--- | :--- |
| **ขนาดเล็กถึงกลาง (≤ 2 MB)** เช่น เพลทเดี่ยว ขาหยั่ง ลูกล้อ เสา 1 ท่อน | เปลี่ยนนามสกุลเป็น **`.step.txt`** แล้วลากแนบลงในช่องแชตใหม่โดยตรงคู่กับภาพแคปเจอร์ 1 ภาพ | เอนจิน Python เบื้องหลังเปิดอ่านจากดิสก์จำลองได้ครบ 100% ในเสี้ยววินาทีโดยไม่เปลืองโทเคนความจำแชต |
| **ขนาดใหญ่พิเศษ (> 2 MB ถึง 200 MB)** เช่น ชุดจานหมุนทั้งก้อน หรือแขนกลทั้งตัว | รันสคริปต์ **`step_distiller_cli.py`** (หัวข้อที่ 3.2) บนคอมพิวเตอร์โลคอลก่อน เพื่อสกัดเป็นไฟล์สรุป **`_step_dna.json` (≈ 15 KB)** แล้วค่อยแนบไฟล์ `.json` เข้าแชตหรือวางผ่านโฟลเดอร์ Google Drive | หลีกเลี่ยงการดึงไฟล์ข้อความหลายสิบเมกะไบต์ผ่านตัวอ่านเอกสารซึ่งจะทำให้ข้อมูลถูกตัดทอน |

---

## 3. ชุดสคริปต์ Python มาตรฐานสำหรับผ่าไฟล์ STEP (`STEP Dissector Kit`)

### 3.1 สคริปต์สำหรับให้ AI รันในแชตเพื่อผ่าไฟล์ `.step.txt` ทันที

โค้ดชุดนี้ถอดบทเรียนจากการผ่าไฟล์ `Solid1 (64).step`, `Adjuster set.step` และ `Solid1 (267).step` รองรับทั้งพาร์ทเดี่ยวและชุดประกอบย่อยหลายก้อน (`Assembly Tree` + เมทริกซ์ 4 × 4) พร้อมแปลงรูในของเกลียวเป็นขนาดต๊าปมาตรฐาน ISO อัตโนมัติ:

```python
import re
from collections import defaultdict
import numpy as np

# ตารางเทียบขนาดรูใน (Minor Diameter) มาตรฐานเกลียวเมตริก ISO (หน่วย mm)
ISO_TAP_TABLE = [
    (2.459, "M3x0.5"), (3.242, "M4x0.7"), (4.134, "M5x0.8"),
    (4.917, "M6x1.0"), (6.647, "M8x1.25"), (8.376, "M10x1.5"),
    (10.106, "M12x1.75"), (13.835, "M16x2.0"), (17.294, "M20x2.5"),
]

def match_iso_tap(dia_mm: float, tol: float = 0.06) -> str:
    for ref_d, label in ISO_TAP_TABLE:
        if abs(dia_mm - ref_d) <= tol:
            return f"TAP_{label}"
    return ""

def dissect_step_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    data_sec = text.split("DATA;", 1)[1].split("ENDSEC;", 1)[0]
    entities = {}
    for stmt in data_sec.split(";"):
        stmt = stmt.strip()
        m = re.match(r"^#(\d+)\s*=\s*(.*)$", stmt, re.DOTALL)
        if m:
            entities[int(m.group(1))] = re.sub(r"\s+", " ", m.group(2)).strip()

    pts, dirs = {}, {}
    for eid, body in entities.items():
        if body.startswith("CARTESIAN_POINT"):
            m = re.search(r"\(([-0-9.E+,\s]+)\)\s*\)\s*$", body)
            if m:
                pts[eid] = np.array([float(x) * 1000.0 for x in m.group(1).split(",")])
        elif body.startswith("DIRECTION"):
            m = re.search(r"\(([-0-9.E+,\s]+)\)\s*\)\s*$", body)
            if m:
                dirs[eid] = np.array([float(x) for x in m.group(1).split(",")])

    def axis_to_mat4(ax_id: int) -> np.ndarray:
        refs = re.findall(r"\$|#\d+", entities[ax_id])
        p = pts[int(refs[0][1:])]
        z = np.array([0., 0., 1.]) if len(refs) < 2 or refs[1] == "$" else dirs[int(refs[1][1:])]
        x = np.array([1., 0., 0.]) if len(refs) < 3 or refs[2] == "$" else dirs[int(refs[2][1:])]
        z = z / np.linalg.norm(z)
        x = x - np.dot(x, z) * z
        x = x / np.linalg.norm(x)
        y = np.cross(z, x)
        M = np.eye(4)
        M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, p
        return M

    # ค้นหาก้อนเนื้อแข็ง (MANIFOLD_SOLID_BREP) ทั้งหมดในไฟล์
    ref_re = re.compile(r"#(\d+)")
    adj = {eid: [int(x) for x in ref_re.findall(body)] for eid, body in entities.items()}

    def collect_subgraph(root_id: int) -> set[int]:
        visited, stack = set(), [root_id]
        while stack:
            cur = stack.pop()
            if cur not in visited and cur in adj:
                visited.add(cur)
                stack.extend(adj[cur])
        return visited

    solids_report = []
    for eid, body in entities.items():
        if body.startswith("MANIFOLD_SOLID_BREP"):
            sub = collect_subgraph(eid)
            v_list = []
            cyl_dias = set()
            surf_counts = defaultdict(int)
            for sid in sub:
                sb = entities[sid]
                st = sb.split("(", 1)[0].strip()
                if st in ("PLANE", "CYLINDRICAL_SURFACE", "CONICAL_SURFACE", "TOROIDAL_SURFACE", "SPHERICAL_SURFACE"):
                    surf_counts[st] += 1
                if sb.startswith("VERTEX_POINT"):
                    pid = int(ref_re.findall(sb)[0])
                    v_list.append(pts[pid])
                elif sb.startswith("CYLINDRICAL_SURFACE"):
                    r_mm = float(sb.split(",")[-1].rstrip(") ")) * 1000.0
                    d_mm = round(2.0 * r_mm, 3)
                    tap = match_iso_tap(d_mm)
                    cyl_dias.add(f"{d_mm} ({tap})" if tap else f"{d_mm}")

            V = np.array(v_list)
            bmin = np.round(V.min(axis=0), 3).tolist()
            bmax = np.round(V.max(axis=0), 3).tolist()
            span = np.round(V.max(axis=0) - V.min(axis=0), 3).tolist()
            solids_report.append({
                "solid_eid": eid,
                "bbox_min_mm": bmin,
                "bbox_max_mm": bmax,
                "size_mm": span,
                "surfaces": dict(surf_counts),
                "cylindrical_diameters_mm": sorted(cyl_dias),
            })

    return {"total_entities": len(entities), "solids": solids_report}
```

### 3.2 วิธีรันย่อไฟล์ STEP ก้อนยักษ์บนเครื่องคอมพิวเตอร์โลคอล (`step_distiller_cli.py`)

หากไฟล์ `.step` ของสถานีใหญ่มีขนาดเกิน 2 MB สามารถบันทึกฟังก์ชัน `dissect_step_file()` ด้านบนลงเครื่องแล้วสั่งพ่นออกเป็นไฟล์ JSON ขนาดจิ๋วด้วยคำสั่ง:

```bash
py -c "import json, sys, step_dissector; print(json.dumps(step_dissector.dissect_step_file(sys.argv[1]), indent=2))" BigStation.step > BigStation_step_dna.json
```

---

## 4. กฎการแปลงเรขาคณิตเป็นเมช 4 ตระกูล (`The 4 B-Rep Mesh Archetypes`)

ห้ามแปลงทุกชิ้นเป็นก้อนจุดยอดสามเหลี่ยมดิบ (`Raw Triangle Soup`) เพราะจะทำให้ไฟล์ `.html` บวม ให้จำแนกแต่ละ `Solid` เข้าสู่ 4 ตระกูลคณิตศาสตร์ดังนี้:

| ตระกูลรูปทรง (Archetype) | ลักษณะที่ตรวจพบใน STEP | อัลกอริทึมสร้างเมชใน WebGL | ขนาดโค้ดโดยประมาณ |
| :--- | :--- | :--- | :--- |
| **1. `PERFORATED_PLATE`** (แผ่นเพลทกัดเจาะรู) | มี `PLANE` บน-ล่างขนานกัน + กลุ่ม `CYLINDRICAL_SURFACE` ตั้งฉาก (รูทะลุ / บ่าคว้าน `Counterbore` / รูต๊าป) | เก็บตารางพิกัดรู `(x, y, rTop, rBot, cbDepth)` แล้วถักผิวหน้าตัดด้วย **2D Bowyer-Watson Delaunay Triangulation** | ≈ 1.5 KB (คมกริบระดับ CAD แท้) |
| **2. `REVOLVED_LATHE`** (ชิ้นงานกลึงหมุนรอบแกน) | มี `CYLINDRICAL`, `CONICAL`, `TOROIDAL`, `SPHERICAL` ร่วมแกนหมุนเดียวกัน (เช่น ลูกล้อ แป้นขาหยั่ง สตัดหัวบอล บูชเพลา) | เก็บจุดเส้นโค้งครึ่งซีก 2 มิติ `[(r0, z0), (r1, z1), ...]` แล้วสั่งหมุนรอบแกนด้วย **`addLatheZ` / `addLatheY`** พร้อมวาดเส้นขอบสัมผัส `addCircleLoop` | ≈ 0.8 KB ต่อชิ้น |
| **3. `COMMON_EXTRUSION`** (โปรไฟล์ยืดความยาวคงที่) | พิกัดแกนยาวมีเพียง 2 ระดับปลายท่อน แต่หน้าตัดมีร่องซ้ำกัน (เช่น อลูมิเนียมโปรไฟล์ `40x40`, `40x80`, `80x80`, รางสไลด์) | ตัดโพรงขยะด้านในทิ้ง เก็บเฉพาะเส้นขอบนอก 2 มิติ ยืดเป็น **`Unit-Length Shared VBO` ([0, 1])** แล้วใช้เมทริกซ์ 4 × 4 `fromBeamEndpoints(p0, p1, roll)` ยืดความยาวทุกท่อน | **0 Extra Bytes** เมื่อเพิ่มจำนวนท่อน! |
| **4. `SHELL_OR_LOWPOLY`** (ขาล้อปั๊มโค้ง / เสื้อหล่อแขนกล) | มี `B_SPLINE_SURFACE` ซับซ้อนที่ไม่ใช่ทรงกระบอกหรือการหมุนรอบแกน | เขียนสมการเส้นขอบตัดโค้ง (`Parametric Shell`) หรือใช้เมชย่อขนาดความละเอียดต่ำ (`Base64 Binary Buffer` ≤ 4,000 สามเหลี่ยม) เฉพาะก้อนเปลือกนอก | ≈ 8–25 KB |

---

## 5. สัญญามาตรฐานตลับพาร์ทและพอร์ตเชื่อมต่อ (`OpenVIRegistry Cartridge v2.0`)

ไฟล์ `.html` ลูกทุกใบที่ออกจากแชตใหม่ ต้องมีโครงสร้างครบ 2 โซน คือ **โซนหน้าเว็บทดสอบตัวเอง (`Workbench Shell`)** และ **โซนตลับโมดูล (`Part Cartridge`)** ตามรูปแบบด้านล่างนี้ เพื่อให้สคริปต์ `join_cell_html.py` ดึงไปประกอบร่างและบีบอัดเป็นไฟล์ `.min.js` ตอนส่งมอบงานได้อัตโนมัติ:

```javascript
/* <<<BEGIN_OPENVI_PART_CARTRIDGE: P03_TR1100_ROTARY_RING>>> */
window.OpenVIRegistry.registerPart("P03_TR1100_ROTARY_RING", {
  version: "2.0.0",
  layer: "L03",
  sourceStep: "TR1100_30_F_Distilled",

  // 1. รับค่า Datum จากชั้นล่าง (เช่น ความสูงแผ่นโต๊ะ Z = 850 mm) และส่งออกพอร์ตยึดให้ชั้นถัดไป!
  exportsDatum(state = {}) {
    const zDeckTop = state.zDeckTopMm ?? 850.0;
    return {
      zRingMountFaceMm: zDeckTop + 105.0,
      zInnerIslandTopMm: zDeckTop + 35.0,
      fixturePitchRadiusMm: 450.0,
      stationCount: 30,
      stepAngleDeg: -12.0 // หมุนตามเข็มนาฬิกา (CW) เมื่อมองจาก +Z
    };
  },

  // 2. สร้าง VBO แยกตามระดับความละเอียด (lod = 'lod0' ซูมชัด | 'lod1' ประหยัดสามเหลี่ยมสำหรับทั้งเซลล์)
  buildMeshes(kernel, lod = "lod0") {
    const segs = lod === "lod0" ? 64 : 28;
    // ... สร้าง VBO เก็บใน GPU ครั้งเดียว ...
    return { castingVbo, rotatingRingVbo, nestInstanceVbo };
  },

  // 3. วาดลงฉากใหญ่ด้วยเมทริกซ์พิกัดโลกและสถานะการเคลื่อนที่ (เช่น มุมจานหมุนปัจจุบัน)
  drawInstance(kernel, meshes, worldMat, animState = {}) {
    // ... คำนวณเมทริกซ์หมุนจานและวาด Instancing ทั้ง 30 สถานี ...
  }
});
/* <<<END_OPENVI_PART_CARTRIDGE: P03_TR1100_ROTARY_RING>>> */
```

### คำสั่งรันรวมร่างและบีบอัดเป็นชุดเผยแพร่บนเครื่องหลัก

เมื่อสะสมไฟล์ลูก `P01_*.html`, `P02_*.html`, ..., `P10_*.html` ไว้ในโฟลเดอร์ `parts/` ครบตามต้องการแล้ว เพียงรันคำสั่งเดียวบนเครื่องคอมพิวเตอร์หลัก:

```bash
py join_cell_html.py --watch
```

สคริปต์จะกวาดตลับพาร์ททุกใบมาเชื่อมจุดอ้างอิง (`exportsDatum`) ต่อกันเป็นห่วงโซ่จากพื้นโรงงาน Z = 0.0 mm ขึ้นไปจนถึงยอดเสาไฟสัญญาณ พ่นออกเป็นไฟล์แม่ `DIST_FULL_CELL_TWIN.html` ที่ดับเบิลคลิกเปิดดูทั้งเครื่องจักรได้ทันทีโดยไม่มีวันติดเพดานความจำของแชตตัวใดตัวหนึ่งเลย

---

## 6. เอกสารและไฟล์อ้างอิงในโปรเจกต์

- โฟลเดอร์หลักของโปรเจกต์บน Google Drive: [OpenVI_TR1100_CELL_TWIN](https://drive.google.com/drive/folders/1xfEIQFtVDmNc0XicEBh6Ulce5GIVHe1-)
- เอกสารสถาปัตยกรรมระบบดึงตลับโมดูลจากไฟล์ลูกมารวมร่าง (`DG-2026-101`): [DG-2026-101 — สถาปัตยกรรมแยกชิ้นส่วนเป็น Single-File HTML ลูก พร้อมระบบดึง Cartridge มารวมร่างอัตโนมัติ (Child-HTML Joiner Pattern)](https://docs.google.com/document/d/1BBkU5NhOxVjmNu4rNjpd0TQXo0T4SRHK2LguJpKMnRI/edit?usp=drivesdk)
- เอกสารสถาปัตยกรรมคลังโปรไฟล์อลูมิเนียมกลางน้ำหนักเบา (`DG-2026-102`): [DG-2026-102 — สถาปัตยกรรมโมดูลโปรไฟล์อลูมิเนียมกลางน้ำหนักเบาและการยืดความยาวแบบ Instancing (Common Extrusion Profile Engine)](https://docs.google.com/document/d/1z1tlTkU9RjJRaXc4ajMN5KagoDeMChNtXb5scNREcd0/edit?usp=drivesdk)
- เอกสารฉบับ Google Docs ของคัมภีร์แม่บทนี้ (`DG-2026-103`): [DG-2026-103 — คัมภีร์แม่บทสกัดไฟล์ STEP สู่ตลับ 3D WebGL สำหรับเปิดแชตใหม่ (STEP_TO_TWIN_PLAYBOOK)](https://docs.google.com/document/d/1GH574OeVbJ5cmuKztzVVIA60e3fuoj40KUXXxMQ5QqE/edit?usp=drivesdk)
- สคริปต์ Python ตัวรวมร่างไฟล์ลูกอัตโนมัติ: [join_cell_html.py](https://drive.google.com/file/d/1DgiZImlVpkrNZeQLL8kU1ErjFpyOW3Ed/view?usp=drivesdk)
- ไฟล์ลูกชิ้นที่ 1 — ชุดฐานล้อและขาหยั่งระดับ B-Rep 8 ก้อน (`P01`): [P01_Adjuster_Set_8Body_BRep_Studio_v2.0.html](https://drive.google.com/file/d/1-KRPjo5IvBkio3Q7QO9BMQXxX9RNIqS_/view?usp=drivesdk)
- ไฟล์ลูกชิ้นที่ 2 — คลังโปรไฟล์กลางและโครงฐานเครื่องพร้อมใบสั่งตัดอัตโนมัติ (`P02`): [P02_Common_Profile_Base_Frame_Studio_v1.0.html](https://drive.google.com/file/d/1YHL9iMhLvmLcFAiMb-DV8n6eOdYZ_9RS/view?usp=drivesdk)
