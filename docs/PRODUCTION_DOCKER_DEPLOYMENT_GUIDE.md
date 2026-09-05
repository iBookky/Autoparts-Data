# คู่มือการติดตั้งและ Deploy ระบบ AutoParts Cross-Reference SaaS บน Server จริงด้วย Docker

คู่มือฉบับสมบูรณ์สำหรับการนำระบบ **AutoParts OEM vs Aftermarket Cross-Reference Platform** ขึ้นใช้งานจริงบน Production Server (Linux VPS / Dedicated Server) ด้วย **Docker & Docker Compose** พร้อมระบบรักษาความปลอดภัย **Caddy Reverse Proxy (Auto Let's Encrypt HTTPS/SSL)** และ **SQLite WAL Persistence**.

---

## 1. ภาพรวมสถาปัตยกรรม Production (Architecture Overview)

```
                       [ ผู้ใช้งาน / ลูกค้า / ทีมงาน ]
                                     │
                                     ▼ (Port 80 / 443 HTTPS)
               ┌───────────────────────────────────────────────┐
               │         Caddy Reverse Proxy (Container)       │
               │  - Auto Let's Encrypt / ZeroSSL (HTTPS)       │
               │  - Gzip / Zstd Compression                    │
               │  - Security Headers (HSTS, CSP, X-Frame)      │
               └──────────────────────┬────────────────────────┘
                                      │ (Internal Bridge Network: autoparts-net)
                                      ▼ (Port 8000)
               ┌───────────────────────────────────────────────┐
               │         FastAPI Web & API (Container)         │
               │  - Single Page Application (SPA Frontend)     │
               │  - Multi-Provider Automotive AI Engine        │
               │  - SaaS Billing, Quota & RBAC Middleware      │
               └──────────────────────┬────────────────────────┘
                                      │
                                      ▼ (Volume Mount: ./data)
               ┌───────────────────────────────────────────────┐
               │    Persistent Storage (Host: ./data)          │
               │  - SQLite Database: autoparts.db (WAL Mode)   │
               │  - Zero Data Loss on Container Rebuilds       │
               └───────────────────────────────────────────────┘
```

### การแยกเส้นทาง URL (Path Separation)
ระบบได้รับการออกแบบโครงสร้าง Path ให้แยกอย่างชัดเจนระหว่างกลุ่มลูกค้า (Customer) และทีมงานภายใน (Platform Owner / Admin):

| กลุ่มผู้ใช้งาน | เส้นทาง URL (Web Path) | คำอธิบายหน้าที่ |
| :--- | :--- | :--- |
| **ลูกค้า (Customer)** | `/` หรือ `/search` | ค้นหาอะไหล่, เทียบเบอร์ OEM/Aftermarket, ถอดรหัส VIN |
| **ลูกค้า (Customer)** | `/pricing` | หน้าราคาแพ็กเกจ SaaS, เลือก Upgrade / Subscribe |
| **ลูกค้า (Customer)** | `/portal` หรือ `/settings` | จัดการโปรไฟล์องค์กร, สมาชิกทีม, Role & Permission ลูกค้า |
| **ลูกค้า (Customer)** | `/crossref` | Cross-Reference Matrix & Interchange Catalog |
| **ลูกค้า (Customer)** | `/coverage` | ข้อมูล Data Coverage และรุ่นรถยนต์ที่รองรับ |
| **ลูกค้า (Customer)** | `/invoices` | ใบเสร็จและประวัติการชำระเงิน พร้อมภาษีมูลค่าเพิ่ม 7% |
| **ลูกค้า (Customer)** | `/api-hub` | จัดการ API Keys สำหรับ Developer & Integrations |
| **Platform Owner** | `/owner` | **Command Center สำนักงานใหญ่**: จัดการโมเดล AI, จัดการราคาแพ็กเกจ, ลูกค้า CRM 360, MRR/ARR |
| **Super Admin** | `/superadmin` | Technical Control Center: ตรวจสอบสถานะเซิร์ฟเวอร์, Web Crawler, RBAC Matrix |
| **Operator Admin** | `/admin` | Customer Operations Hub: ตรวจสอบคิวข้อมูลอะไหล่, จัดการผู้ใช้ |
| **Staff Member** | `/staff` | Task Workspace: งานขายและตรวจสอบรายการอะไหล่ |
| **Healthcheck** | `/health` หรือ `/api/health` | ตรวจสอบสถานะ Container และฐานข้อมูล (สำหรับ Uptime Monitor / Load Balancer) |

---

## 2. ข้อกำหนดของเซิร์ฟเวอร์ (Server Requirements)

* **ระบบปฏิบัติการแนะนำ**: Ubuntu 22.04 LTS หรือ Ubuntu 24.04 LTS (64-bit)
* **CPU**: 1 - 2 vCPU ขั้นต่ำ (แนะนำ 2 vCPU สำหรับโหลดที่มีผู้ใช้หลายคน)
* **RAM**: 2 GB ขั้นต่ำ (แนะนำ 4 GB สำหรับ AI processing caching)
* **SSD/Storage**: 20 GB ขึ้นไป
* **เครือข่าย / Ports**:
  * `Port 80` (HTTP สำหรับ Caddy Challenge และ Auto-Redirect ไปยัง HTTPS)
  * `Port 443` (HTTPS / HTTP3 สำหรับการเชื่อมต่อที่ปลอดภัย)
  * `Port 22` (SSH สำหรับการเข้าจัดการ Server)

---

## 3. ขั้นตอนที่ 1: ติดตั้ง Docker & Docker Compose V2 บน Ubuntu

เชื่อมต่อเข้าสู่เซิร์ฟเวอร์ผ่าน SSH:
```bash
ssh root@your-server-ip
```

รันคำสั่งเพื่ออัปเดตระบบและติดตั้ง Docker Engine:
```bash
# 1. อัปเดต package list
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 2. เพิ่ม Docker Official GPG Key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 3. ติดตั้ง Docker Repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. ติดตั้ง Docker Engine และ Docker Compose Plugin
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. ตรวจสอบเวอร์ชัน Docker
docker --version
docker compose version
```

---

## 4. ขั้นตอนที่ 2: ตั้งค่า Domain Name (DNS Settings)

1. เข้าไปยังผู้ให้บริการจดโดเมน หรือ Cloudflare ของท่าน
2. เพิ่ม **A Record** ชี้ไปยัง Public IP ของเซิร์ฟเวอร์:
   * **Type**: `A`
   * **Name**: `parts` (หรือ `@` หากใช้ root domain)
   * **Content / Target**: `IP_ของ_SERVER_ท่าน` (เช่น `128.199.xxx.xxx`)
   * **TTL**: Auto หรือ 300
   * **SSL/TLS Mode ใน Cloudflare**: หากเปิด Cloudflare Proxy แนะนำให้ตั้งค่า SSL เป็น **Full (Strict)** เพื่อให้ Caddy ออกใบรับรอง Let's Encrypt ได้อย่างถูกต้อง

---

## 5. ขั้นตอนที่ 3: Clone Codebase และเตรียม Configuration

สร้างโฟลเดอร์สำหรับแอปพลิเคชันบนเซิร์ฟเวอร์:
```bash
# สร้างโฟลเดอร์โปรเจกต์
mkdir -p /opt/autoparts
cd /opt/autoparts

# Clone โค้ดจาก Git Repository
git clone <YOUR_REPOSITORY_URL> .

# สร้างโฟลเดอร์สำหรับเก็บข้อมูลถาวร (Persistent Data)
mkdir -p ./data ./logs/caddy
sudo chown -R 1000:1000 ./data
```

### สร้างไฟล์ `.env` สำหรับ Production
คัดลอกไฟล์เทมเพลตและแก้ไขค่า:
```bash
cp .env.production.example .env
nano .env
```

แก้ไขค่าในไฟล์ `.env` ให้ตรงกับการใช้งานจริง:
```ini
# โดเมนที่ชี้มายังเซิร์ฟเวอร์นี้ (Caddy จะออก SSL ให้อัตโนมัติ)
DOMAIN_NAME=parts.yourcompany.com
PORT=8000
ENVIRONMENT=production

# ที่อยู่ Database SQLite ภายใน Container
DB_PATH=/app/data/autoparts.db

# API Keys ผู้ให้บริการ AI (สามารถใส่ที่นี่ หรือกรอกผ่านเมนู /owner บนเว็บได้เช่นกัน)
OPENAI_API_KEY=sk-proj-xxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxx
GEMINI_API_KEY=AIzaxxxxxx
DEEPSEEK_API_KEY=sk-xxxxxx
GROK_API_KEY=xai-xxxxxx
MISTRAL_API_KEY=xxxxxx
```
*(กด `Ctrl + O` แล้ว `Enter` เพื่อบันทึก และ `Ctrl + X` เพื่อออกจาก nano)*

---

## 6. ขั้นตอนที่ 4: สั่ง Deploy และเริ่มต้นการทำงาน

รันคำสั่ง Docker Compose เพื่อ Build Image และเริ่มต้นการทำงานในโหมด Background:

```bash
# Build และ Start Containers สำหรับ Production
docker compose -f docker-compose.prod.yml up -d --build
```

### ตรวจสอบสถานะการทำงาน
```bash
# ดูสถานะของ Containers
docker compose -f docker-compose.prod.yml ps

# ดู Logs การทำงานแบบ Real-time
docker compose -f docker-compose.prod.yml logs -f app
```

เมื่อระบบเริ่มทำงานเรียบร้อย ท่านสามารถเปิดเบราว์เซอร์และเข้าไปที่ `https://parts.yourcompany.com` จะพบว่า:
1. ระบบมีแม่กุญแจเขียว **HTTPS (SSL)** ให้อัตโนมัติ
2. ฐานข้อมูลเริ่มต้นจะถูกสร้างและทำ Migrations ให้อัตโนมัติใน `./data/autoparts.db`

---

## 7. ขั้นตอนที่ 5: การตั้งค่า Backup ฐานข้อมูล SQLite อัตโนมัติ (Automated Daily Backup)

ฐานข้อมูล SQLite จะเปิดโหมด **WAL (Write-Ahead Logging)** ไว้อัตโนมัติ เพื่อให้สำรองข้อมูลได้อย่างปลอดภัย 100% โดยไม่ต้องหยุดการทำงานของเซิร์ฟเวอร์

### 1. สร้างสคริปต์ Backup
```bash
sudo nano /opt/autoparts/backup_db.sh
```

วางโค้ดด้านล่างนี้ลงในไฟล์:
```bash
#!/bin/bash
# Script สำรองข้อมูล AutoParts SQLite Database

BACKUP_DIR="/opt/autoparts/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_FILE="/opt/autoparts/data/autoparts.db"
BACKUP_FILE="$BACKUP_DIR/autoparts_backup_$TIMESTAMP.db.gz"

mkdir -p "$BACKUP_DIR"

# ตรวจสอบว่าไฟล์ฐานข้อมูลมีอยู่จริง
if [ -f "$DB_FILE" ]; then
    # ใช้ sqlite3 .backup เพื่อความปลอดภัยของธุรกรรมระหว่างที่มีการเขียนข้อมูล
    sqlite3 "$DB_FILE" ".backup '/tmp/temp_backup.db'"
    gzip -c /tmp/temp_backup.db > "$BACKUP_FILE"
    rm -f /tmp/temp_backup.db
    echo "[$(date)] Backup completed successfully: $BACKUP_FILE"
else
    echo "[$(date)] Error: Database file not found at $DB_FILE"
    exit 1
fi

# ลบไฟล์สำรองข้อมูลที่เก่าเกิน 30 วัน เพื่อประหยัดพื้นที่ดิสก์
find "$BACKUP_DIR" -type f -name "*.db.gz" -mtime +30 -delete
```

### 2. ให้สิทธิ์การรันสคริปต์
```bash
chmod +x /opt/autoparts/backup_db.sh
```

### 3. ตั้งค่า Cron Job ให้ทำงานทุกวันเวลา 03:00 น.
```bash
crontab -e
```
เพิ่มบรรทัดนี้ลงไปท้ายไฟล์:
```cron
0 3 * * * /opt/autoparts/backup_db.sh >> /var/log/autoparts_backup.log 2>&1
```

---

## 8. ขั้นตอนที่ 6: การอัปเดตเวอร์ชันใหม่ (Zero-Downtime Update Workflow)

เมื่อมีการแก้ไขหรืออัปเดตโค้ดใหม่จาก Repository สามารถอัปเดตขึ้น Server ได้ง่ายๆ ใน 2 ขั้นตอน:

```bash
cd /opt/autoparts

# 1. ดึงโค้ดล่าสุด
git pull origin main

# 2. Rebuild และ Reload Containers แบบไม่กระทบข้อมูล
docker compose -f docker-compose.prod.yml up -d --build
```
> **หมายเหตุ**: ข้อมูลทั้งหมด (บัญชีผู้ใช้, อะไหล่, ประวัติการค้นหา, สถิติ AI) ที่เก็บใน `./data/autoparts.db` จะไม่สูญหายและเชื่อมต่อต่อเนื่องทันที

---

## 9. สรุปคำสั่งที่ใช้งานบ่อย (Cheat Sheet)

| การทำงาน | คำสั่ง (Command) |
| :--- | :--- |
| **ดู Logs Backend** | `docker compose -f docker-compose.prod.yml logs -f app` |
| **ดู Logs Caddy Proxy** | `docker compose -f docker-compose.prod.yml logs -f caddy` |
| **Restart ระบบทั้งหมด** | `docker compose -f docker-compose.prod.yml restart` |
| **หยุดการทำงาน** | `docker compose -f docker-compose.prod.yml down` |
| **ตรวจสอบ Healthcheck** | `curl -i http://localhost:8000/health` |
| **เข้า Shell ใน Container** | `docker compose -f docker-compose.prod.yml exec app /bin/bash` |
| **ดูการใช้ RAM / CPU** | `docker stats` |

---

## 10. การเข้าใช้งานครั้งแรก (Initial Access)

1. เข้าหน้าเว็บไซต์ตามโดเมนที่ตั้งไว้ เช่น `https://parts.yourdomain.com`
2. **เข้าสู่ระบบ Platform Owner Command Center**:
   * ไปที่ `https://parts.yourdomain.com/owner` หรือกดปุ่มเข้าสู่ระบบ
   * เข้าสู่ระบบด้วยบัญชีสิทธิ์ `OWNER` (เช่น บัญชี Owner เริ่มต้นของระบบ)
   * ไปที่แท็บ **"🧠 จัดการ AI Engine ยานยนต์"** เพื่อตรวจสอบโมเดล AI ที่เชื่อมต่อ, กดทดสอบ Ping Test, หรือกรอก API Key ใหม่ได้ทันที
3. **เข้าสู่ระบบลูกค้า (Customer Simulation)**:
   * ไปที่ `https://parts.yourdomain.com/search` เพื่อทดสอบค้นหาเบอร์อะไหล่
   * หรือกดปุ่ม `👁️ ดูมุมมองลูกค้า` บน Header ของ Platform Owner เพื่อสลับมุมมองไป-มาได้อย่างราบรื่น
