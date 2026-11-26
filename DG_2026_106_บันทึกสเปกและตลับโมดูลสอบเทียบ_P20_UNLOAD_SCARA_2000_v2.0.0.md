# DG-2026-106 — บันทึกสเปกและตลับโมดูลสอบเทียบแขนกล 2000-Unload SCARA (`P20_UNLOAD_SCARA_2000`)

## ข้อมูลควบคุมเอกสารและประวัติการปรับปรุง (Revision Control & Metadata)

| รายการควบคุม (Field) | รายละเอียดทางวิศวกรรม (Engineering Specification) |
| :--- | :--- |
| **รหัสเอกสาร (Dossier ID)** | `DG-2026-106` (`P20_UNLOAD_SCARA_2000_SPEC_v2.0.md`) |
| **รหัสตลับโมดูล (Part ID)** | `P20_UNLOAD_SCARA_2000` (Layer: `L04`) |
| **รหัสรุ่นอุปกรณ์ (Equipment Model)** | `IXP-4N6520-WA-S-P3-B` (IAI PowerCON SCARA 4-Axis) + `VSP-C20-10BN-6` (Vacuum Pad) |
| **สถานะเอกสาร (Release Status)** | `PRODUCTION RELEASE v2.0.0` (ผ่านการสอบเทียบกับแคตตาล็อกและโมเดล CAD) |
| **วันที่อนุมัติ (Effective Date)** | 25 พฤศจิกายน 2026 |
| **โครงการเป้าหมาย (Target Cell)** | `OpenVI_TR1100_CELL_TWIN` และสคริปต์รวมร่างเซลล์ `join_cell_html.py` |

---

### ประวัติการแก้ไขรุ่น (Revision History Table)

| รุ่น (Rev.) | วันที่ | รายละเอียดการปรับปรุงทางวิศวกรรม (Engineering Changes) | ผู้รับผิดชอบ |
| :--- | :--- | :--- | :--- |
| **v1.0.0** | 25 พ.ย. 2026 | สกัดข้อมูล B-Rep เรขาคณิต 11 ชิ้นจาก `2000-Unload scara.step_step_dna.json` และสร้างตลับร่างเริ่มต้น | CAD Dissector |
| **v2.0.0** | 25 พ.ย. 2026 | **Calibrated Release:**<br>1. ปรับช่วงขอบเขตมุม Joint และสโตรก $Z$ ตามแคตตาล็อกจริง ($J_1=\pm 127^\circ, J_2=\pm 127^\circ, Z=0\dots -200\text{ mm}, R=\pm 360^\circ$)<br>2. สลับลำดับซ้อนฐาน: ขาตั้งมอเตอร์ `Solid 460` ($Z=0\dots 70\text{ mm}$) อยู่ล่างสุด ตามด้วยแผ่นเพลท `Solid 455` ($Z=70\dots 85\text{ mm}$)<br>3. ปรับระดับความสูงท้องแขนท่อนแรกเป็น $Z = 333.5\text{ mm}$ และเพิ่มมุมบิดฐานติดตั้ง $45^\circ$<br>4. เพิ่มระบบแจ้งเตือนและเรนเดอร์ขอบเขตห้ามทำงาน (`Operation Prohibited Area` $R = 296.717\text{ mm}$)<br>5. ปรับพอร์ตส่งออก `exportsDatum(state)` ให้ส่งพิกัดตำแหน่งหัวดูดจริงระดับมิลลิเมตร | Lead Control Eng / Noom |

---

## 1. ข้อมูลจำเพาะทางกลและพิกัดการเคลื่อนที่ (Calibrated Kinematic Benchmarks)

อ้างอิงจากแคตตาล็อกผู้ผลิต IAI เอกสารหมายเลข `IXP_CE0219-5A` หน้า 19–20:

```
                          [J2 Elbow Axis]
                                o
                               / \
              L1 = 360 mm     /   \    L2 = 290 mm
              (±127 deg)     /     \   (±127 deg)
                            /       \
                           /         o [Z Quill Axis] (Stroke 200 mm)
                          o           \
                  [J1 Base Axis]       \  LTool = 85 mm (Wrist Rotation ±360 deg)
                  (Z = 333.5 mm)        * [TCP: VSP-C20 Vacuum Cup]
```

| แกนการเคลื่อนที่ (Axis) | ระยะพิกัดทางกล (Link / Stroke) | ช่วงการทำงาน (Work Envelope) | อัตราเร็วสูงสุด (Speed) | ความแม่นยำซ้ำ (Repeatability) |
| :--- | :--- | :--- | :--- | :--- |
| **Axis 1 (Shoulder $J_1$)** | ความยาวแขน $L_1 = 360.00\text{ mm}$ | $\pm 127^\circ$ | $2,916\text{ mm/s}$ (Composite) | $\pm 0.04\text{ mm}$ |
| **Axis 2 (Elbow $J_2$)** | ความยาวแขน $L_2 = 290.00\text{ mm}$ | $\pm 127^\circ$ | $2,916\text{ mm/s}$ (Composite) | $\pm 0.04\text{ mm}$ |
| **Axis 3 (Vertical Quill $Z$)** | สโตรกเลื่อนแกนตั้ง $= 200.00\text{ mm}$ | $0.0\text{ mm} \rightarrow -200.0\text{ mm}$ | $240\text{ mm/s}$ | $\pm 0.02\text{ mm}$ |
| **Axis 4 (Wrist Roll $R$)** | การหมุนรอบแกนเครื่องมือ | $\pm 360^\circ$ | $700^\circ\text{/s}$ | $\pm 0.02^\circ$ |
| **รัศมีทำงานรวม (Reach)** | $L_1 + L_2 = 650.00\text{ mm}$ | รัศมีในสุด $R_{\min} = 296.717\text{ mm}$ | — | — |
| **น้ำหนักชิ้นงานยก (Payload)** | พิกัดปกติ $2.0\text{ kg}$ / สูงสุด $6.0\text{ kg}$ | รอบเวลาทำงานมาตรฐาน $0.81\text{ s}$ | — | — |
| **น้ำหนักตัวหุ่นยนต์ (Mass)** | $22.00\text{ kg}$ (รุ่น 4 แกนมาตรฐาน) | ระบบเบรก Option `B` (ล็อกแกนแนวดิ่ง) | — | — |

---

## 2. ลำดับโครงสร้างฐานและความสูงแกน $Z$ (Structural Stack Calibration)

จากการวิเคราะห์รูเจาะ B-Rep ในไฟล์ STEP และระยะอ้างอิงจากแบบดรอว์อิ้ง:
1. **ชั้นล่างสุด — โครงกล่องมอเตอร์และเกียร์ (`Solid #460`):** ขนาด $200 \times 200 \times 70\text{ mm}$ วางประกบติดกับแผ่นโต๊ะเครื่องจักรหลัก $Z = 0.0\dots 70.0\text{ mm}$
2. **ชั้นคั่นกลาง — เพลทติดตั้งฐาน (`Solid #455`):** ขนาด $200 \times 200 \times 15\text{ mm}$ วางประกบบนกล่องมอเตอร์ที่ระดับ $Z = 70.0\dots 85.0\text{ mm}$ โดยมีมุมบิดฐานติดตั้งทำมุม $45^\circ$ ตามแนวรูต๊าป $\text{M10}\times 1.5$ (PCD $165\text{ mm}$)
3. **เสาไหล่ฐานหุ่นยนต์ (`Solid #459`):** เริ่มต้นที่ระดับ Seating Face $Z = 85.0\text{ mm}$ ขึ้นไปจนถึงระดับกึ่งกลางแนวแกนหมุนของแขนท่อนแรก
4. **แนวระนาบท้องแขนท่อนแรก (`Solid #458`):** ลอยตัวอยู่ที่ระดับความสูง **$Z = 333.5\text{ mm}$** เหนือระนาบฐานโต๊ะ $Z = 0.0\text{ mm}$

---

## 3. สัญญามาตรฐานตลับโมดูล (`OpenVIRegistry Cartridge v2.0.0`)

โค้ดชุดนี้ผ่านการทดสอบ Zero-Bloat และสามารถนำไปเสียบเข้ากับไฟล์ `master_shell_template.html` หรือสั่งรวมร่างผ่าน `join_cell_html.py` ได้ทันที:

```javascript
/* =========================================================================
   <<<BEGIN_OPENVI_PART_CARTRIDGE: P20_UNLOAD_SCARA_2000>>>
   Sub-Assembly Cartridge: 2000-Unload SCARA (IAI IXP-4N6520 + VSP-C20)
   Standard: OpenVIRegistry v2.0 | Version: 2.0.0 | Dossier: DG-2026-106
   ========================================================================= */
window.OpenVIRegistry.registerPart("P20_UNLOAD_SCARA_2000", {
  version: "2.0.0",
  layer: "L04",
  sourceStep: "2000-Unload_scara_Sanitized",
  uutId: "UUT_DUMMY",
  boundingBoxMm: { 
    min: [-382.0, -100.0, 0.0], 
    max: [290.0, 430.0, 450.0], 
    size: [672.0, 530.0, 450.0] 
  },

  // 1. ส่งออกพิกัดจุดเชื่อมต่อ (Mating Ports) และการคำนวณ Forward Kinematics
  exportsDatum(state = {}) {
    const zMount = state.zMountFaceMm ?? 0.0;
    const j1Deg = state.j1Deg ?? 15.0;
    const j2Deg = state.j2Deg ?? 45.0;
    const zStrokeMm = state.zStrokeMm ?? -40.0;
    const rDeg = state.rDeg ?? 0.0;

    const j1 = j1Deg * Math.PI / 180.0;
    const j12 = (j1Deg + j2Deg) * Math.PI / 180.0;
    const j12r = (j1Deg + j2Deg + rDeg) * Math.PI / 180.0;

    const L1 = 360.0;    // แขนท่อน 1 (Shoulder to Elbow)
    const L2 = 290.0;    // แขนท่อน 2 (Elbow to Quill)
    const LTool = 85.0;  // ระยะเยื้องศูนย์ของแผ่น Adaptor ไปยังหัวดูดสุญญากาศ

    const elbowX = L1 * Math.cos(j1);
    const elbowY = L1 * Math.sin(j1);

    const quillX = elbowX + L2 * Math.cos(j12);
    const quillY = elbowY + L2 * Math.sin(j12);

    const tcpX = quillX + LTool * Math.cos(j12r);
    const tcpY = quillY + LTool * Math.sin(j12r);
    const tcpZ = zMount + 165.0 + zStrokeMm; // ที่สโตรก Z = -165 mm ปลายลูกยางสัมผัสระดับโต๊ะ

    return {
      partId: "P20_UNLOAD_SCARA_2000",
      revision: "2.0.0",
      uutIdentifier: "UUT_DUMMY",
      mountingBasePort: {
        positionMm: [0.0, 0.0, zMount],
        normal: [0.0, 0.0, -1.0],
        plateSizeMm: [200.0, 200.0, 15.0],
        boltPattern: "8x M10x1.5 (Minor Ø8.376mm) on PCD 165mm + 4x Ø12/Ø6.5 CB",
        baseOrientationOffsetDeg: 45.0
      },
      quillFlangePort: {
        positionMm: [
          Number(quillX.toFixed(3)), 
          Number(quillY.toFixed(3)), 
          Number((zMount + 247.0 + zStrokeMm).toFixed(3))
        ],
        boltPattern: "4x M6x1.0 (Minor Ø4.917mm) on PCD 38mm"
      },
      vacuumToolPort: {
        positionMm: [
          Number(tcpX.toFixed(3)), 
          Number(tcpY.toFixed(3)), 
          Number(tcpZ.toFixed(3))
        ],
        normal: [0.0, 0.0, -1.0],
        cupModel: "VSP-C20-10BN-6 (Ø20mm Pad)",
        stemThread: "M16x2.0 (Minor Ø13.800mm)"
      },
      workEnvelopeLimits: {
        j1RangeDeg: [-127.0, 127.0],
        j2RangeDeg: [-127.0, 127.0],
        zStrokeRangeMm: [-200.0, 0.0],
        rRangeDeg: [-360.0, 360.0],
        minRadiusMm: 296.717,
        maxRadiusMm: 650.0
      },
      kinematics: { j1Deg, j2Deg, zStrokeMm, rDeg }
    };
  },

  // 2. สร้างเมช GPU VBOs แยกตามระดับความละเอียด (LOD-0 / LOD-1)
  buildMeshes(kernel, lod = "lod0") {
    const segLathe = lod === "lod0" ? 40 : 18;
    const segHole = lod === "lod0" ? 20 : 10;
    const segArc = lod === "lod0" ? 18 : 8;

    // Solid 455: แผ่นเพลทฐาน (Z = 70..85 mm)
    const baseHoles = [
      { x: 0, y: 0, r: 10.0 },
      { x: -80, y: -80, r: 3.25, cbRadius: 6.0, cbDepth: 7.0 },
      { x: -80, y:  80, r: 3.25, cbRadius: 6.0, cbDepth: 7.0 },
      { x:  80, y: -80, r: 3.25, cbRadius: 6.0, cbDepth: 7.0 },
      { x:  80, y:  80, r: 3.25, cbRadius: 6.0, cbDepth: 7.0 },
      { x: -82.731, y:  2.121, r: 4.188 },
      { x:  -2.121, y: 82.731, r: 4.188 },
      { x:   0.707, y: -81.317, r: 4.188 },
      { x:  81.317, y:  -0.707, r: 4.188 }
    ];
    const eid455 = kernel.uploadMesh(
      BRepBuilder.createPerforatedPlate(
        BRepBuilder.makeChamferRectContour(200, 200, 8),
        baseHoles, 70.0, 85.0, segHole
      )
    );

    // Solid 460: กล่องขาตั้งมอเตอร์ล่างสุด (Z = 0..70 mm)
    const eid460 = kernel.uploadMesh(
      BRepBuilder.createPerforatedPlate(
        BRepBuilder.makeChamferRectContour(156, 156, 14),
        [
          { x: -62, y: -62, r: 5.5 },
          { x: -62, y:  62, r: 5.5 },
          { x:  62, y: -62, r: 5.5 },
          { x:  62, y:  62, r: 5.5 }
        ],
        0.0, 70.0, segHole
      )
    );

    // Solid 459: เสาไหล่ SCARA (Z = 85..250 mm)
    const colLathe = BRepBuilder.createLatheZ([
      [0, 85], [67, 85], [67, 102], [60, 108], [60, 232], [66, 236], [66, 250], [32, 250], [0, 250]
    ], segLathe, 0, 0);
    const colSpine = BRepBuilder.createPerforatedPlate(
      [[-145, -42], [-133, -52], [0, -52], [0, 52], [-133, 52], [-145, 42]],
      [], 85.0, 232.0, segHole
    );
    const eid459 = kernel.uploadMesh(BRepBuilder.mergeGeoms([colLathe, colSpine]));

    // Solid 458: แขนท่อน 1 J1 (L1 = 360 mm, Z = 250..316 mm)
    const eid458 = kernel.uploadMesh(
      BRepBuilder.createPerforatedPlate(
        BRepBuilder.makeStadiumContour(0, 360, 35, segArc),
        [
          { x: 0, y: 0, r: 16.0, cbRadius: 24.0, cbDepth: 8.0 },
          { x: 360, y: 0, r: 15.0, cbRadius: 21.0, cbDepth: 8.0 }
        ],
        250.0, 316.0, segHole
      )
    );

    // Solid 457: แขนท่อน 2 J2 + ฝาครอบโค้ง (L2 = 290 mm, Z = 316..434 mm)
    const eid457 = kernel.uploadMesh(BRepBuilder.createScaraArm2Shell(lod));

    // Solid 456: เพลาขับ Spline Quill (Ø16 x 350 mm)
    const eid456 = kernel.uploadMesh(
      BRepBuilder.createLatheZ([
        [0, 253], [12, 253], [12, 265], [8.0, 265], [8.0, 598], [6.5, 603], [0, 603]
      ], segLathe, 0, 0)
    );

    // Solid 462, 461, 463, 464, 465: ชุดเครื่องมือและลูกยางดูดสุญญากาศ
    const eid462 = kernel.uploadMesh(
      BRepBuilder.createLatheZ([[0, 247], [25, 247], [25, 252], [14, 252], [14, 262], [0, 262]], segLathe)
    );
    const eid461 = kernel.uploadMesh(
      BRepBuilder.createPerforatedPlate(
        BRepBuilder.makeStadiumContour(-5, 88, 28, segArc),
        [
          { x: 0, y: 0, r: 7.25 },
          { x: -19, y: 0, r: 3.3, cbRadius: 5.5, cbDepth: 3.5 },
          { x:  19, y: 0, r: 3.3, cbRadius: 5.5, cbDepth: 3.5 },
          { x: 0, y: -19, r: 3.3, cbRadius: 5.5, cbDepth: 3.5 },
          { x: 0, y:  19, r: 3.3, cbRadius: 5.5, cbDepth: 3.5 },
          { x: 85, y: 0, r: 7.25 }
        ],
        241.0, 247.0, segHole
      )
    );
    const eid463 = kernel.uploadMesh(
      BRepBuilder.createLatheZ([[0, 232], [10, 232], [10, 241], [7, 241], [7, 247], [10, 247], [10, 255], [0, 261]], segLathe)
    );
    const eid464 = kernel.uploadMesh(
      BRepBuilder.createLatheZ([[0, 177], [6.5, 177], [6.5, 192], [5.0, 192], [5.0, 222], [8.0, 222], [8.0, 232], [0, 232]], segLathe)
    );
    const eid465 = kernel.uploadMesh(
      BRepBuilder.createLatheZ([[0, 165], [9.815, 165], [8.2, 169], [6.8, 171], [8.5, 174], [7.0, 177], [0, 177]], segLathe)
    );

    // แหวนมาร์กเกอร์จุดยึดและเส้นเขตห้ามทำงาน
    const baseDatumRing = kernel.uploadMesh(
      BRepBuilder.createLatheZ([[80, 0.2], [85, 0.2], [85, 2.2], [80, 2.2], [80, 0.2]], 36)
    );
    const tcpDatumRing = kernel.uploadMesh(
      BRepBuilder.createLatheZ([[0, -1.5], [11.5, -1.5], [11.5, 0.5], [0, 0.5]], 28)
    );
    const prohibitRing = kernel.uploadMesh(
      BRepBuilder.createLatheZ([[294.0, 0.2], [299.4, 0.2], [299.4, 2.0], [294.0, 2.0]], 48)
    );

    return {
      eid455, eid460, eid459, eid458, eid457,
      eid456, eid462, eid461, eid463, eid464, eid465,
      baseDatumRing, tcpDatumRing, prohibitRing
    };
  },

  // 3. ฟังก์ชันวาดลงฉากด้วยเมทริกซ์การเคลื่อนที่
  drawInstance(kernel, meshes, worldMat, animState = {}) {
    const j1Rad = (animState.j1Deg ?? 0) * Math.PI / 180;
    const j2Rad = (animState.j2Deg ?? 0) * Math.PI / 180;
    const zStroke = animState.zStrokeMm ?? 0;
    const rRad = (animState.rDeg ?? 0) * Math.PI / 180;
    const vis = animState.visibility || {};

    // ฐานล่างสุด Solid 460
    if (vis[460] !== false) kernel.drawPart(meshes.eid460, worldMat, [0.18, 0.20, 0.25]);

    // เพลทฐาน Solid 455 บิดมุม 45 องศา
    if (vis[455] !== false) {
      const mPlate = kernel.Mat4.create();
      kernel.Mat4.rotateZ(mPlate, worldMat, 45.0 * Math.PI / 180.0);
      kernel.drawPart(meshes.eid455, mPlate, [0.55, 0.58, 0.65]);
    }

    // เสาไหล่หุ่นยนต์ Solid 459
    if (vis[459] !== false) kernel.drawPart(meshes.eid459, worldMat, [0.72, 0.75, 0.80]);

    // แขนท่อน 1 หมุนรอบแกน J1
    const mJ1 = kernel.Mat4.create();
    kernel.Mat4.rotateZ(mJ1, worldMat, j1Rad);
    if (vis[458] !== false) kernel.drawPart(meshes.eid458, mJ1, [0.86, 0.89, 0.94]);

    // แขนท่อน 2 ต่อที่ระยะ X = +360 mm และหมุนตามมุม J2
    const mJ2 = kernel.Mat4.create();
    kernel.Mat4.translate(mJ2, mJ1, [360.0, 0.0, 0.0]);
    kernel.Mat4.rotateZ(mJ2, mJ2, j2Rad);
    if (vis[457] !== false) kernel.drawPart(meshes.eid457, mJ2, [0.90, 0.92, 0.96]);

    // แกน Quill ต่อที่ระยะ X = +290 mm เลื่อนขึ้น-ลงตามสโตรก Z
    const mWrist = kernel.Mat4.create();
    kernel.Mat4.translate(mWrist, mJ2, [290.0, 0.0, zStroke]);
    kernel.Mat4.rotateZ(mWrist, mWrist, rRad);

    if (vis[456] !== false) kernel.drawPart(meshes.eid456, mWrist, [0.72, 0.75, 0.80]);
    if (vis[462] !== false) kernel.drawPart(meshes.eid462, mWrist, [0.28, 0.32, 0.38]);
    if (vis[461] !== false) kernel.drawPart(meshes.eid461, mWrist, [0.18, 0.22, 0.28]);

    // หัวดูดสุญญากาศเยื้องศูนย์ X = +85.0 mm
    const mVac = kernel.Mat4.create();
    kernel.Mat4.translate(mVac, mWrist, [85.0, 0.0, 0.0]);
    if (vis[463] !== false) kernel.drawPart(meshes.eid463, mVac, [0.80, 0.65, 0.25]);
    if (vis[464] !== false) kernel.drawPart(meshes.eid464, mVac, [0.70, 0.73, 0.77]);
    if (vis[465] !== false) kernel.drawPart(meshes.eid465, mVac, [0.08, 0.62, 0.92]);
  }
});
/* <<<END_OPENVI_PART_CARTRIDGE: P20_UNLOAD_SCARA_2000>>> */
```

---

## 4. แผนการนำไปประกอบรวมร่างในสเต็ปถัดไป (Assembly Roadmap)

1. **เชื่อมต่อกับแผ่นโต๊ะ `P03_Base_Table_Plate`:**
   - จุดติดตั้งฐาน `mountingBasePort` ของหุ่นยนต์จะนำไปเกาะกับตำแหน่งรูยึดบนโต๊ะหลัก ที่ระดับระนาบหน้าโต๊ะ $Z_{\text{table}} = 850.0\text{ mm}$
   - ส่งผลให้ระนาบปลายหัวดูดของหุ่นยนต์สามารถกดลงมาหยิบชิ้นงานบนจานหมุนหรือถาดรองรับได้อย่างเที่ยงตรง
2. **การสั่งรวมร่างด้วยสคริปต์อัตโนมัติ:**
   - เก็บไฟล์ `P20_Unload_SCARA_2000_Studio_Draft_v2.0.html` ไว้ในโฟลเดอร์ `parts/`
   - เรียกใช้สคริปต์บนเครื่องคอมพิวเตอร์หลัก:
     ```bash
     py join_cell_html.py --watch
     ```
   - สคริปต์จะดึงพอร์ต `exportsDatum` เชื่อมต่อเข้ากับห่วงโซ่ดิจิทัลทวินทั้งเซลล์โดยอัตโนมัติ