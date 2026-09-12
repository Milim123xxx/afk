# Discord Voice AFK Bot

บอต Discord สำหรับเข้าไปอยู่ในห้องโทร (Voice Channel) แบบ AFK พร้อมระบบส่งต่อข้อความระหว่างห้องแชทในเซิร์ฟเวอร์

## Environment Variables ที่ต้องใส่ใน Render

| Key | รายละเอียด |
|---|---|
| `TOKEN` | Bot Token จาก Discord Developer Portal |
| `GUILD_ID` | Server ID ของเซิร์ฟเวอร์ Discord |

ไม่ต้องใช้ `WELCOME_CHANNEL_ID`

## Render.com

- เลือก **New > Blueprint** แล้วเชื่อมต่อ Repository ที่มีไฟล์ `render.yaml` หรือสร้าง **Web Service** ด้วยค่าเหล่านี้:
- Build Command: `python -m pip install --upgrade pip && python -m pip install -r requirements.txt`
- Start Command: `python -u main.py`
- Health Check Path: `/health`

ถ้าใช้ `render.yaml` ระบบจะตั้งค่าให้ตามไฟล์ โดยต้องกรอกค่า `TOKEN` และ `GUILD_ID` ใน Render เอง ห้ามใส่เครื่องหมาย backticks หรือช่องว่างเกินมาในค่าเหล่านี้

หลัง Deploy ให้ตรวจใน Logs ว่ามีข้อความ `ออนไลน์แล้ว` และ `ซิงก์คำสั่งสำเร็จ` หากไม่พบ ให้ตรวจว่า Token ยังใช้ได้, `GUILD_ID` เป็น Server ID ตัวเลข, และบอตถูกเชิญเข้าเซิร์ฟเวอร์นั้นแล้ว

หลัง Deploy สำเร็จ ให้รัน `/chat` หนึ่งครั้งเพื่อเลือกห้อง ระบบจะเก็บค่าไว้ในไฟล์ของ instance ปัจจุบัน ไฟล์นี้ไม่ใช่พื้นที่ถาวรของ Render ดังนั้นหลัง redeploy/restart อาจต้องรัน `/chat` ใหม่ หากต้องการเก็บค่าถาวรต้องเปลี่ยนไปใช้ฐานข้อมูลหรือ Persistent Disk ที่รองรับโดยแผนบริการของ Render

**ข้อจำกัดสำคัญของ Render Free:** Web Service อาจเข้าสู่สถานะ sleep เมื่อไม่มี HTTP traffic ทำให้บอตหลุดจากห้อง Voice ได้ ไม่มีโค้ดฝั่งบอตที่รับประกันให้ Free Service ออนไลน์ตลอดเวลา หากต้องการ AFK ต่อเนื่องควรใช้แผนที่ไม่ sleep หรือย้ายเป็นบริการที่เหมาะกับงานรันตลอดเวลา

## วิธีใช้

1. เชิญบอตเข้าเซิร์ฟเวอร์
2. ให้บอตมีสิทธิ์ `View Channel` และ `Connect` ในห้องโทรที่ต้องการ
3. เข้าห้องโทรก่อน แล้วใช้ `/afk` ได้เลย บอตจะเข้าห้องเดียวกับคุณอัตโนมัติ หรือจะเลือกห้องในช่อง `channel` ก็ได้
4. ใช้ `/off` เมื่อให้บอตออกจากห้อง

## ระบบแชทสองห้องผ่านบอต

ผู้ดูแลใช้ `/chat` แล้วเลือก 2 ห้อง: `source` คือห้องที่สมาชิกใช้พิมพ์ข้อความ และ `reply_room` คือห้องสำหรับผู้ดูแลตอบกลับ เมื่อมีข้อความในห้องต้นทาง บอตจะส่งสำเนาไปห้องตอบกลับ ให้กด **Reply** ที่สำเนานั้น แล้วพิมพ์คำตอบ บอตจะส่งคำตอบกลับไปห้องต้นทางในชื่อบอต

ใช้ `/chat_off` เพื่อปิดระบบแชท

## ตั้งค่า Discord

ระบบ AFK ไม่ใช้ Privileged Gateway Intents แต่ระบบแชทอ่านข้อความในห้องต้นทางและห้องตอบกลับ จึงต้องเปิด **Message Content Intent** ใน Discord Developer Portal > Bot > Privileged Gateway Intents

## วิธีหา ID

เปิด Developer Mode ใน Discord ที่ **User Settings > Advanced > Developer Mode** จากนั้นคลิกขวาที่ชื่อเซิร์ฟเวอร์และเลือก **Copy Server ID** เพื่อนำไปใส่ใน `GUILD_ID`

## ข้อควรระวัง

ห้ามเผยแพร่ Bot Token หาก Token รั่ว ให้ Reset Token ทันทีใน Discord Developer Portal

Render Free อาจพัก Web Service เมื่อไม่มีการใช้งาน จึงอาจทำให้บอตหลุดจากห้องโทรได้ หากต้องการออนไลน์ต่อเนื่องควรใช้บริการหรือแผนที่ไม่ Sleep
