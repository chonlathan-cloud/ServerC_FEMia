📄 ฉบับที่ 1: TDD - MIA-Data-Service (Server C)
Role: Backend for Admin Portal & Data Analytics Tech Stack: Python 3.11+, FastAPI, SQLModel (AsyncPG) Port: 8002 (เพื่อไม่ให้ชนกับ Server B: 8000 และ Server A: 8001)

1. Project Structure
(เน้นการ Reuse Code จาก Server B)

mia-data/
├── requirements.txt          # Copy from Server B
├── .env                      # Config: DB_URL (Same as B), SERVICE_KEY
├── main.py                   # Entry point
└── src/
    ├── config.py             # Load Env
    ├── database.py           # Copy from Server B (Shared Connection)
    ├── security.py           # Copy from Server B (Firebase Verify)
    ├── models.py             # Copy from Server B (Shared Schema)
    ├── routers/
    │   └── admin.py          # ⭐ New: Logic สำหรับ Admin ทั้งหมด
    └── services/
        └── bigquery_service.py # (Placeholder for Future)
2. Key Features & API Endpoints (src/routers/admin.py)
ต้องมีการเช็ค Depends(get_current_admin_user) ทุกครั้ง

GET /admin/shops

Logic: Query ตาราง Shop ทั้งหมด (ไม่กรอง owner_uid) พร้อม Pagination

Response: List of Shops (ID, Name, Tier, Owner Email, LINE Connect Status)

GET /admin/shops/{shop_id}

Logic: ดึงรายละเอียดร้านเจาะจง รวมถึง line_config (เพื่อดูว่าเชื่อมต่อหรือยัง)

PATCH /admin/shops/{shop_id}/integration

Logic: รับค่า channelSecret, accessToken, botId แล้วอัปเดตลง JSON line_config

Use Case: Admin เป็นคนกรอก Key ให้ลูกค้า

PATCH /admin/shops/{shop_id}/tier

Logic: เปลี่ยน Package (Free -> Pro) อัปเดตคอลัมน์ tier

POST /admin/broadcast/global

Logic: (Future) ส่งข้อความหาลูกค้าทุกร้าน (ต้องระวัง Rate Limit)

3. Database Connection
Connection: เชื่อมต่อ PostgreSQL ก้อนเดียวกับ Server B (DB_URL)

Constraint: อ่าน/เขียน ตาราง shops ได้อิสระ แต่ห้ามแก้ Schema (ต้องแก้ที่ Server B เป็นหลักเพื่อความไม่งง)