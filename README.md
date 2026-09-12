# Discord Voice AFK Bot — Render Ready

บอต Discord สำหรับเข้า Voice Channel แบบ AFK และระบบส่งข้อความระหว่างห้องแชท

## Render

ใช้ค่าเหล่านี้:

- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Health Check Path: `/health`

Environment Variables:

| Key | ค่า |
|---|---|
| `TOKEN` | Discord Bot Token |
| `GUILD_ID` | Server ID |
| `PYTHON_VERSION` | `3.11.9` |
| `PYTHONUNBUFFERED` | `1` |

`PORT` **ไม่ต้องสร้างเอง** เพราะ Render จะกำหนดให้ Web Service อัตโนมัติ

## Discord

บอตต้องมีอย่างน้อย:
- View Channel
- Connect
- Send Messages / Embed Links สำหรับระบบ `/chat`

เปิด **Message Content Intent** ใน Discord Developer Portal ถ้าจะใช้ระบบ `/chat`

## คำสั่ง

- `/afk` — ให้บอตเข้าห้อง Voice ที่คุณอยู่ หรือเลือกห้อง
- `/off` — ออกจาก Voice และปิด AFK
- `/chat` — ตั้งค่าห้องต้นทางและห้องตอบกลับ
- `/chat_off` — ปิดระบบแชท

## สำคัญเรื่อง Render Free

โค้ดนี้ถูกจัดให้ทำงานเป็น Render Web Service และมี `/health` ที่ `0.0.0.0:$PORT` แล้ว

แต่ Render Free **ไม่สามารถรับประกันการออนไลน์ใน Voice 24/7 ได้** เพราะ Free Web Service จะ spin down หลังไม่มี inbound traffic ประมาณ 15 นาที และ filesystem เป็นแบบชั่วคราว ดังนั้นค่า `/chat` ที่บันทึกลง `chat_config.json` อาจหายเมื่อ instance restart/spin down/redeploy

ถ้าต้องการให้บอต Voice ออนไลน์ต่อเนื่องจริง ๆ ควรใช้ instance/บริการที่ไม่ spin down

## Security

อย่าใส่ Bot Token ลงใน GitHub หรือในโค้ด หาก Token เคยรั่ว ให้ Reset Token จาก Discord Developer Portal แล้วใส่ Token ใหม่ใน Render Environment Variables.
