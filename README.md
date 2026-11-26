# OpenVI_TR1100_CELL_TWIN — Machine-as-Code & 3D WebGL Cartridge Factory

โปรเจกต์ต้นแบบ **3D Digital Twin เครื่องจักรอัตโนมัติขนาดใหญ่** ภายใต้แนวคิด **Machine-as-Code** และ **Child-HTML Joiner Pattern** ออกแบบมาเพื่อแก้ปัญหาความจำแชตเต็ม (Context Overflow) และปัญหาไฟล์โมเดล 3 มิติบวม โดยแยกพัฒนาและตรวจรับชิ้นส่วนย่อยทีละไฟล์ (`Single-File Child HTML` ที่รันตัวเองได้แบบออฟไลน์ 100%) แล้วสกัดเฉพาะบล็อกตลับโมดูล (`OpenVIRegistry Cartridge`) มารวมร่างเข้ากับโครงหน้าเว็บแม่เป็นเครื่องจักรเต็มเซลล์ที่ลื่นไหลระดับ 60 FPS

---

## 1. สารบัญไฟล์หลักในโปรเจกต์ (Project Inventory)

ตารางด้านล่างสรุปบทบาทของไฟล์เครื่องมือ สคริปต์ ตลับพาร์ทลูก และเอกสารสถาปัตยกรรมทั้งหมดที่จัดเตรียมไว้ในคลังโปรเจกต์:

| หมวดหมู่ | ชื่อไฟล์ / รหัสเอกสาร | ประเภทไฟล์ | บทบาทหน้าที่ในสายการผลิต |
| :--- | :--- | :--- | :--- |
| **กฎและทักษะ AI** | `AGENTS.md` | Markdown (`.md`) | กฎเหล็กพิกัด Z-Up หน่วยวิศวกรรม และข้อบังคับสำหรับ AI Coder ทุกตัว |
| **กฎและทักษะ AI** | `SKILL.md` | Markdown (`.md`) | ชุดคำสั่งทักษะ `openvi-step-to-webgl-factory` สำหรับตั้งค่าในเมนูทักษะ |
| **คัมภีร์เปิดแชตใหม่** | `STEP_TO_TWIN_PLAYBOOK.md` | Markdown (`.md`) | คู่มือแนบเปิดหัวแชตใหม่เพื่อผ่าไฟล์ STEP เป็นตลับ 3D WebGL รายชิ้น |
| **สคริปต์ระบบ** | `bootstrap_machine_repo.py` | Python 3 (`.py`) | สคริปต์กางโครงสร้าง 6 โฟลเดอร์ย่อย การ์ดพาร์ท และรันเทสต์ทางกล 5 ข้อ |
| **สคริปต์ระบบ** | `join_cell_html.py` | Python 3 (`.py`) | สคริปต์กวาดดึงตลับ `CARTRIDGE` จากไฟล์ลูกมารวมร่างในไฟล์แม่ (รองรับ `--watch`) |
| **สคริปต์ระบบ** | `step_dissector.py` | Python 3 (`.py`) | สคริปต์ย่อไฟล์ `.step` ขนาดใหญ่ (> 2 MB) เป็นไฟล์สรุปเรขาคณิต `_step_dna.json` |
| **โครงเว็บแม่** | `master_shell_template.html` | WebGL HTML5 | หน้าเว็บแม่พร้อมเอนจิน B-Rep กลาง ห่วงโซ่พิกัด และปุ่มเสียบไฟล์ลูกรวมร่างสด |
| **ตลับพาร์ทลูก** | `P01_Adjuster_Set_8Body_BRep_Studio_v2.0.html` | WebGL HTML5 | ชุดมุมฐานเครื่องระดับ B-Rep 8 ก้อน (เพลทหนา 15 mm + ล้อ `CJHB75` + ขาหยั่ง `M16`) |
| **ตลับพาร์ทลูก** | `P02_Common_Profile_Base_Frame_Studio_v1.0.html` | WebGL HTML5 | คลังโปรไฟล์อลูมิเนียมกลาง (`40x40`, `40x80`, `80x80`) + โครงฐาน 4 มุมและใบสั่งตัด |
| **ต้นแบบรุ่นแรก** | `L01_3Part_Corner_Assembly_Solid1_CJHB75_CAJPJ16_v1.0.html` | WebGL HTML5 | ต้นแบบทดสอบแนวคิดชุดประกอบมุมฐานเครื่อง 3 ชิ้นรุ่นแรก |
| **เอกสารสเปก** | `DG-2026-101` | Google Docs | สถาปัตยกรรมแยกชิ้นส่วนเป็น Single-File HTML ลูกและระบบดึงตลับรวมร่าง |
| **เอกสารสเปก** | `DG-2026-102` | Google Docs | สถาปัตยกรรมโมดูลโปรไฟล์อลูมิเนียมกลางน้ำหนักเบาและการยืดความยาวด้วยเมทริกซ์ 4 × 4 |
| **เอกสารสเปก** | `DG-2026-103` | Google Docs | คัมภีร์แม่บทสกัดไฟล์ STEP สู่ตลับ 3D WebGL ฉบับอ่านทบทวนออนไลน์ |

---

## 2. โครงสร้างโฟลเดอร์เมื่อกางลงเครื่องคอมพิวเตอร์ (Local Directory Tree)

เมื่อดาวน์โหลดโฟลเดอร์โปรเจกต์ลงมาไว้ในเครื่องแล้วรันสคริปต์ติดตั้ง ระบบจะจัดเรียงโครงสร้างมาตรฐานดังนี้:

```text
OpenVI_TR1100_CELL_TWIN/
├── README.md                                  # สารบัญและคู่มือการรันโปรเจกต์ฉบับนี้
├── AGENTS.md                                  # กฎปฏิบัติการสำหรับ AI Coder Agent
├── SKILL.md                                   # นิยามทักษะ openvi-step-to-webgl-factory
├── STEP_TO_TWIN_PLAYBOOK.md                   # คัมภีร์แม่บทสำหรับโยนเปิดหัวใน New Chat
├── bootstrap_machine_repo.py                  # สคริปต์สร้างโฟลเดอร์ 00..05 และรัน Unit Test
├── join_cell_html.py                          # สคริปต์ดึง Cartridge จากไฟล์ลูกมารวมเป็นไฟล์แม่
├── step_dissector.py                          # สคริปต์สกัดไฟล์ STEP ขนาดใหญ่เป็น _step_dna.json
├── master_shell_template.html                 # โครงหน้าเว็บแม่ (Master Cell Shell)
├── 00_specs/                                  # ค่าคงที่หลัก (CELL_CONSTANTS.json)
├── 01_catalog_parts/                          # การ์ดพาร์ทมาตรฐาน MISUMI / WEISS
├── 02_patterns/                               # แม่แบบวิศวกรรมใช้ซ้ำ (PATTERN_DNA)
├── 03_assembly_layers/                        # ลำดับการประกอบจากพื้นขึ้นยอดเครื่อง (L01 -> L05)
├── 04_cad_distiller/                          # สคริปต์ส่งออกข้อมูลจาก Autodesk Fusion 360
└── 05_tests_and_webgl/                        # ชุดทดสอบสมการทางกลและโฟลเดอร์รวมร่างเว็บ 3D
    ├── verify_machine_repo.py                 # สคริปต์ตรวจสมการความปลอดภัยทางกล 5 ข้อ
    ├── DIST_FULL_CELL_TWIN.html               # [ผลลัพธ์อัตโนมัติ] ไฟล์แม่ที่รวมร่างพาร์ทลูกครบทุกใบ
    └── parts/                                 # โฟลเดอร์วางไฟล์ลูก P01_*.html, P02_*.html, ...
```

---

## 3. วิธีรันและใช้งานทั้งระบบ (4 Core Workflows)

ระบบทั้งหมดใช้เฉพาะไลบรารีมาตรฐานติดเครื่อง Python 3.12+ (ไม่ต้องติดตั้งแพ็กเกจภายนอกเพิ่มเติม) และเบราว์เซอร์ทั่วไป (Chrome / Edge)

### เวิร์กโฟลว์ที่ 1 — กางโครงสร้างโปรเจกต์และรันตรวจสมการทางกล (Initial Setup & Unit Tests)

เปิดเทอร์มินัลในโฟลเดอร์โปรเจกต์แล้วรันคำสั่งเดียวเพื่อสร้างโฟลเดอร์ย่อย `00_specs` ถึง `05_tests_and_webgl` พร้อมตรวจสอบสมการความปลอดภัยทางกลทั้ง 5 ข้อ:

```bash
py bootstrap_machine_repo.py
```

หากมีการแก้ไขตัวเลขความสูงหรือสเปกพาร์ทใน `00_specs/CELL_CONSTANTS.json` สามารถรันตรวจซ้ำได้ตลอดเวลาด้วยคำสั่ง:

```bash
py 05_tests_and_webgl/verify_machine_repo.py
```

### เวิร์กโฟลว์ที่ 2 — การรวมร่างไฟล์พาร์ทลูกเข้าสู่หน้าเว็บแม่ (Joining Child Cartridges)

ทำได้ 2 วิธีตามความสะดวก:

1. **วิธีรวมร่างสดผ่านหน้าเบราว์เซอร์ทันที (ไม่ต้องรันคำสั่งใดๆ):**
   - ดับเบิลคลิกเปิดไฟล์ `master_shell_template.html` บนเบราว์เซอร์โดยตรง
   - คลิกปุ่ม **`+ เสียบไฟล์ลูก (.html)`** บนแถบด้านบน แล้วเลือกไฟล์ `P01_Adjuster_Set_8Body_BRep_Studio_v2.0.html` และ `P02_Common_Profile_Base_Frame_Studio_v1.0.html` ระบบจะดูดตลับโมดูลขึ้นมาประกอบร่างบนพื้นโรงงาน Z = 0.0 mm ทันทีโดยไม่ติดบล็อก CORS
2. **วิธีคอมไพล์รวมเป็นไฟล์เดี่ยวออฟไลน์ด้วย Python (`DIST_FULL_CELL_TWIN.html`):**
   - ย้ายหรือคัดลอกไฟล์ลูก `P01_*.html`, `P02_*.html`, ... ไปไว้ในโฟลเดอร์ `parts/` (หรือ `05_tests_and_webgl/parts/`) และวาง `master_shell_template.html` ไว้คู่กัน
   - รันสคริปต์รวมร่าง (เติม `--watch` เพื่อให้ประกอบร่างใหม่อัตโนมัติทุกครั้งที่กดบันทึกไฟล์ลูก):

```bash
py join_cell_html.py --watch
```

### เวิร์กโฟลว์ที่ 3 — การเปิดแชตใหม่เพื่อปั้นพาร์ทถัดไปจากไฟล์ STEP (Stateless Part Factory)

เมื่อต้องการสร้างชิ้นส่วนถัดไป (เช่น `P03` แผ่นโต๊ะและจานหมุน `TR1100`, `P04` เกาะกลางหัววัดไฟแรงสูง, หรือ `P05` แขนกล `SCARA`) โดยไม่ให้ความจำแชตเต็ม:

1. **กรณีไฟล์ `.step` ขนาดไม่เกิน 2 MB:** เปลี่ยนนามสกุลไฟล์เป็น `.step.txt` แล้วเปิดแชตใหม่ โยนไฟล์ `STEP_TO_TWIN_PLAYBOOK.md` (หรือเรียกใช้ทักษะ `openvi-step-to-webgl-factory`) คู่กับไฟล์ `.step.txt` และภาพหน้าจอจากโปรแกรม CAD 1 ภาพ
2. **กรณีไฟล์ `.step` ขนาดใหญ่เกิน 2 MB:** รันสคริปต์ย่อไฟล์บนเครื่องคอมพิวเตอร์ก่อนเพื่อบีบเป็นไฟล์สรุป `_step_dna.json` ขนาดประมาณ 10–30 KB แล้วนำไฟล์ `.json` นั้นแนบเข้าแชตใหม่แทน:

```bash
py step_dissector.py BigSubAssembly.step
```

### เวิร์กโฟลว์ที่ 4 — การตรวจดูแยกชิ้นส่วน (Standalone Component QC)

ไฟล์ลูกทุกใบ (`P01_*.html`, `P02_*.html`, ...) มีเปลือกหน้าเว็บทดสอบตัวเองในตัว สามารถดับเบิลคลิกเปิดดูแยกชิ้นเพื่อใช้เครื่องมือ `Section Analysis` ผ่าดูเกลียวใน ลูกหมากหัวบอล บ่าคว้าน `Counterbore` และปรับโหมดความละเอียด `LOD-0` / `LOD-1` ได้โดยอิสระทุกใบ

---

## 4. กฎเหล็กทางวิศวกรรมของโปรเจกต์ (Engineering Invariants)

1. **ระบบพิกัดโลก (`Right-Handed Z-Up`):** พื้นโรงงานคือ Z = 0.0 mm แกน +Z ชี้ขึ้นแนวดิ่ง แกน +X ชี้ไปทางสายพานลำเลียงขาออก และจานหมุน `TR1100-30-F` หมุนแบ่งจังหวะตามเข็มนาฬิกา (`CW` ขั้นละ -12.0° จำนวน 30 สถานี)
2. **ห่วงโซ่พิกัดต่อเนื่อง (`Bottom-Up Datum Chain`):** ห้ามใส่ตัวเลขความสูงลอยตัว ทุกชั้นรับค่าความสูงจาก `exportsDatum()` ของชั้นล่างเสมอ (เช่น ในโหมดตั้งเครื่องตามไฟล์ STEP ขาหยั่งยกแผ่นเพลทมุมหนา 15.0 mm ให้อยู่ที่ระดับ 110.0 / 125.0 mm ลูกล้อลอยพ้นพื้น +4.0 mm และต่อเสา `40x80` สูง 720.0 mm ขึ้นไปรับโครงแผ่นโต๊ะที่ 845.0 mm)
3. **งบประมาณสามเหลี่ยมและระบบตัดวงจร (`Performance & Safety Gate`):** รองรับเมช 2 ระดับ (`lod0` สำหรับส่องตรวจแบบระยะใกล้ และ `lod1` สำหรับเดินเครื่องเต็มเซลล์ไม่เกิน 120,000 สามเหลี่ยม) พร้อมตัวตัดวงจรอัตโนมัติในไฟล์แม่หากเวลาวาดเฟรมเกิน 20.0 ms ติดต่อกัน 15 เฟรม
4. **ความสะอาดด้านทรัพย์สินทางปัญญา (`Projector Safety Check`):** ห้ามเก็บชื่อลูกค้า รหัสผลิตภัณฑ์ลับ หรือหมายเลขซีเรียลไว้ในโค้ดและเอกสารทั้งหมด โดยแทนที่ชิ้นงานทดสอบด้วยรหัสกลาง `UUT_DUMMY` เท่านั้น

---

## 5. สารบัญลิงก์ไฟล์ทั้งหมดบน Google Drive (Cloud File Links)

รายการด้านล่างเชื่อมต่อไปยังโฟลเดอร์รากและไฟล์ต้นฉบับทุกชิ้นที่บันทึกไว้บน Google Drive ของโปรเจกต์:

- โฟลเดอร์หลักของโปรเจกต์: [OpenVI_TR1100_CELL_TWIN](https://drive.google.com/drive/folders/1xfEIQFtVDmNc0XicEBh6Ulce5GIVHe1-)
- กฎปฏิบัติการสำหรับ AI Coder: [AGENTS.md](https://docs.google.com/document/d/1cVe4e7Ll6xMqyKCBIlN0xF9WZGLOUtGc/edit?usp=drivesdk&ouid=117359208261652803420&rtpof=true&sd=true)
- ไฟล์นิยามทักษะสำหรับเมนูทักษะ: [SKILL.md](https://docs.google.com/document/d/1EKX8S8-LnQSl-MMDiyFJj9SVbUtKSZ5u/edit?usp=drivesdk&ouid=117359208261652803420&rtpof=true&sd=true)
- คัมภีร์แม่บทแนบเปิดหัวแชตใหม่ฉบับ `.md`: [STEP_TO_TWIN_PLAYBOOK.md](https://docs.google.com/document/d/1jWjep5HhRYo_nplfzjb5WN_0WnNm0ZZC/edit?usp=drivesdk&ouid=117359208261652803420&rtpof=true&sd=true)
- สคริปต์กางโครงสร้างโปรเจกต์และรันเทสต์ทางกล: [bootstrap_machine_repo.py](https://drive.google.com/file/d/1_hr7_1ZIT9SLv3R-qpcmhF7qMa_Kmswq/view?usp=drivesdk)
- สคริปต์ดึงตลับโมดูลจากไฟล์ลูกมารวมร่าง: [join_cell_html.py](https://drive.google.com/file/d/1DgiZImlVpkrNZeQLL8kU1ErjFpyOW3Ed/view?usp=drivesdk)
- สคริปต์ย่อไฟล์ STEP ขนาดใหญ่เป็น JSON: [step_dissector.py](https://drive.google.com/file/d/1dvhqQhnTvEPu2dEzr0aTIff5wRjnTfMo/view?usp=drivesdk)
- โครงหน้าเว็บแม่สำหรับรวมร่างทั้งเซลล์: [master_shell_template.html](https://drive.google.com/file/d/1LfHZU-Phi7Anfcxiim67zCFADDtwdaao/view?usp=drivesdk)
- ตลับพาร์ทลูก `P01` ชุดล้อและขาหยั่ง B-Rep 8 ก้อน: [P01_Adjuster_Set_8Body_BRep_Studio_v2.0.html](https://drive.google.com/file/d/1-KRPjo5IvBkio3Q7QO9BMQXxX9RNIqS_/view?usp=drivesdk)
- ตลับพาร์ทลูก `P02` คลังโปรไฟล์กลางและโครงฐานเครื่อง: [P02_Common_Profile_Base_Frame_Studio_v1.0.html](https://drive.google.com/file/d/1YHL9iMhLvmLcFAiMb-DV8n6eOdYZ_9RS/view?usp=drivesdk)
- ต้นแบบชุดประกอบมุมฐานเครื่อง 3 ชิ้นรุ่นแรก: [L01_3Part_Corner_Assembly_Solid1_CJHB75_CAJPJ16_v1.0.html](https://drive.google.com/file/d/1MgcyNn8ktpvasq0q6Q6_gBj4k0i1-G7J/view?usp=drivesdk)
- เอกสารสถาปัตยกรรม `DG-2026-101`: [DG-2026-101 — Child-HTML Joiner Pattern](https://docs.google.com/document/d/1BBkU5NhOxVjmNu4rNjpd0TQXo0T4SRHK2LguJpKMnRI/edit?usp=drivesdk)
- เอกสารสถาปัตยกรรม `DG-2026-102`: [DG-2026-102 — Common Extrusion Profile Engine](https://docs.google.com/document/d/1z1tlTkU9RjJRaXc4ajMN5KagoDeMChNtXb5scNREcd0/edit?usp=drivesdk)
- เอกสารคัมภีร์แม่บท `DG-2026-103`: [DG-2026-103 — STEP_TO_TWIN_PLAYBOOK](https://docs.google.com/document/d/1GH574OeVbJ5cmuKztzVVIA60e3fuoj40KUXXxMQ5QqE/edit?usp=drivesdk)
