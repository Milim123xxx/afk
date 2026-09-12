# Discord Voice AFK Bot

บอต Discord สำหรับเข้าไปอยู่ในห้องโทร (Voice Channel) แบบ AFK พร้อมปิดไมค์ ปิดเสียงตัวเอง และเชื่อมต่อกลับเมื่อหลุด

## Environment Variables ที่ต้องใส่ใน Render

| Key | รายละเอียด |
|---|---|
| `TOKEN` | Bot Token จาก Discord Developer Portal |
| `GUILD_ID` | Server ID ของเซิร์ฟเวอร์ Discord |

ไม่ต้องใช้ `WELCOME_CHANNEL_ID`

## Render.com

- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Health Check Path: `/health`

ถ้าใช้ `render.yaml` ระบบจะตั้งค่าให้ตามไฟล์ แต่ต้องกรอกค่า `TOKEN` และ `GUILD_ID` ใน Render เอง

## วิธีใช้

1. เชิญบอตเข้าเซิร์ฟเวอร์
2. ให้บอตมีสิทธิ์ `View Channel` และ `Connect` ในห้องโทรที่ต้องการ
3. ใช้ `/afk` แล้วเลือกห้องโทร
4. ใช้ `/off` เมื่อให้บอตออกจากห้อง

## ตั้งค่า Discord

บอตเวอร์ชันนี้ไม่ใช้ Privileged Gateway Intents จึงไม่ต้องเปิด Server Members Intent หรือ Message Content Intent สำหรับระบบ AFK

## วิธีหา ID

เปิด Developer Mode ใน Discord ที่ **User Settings > Advanced > Developer Mode** จากนั้นคลิกขวาที่ชื่อเซิร์ฟเวอร์และเลือก **Copy Server ID** เพื่อนำไปใส่ใน `GUILD_ID`

## ข้อควรระวัง

ห้ามเผยแพร่ Bot Token หาก Token รั่ว ให้ Reset Token ทันทีใน Discord Developer Portal

Render Free อาจพัก Web Service เมื่อไม่มีการใช้งาน จึงอาจทำให้บอตหลุดจากห้องโทรได้ หากต้องการออนไลน์ต่อเนื่องควรใช้บริการหรือแผนที่ไม่ Sleep
