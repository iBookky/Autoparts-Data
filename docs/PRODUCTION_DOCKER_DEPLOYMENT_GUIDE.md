# คู่มือการติดตั้งและ Deploy ระบบ AutoParts Cross-Reference SaaS บน Server จริง

คู่มือฉบับสมบูรณ์สำหรับการนำระบบ **AutoParts OEM vs Aftermarket Cross-Reference Platform** ขึ้นใช้งานจริงบน Production Server โดยแบ่งออกเป็น 2 แนวทางหลักตามสภาพแวดล้อมของท่าน:

* **ส่วนที่ 1 (แนะนำสำหรับท่าน)**: การติดตั้งบนเซิร์ฟเวอร์ที่ใช้ **Plesk Control Panel + Docker Extension**
* **ส่วนที่ 2**: การติดตั้งบน **Linux VPS ทั่วไป (Ubuntu + Docker Compose + Caddy Auto-SSL)**

---

# 🌟 ส่วนที่ 1: การติดตั้งบนเซิร์ฟเวอร์ Plesk Control Panel (Plesk + Docker Extension)

เมื่อเซิร์ฟเวอร์ของท่านใช้งาน **Plesk Obsidian** และติดตั้ง **Docker Extension** เรียบร้อยแล้ว ท่านสามารถ Deploy และดูแลรักษาระบบได้อย่างง่ายดายผ่านหน้าเว็บ UI ของ Plesk โดยไม่ต้องกังวลเรื่องการจัดการ SSL หรือ Web Server พอร์ตชนกัน เพราะ **Plesk Nginx จะทำหน้าที่เป็น Reverse Proxy และจัดการ SSL ให้โดยอัตโนมัติ**

```
                       [ ผู้ใช้งาน / ลูกค้า / ทีมงาน ]
                                     │
                                     ▼ (Port 80 / 443 HTTPS)
               ┌───────────────────────────────────────────────┐
               │              Plesk Nginx Web Server           │
               │  - SSL It! / Free Let's Encrypt Certificate   │
               │  - Auto HTTP -> HTTPS Redirection             │
               │  - Plesk Docker Proxy Rule                    │
               └──────────────────────┬────────────────────────┘
                                      │ (Internal Proxy: http://127.0.0.1:8000)
                                      ▼
               ┌───────────────────────────────────────────────┐
               │       AutoParts App (Docker Container)        │
               │  - FastAPI Web & API Service (Port 8000)      │
               │  - Multi-Provider Automotive AI Engine        │
               │  - Commercial Billing & RBAC Protection       │
               └──────────────────────┬────────────────────────┘
                                      │
                                      ▼ (Volume Mapping)
               ┌───────────────────────────────────────────────┐
               │    Host Path: /var/www/vhosts/.../data        │
               │  - SQLite Database: parts_cross_ref.db (WAL)  │
               │  - ข้อมูลไม่สูญหายเมื่อ Rebuild Container    │
               └───────────────────────────────────────────────┘
```

---

## ขั้นตอนที่ 1.1: เพิ่มโดเมนและออกใบรับรอง SSL ฟรีบน Plesk

1. เข้าสู่ **Plesk Control Panel**
2. ไปที่เมนู **Websites & Domains** > คลิก **Add Domain** หรือ **Add Subdomain**
   * **Domain Name**: เช่น `parts.yourdomain.com`
   * **Hosting Type**: Website Hosting
3. ติดตั้ง **SSL Certificate (Let's Encrypt)** ฟรี 1-Click:
   * ในหน้าการตั้งค่าโดเมน คลิกที่ **SSL/TLS Certificates** (หรือ **SSL It!**)
   * คลิกปุ่ม **Install** ภายใต้หัวข้อ **Let's Encrypt**
   * ติ๊กเลือก *Secure the domain name* และ *Redirect from HTTP to HTTPS*
   * กด **Get it free** — โดเมนของท่านจะมีแม่กุญแจเขียว (HTTPS) ทันที

---

## ขั้นตอนที่ 1.2: อัปโหลดโค้ดขึ้นเซิร์ฟเวอร์ Plesk

ท่านสามารถนำโค้ดขึ้นเซิร์ฟเวอร์ได้ 2 วิธี:

### วิธี A: ผ่าน Plesk Git Extension (แนะนำ - อัปเดตโค้ดอัตโนมัติ)
1. ในหน้าโดเมนบน Plesk คลิกที่ **Git**
2. ใส่ **Repository URL** และเลือก Branch `main`
3. ตั้งค่า **Target Directory**: เช่น `/autoparts-app`
4. กด **OK** เพื่อดึงโค้ดลงมา

### วิธี B: ผ่าน SSH / File Manager
1. เชื่อมต่อ SSH เข้า Server:
   ```bash
   cd /var/www/vhosts/yourdomain.com/
   git clone <YOUR_REPOSITORY_URL> autoparts-app
   cd autoparts-app
   ```
2. สร้างโฟลเดอร์สำหรับเก็บฐานข้อมูลถาวร:
   ```bash
   mkdir -p /var/www/vhosts/yourdomain.com/data
   mkdir -p /var/www/vhosts/yourdomain.com/backups
   chmod 777 /var/www/vhosts/yourdomain.com/data
   ```

---

## ขั้นตอนที่ 1.3: สั่ง Build Image และรัน Container บน Plesk

ท่านสามารถเลือกวิธีที่สะดวกที่สุดได้ 3 วิธี:

### วิธีที่ 1: ใช้สคริปต์ 1-Click บน Plesk SSH / Terminal (แนะนำ - ง่ายและเร็วที่สุด)
เพียงต่อ SSH เข้า Server หรือเปิด **Plesk Terminal** ในโฟลเดอร์แอป แล้วสั่ง:
```bash
cd /var/www/vhosts/yourdomain.com/autoparts-app
bash deploy_plesk_image.sh
```
*(สคริปต์จะทำการสร้างโฟลเดอร์ Data, Build Docker Image, และสั่งรัน Container บน `127.0.0.1:8000` ให้อัตโนมัติในคำสั่งเดียว)*

---

### วิธีที่ 2: Build Image เป็นไฟล์ `.tar.gz` แล้วอัปโหลดขึ้น Plesk (ไม่ต้อง Build บน Server)
หากท่านต้องการ Build Image บนเครื่องของท่าน แล้วอัปโหลดเป็นไฟล์ก้อนเดียวขึ้น Plesk:
1. **บนเครื่องของท่าน**: รันสคริปต์ส่งออก Image
   ```bash
   bash export_docker_image.sh
   ```
   *(จะได้ไฟล์ `autoparts-image.tar.gz`)*
2. **อัปโหลดไฟล์ `autoparts-image.tar.gz`** ขึ้น Plesk (ผ่าน Plesk File Manager หรือ SFTP)
3. **บน Plesk SSH / Terminal**: โหลด Image และสั่งรัน
   ```bash
   docker load < autoparts-image.tar.gz
   
   docker run -d \
     --name autoparts-app \
     --restart unless-stopped \
     -p 127.0.0.1:8000:8000 \
     -v /var/www/vhosts/yourdomain.com/data:/app/data \
     autoparts-app:latest
   ```

---

### วิธีที่ 3: Build & Run ผ่านหน้าเว็บ Plesk Docker UI
1. ในเมนูด้านซ้ายของ Plesk คลิกที่ **Docker**
2. คลิก **Build Image** > เลือก Path ไปยังโฟลเดอร์โปรเจกต์ หรือรัน `docker build -t autoparts-app:latest .`
3. ในหน้า Image คลิก **Run (Advanced)**:
   * **Container Name**: `autoparts-app`
   * **Automatic start after system reboot**: ✅ ติ๊กถูก
   * **Port Mapping**:
     * Host Port: `8000` (หรือ `127.0.0.1:8000`)
     * Container Port: `8000` (Protocol: TCP)
   * **Volume Mapping**:
     * Host Path: `/var/www/vhosts/yourdomain.com/data`
     * Container Path: `/app/data`
   * **Environment Variables**:
     * `PORT` = `8000`
     * `DB_PATH` = `/app/data/autoparts.db`
     * `ENVIRONMENT` = `production`
4. กด **OK** เพื่อเริ่มการทำงานของ Container

---

## ขั้นตอนที่ 1.4: ตั้งค่า Plesk ให้ชี้โดเมนเข้า Docker Container (Docker Proxy Rule)

เพื่อให้ผู้ใช้งานที่เข้าผ่าน `https://parts.yourdomain.com` สามารถเข้าถึง Container ได้ทันที:

### วิธีที่ 1: ใช้เมนู Docker Proxy Rules ของ Plesk (ง่ายที่สุด)
1. ไปที่ **Websites & Domains** > เลือกโดเมน `parts.yourdomain.com`
2. คลิกที่เมนู **Docker Proxy Rules**
3. คลิก **Add Rule**
4. เลือก Container: `autoparts-app` และ Port: `8000 (TCP)`
5. กด **OK** — Plesk จะเชื่อมต่อ Domain เข้ากับ Docker ให้อัตโนมัติทันที

---

### วิธีที่ 2: ตั้งค่าผ่าน Apache & Nginx Settings (ประสิทธิภาพสูงสุด)
หากท่านต้องการตั้งค่า WebSocket และ Proxy Headers เอง:
1. ไปที่ **Websites & Domains** > เลือกโดเมน `parts.yourdomain.com`
2. คลิก **Apache & Nginx Settings**
3. เลื่อนลงมาที่หัวข้อ **Additional Nginx directives** วางโค้ดด้านล่างนี้ลงไป:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 180s;
    proxy_connect_timeout 180s;
    client_max_body_size 50M;
}
```
4. กด **Apply** หรือ **OK**

เมื่อเปิดเบราว์เซอร์เข้าที่ `https://parts.yourdomain.com` ระบบ AutoParts จะพร้อมใช้งาน 100%!

---

## ขั้นตอนที่ 1.5: การตั้งเวลา Backup ฐานข้อมูลอัตโนมัติบน Plesk

ตั้งค่าให้ Plesk สำรองข้อมูล SQLite Database อัตโนมัติทุกวันเวลา 03:00 น.:

1. ไปที่ **Websites & Domains** > เลือกโดเมนของท่าน > คลิก **Scheduled Tasks** (Cron Jobs)
2. คลิก **Add Task**:
   * **Task Type**: Run a command
   * **Command**:
     ```bash
     sqlite3 /var/www/vhosts/yourdomain.com/data/autoparts.db ".backup '/var/www/vhosts/yourdomain.com/backups/autoparts_$(date +\%Y\%m\%d_\%H\%M).db'" && gzip -f /var/www/vhosts/yourdomain.com/backups/*.db
     ```
   * **Run**: Daily (เวลา 03:00)
3. กด **Apply** หรือ **OK**

---

## ขั้นตอนที่ 1.6: การอัปเดตเวอร์ชันใหม่บน Plesk (Update Workflow)

เมื่อท่านมีการแก้ไขโค้ดใหม่:
1. หากใช้ **Plesk Git**: กดปุ่ม **Pull Updates** ในหน้า Git ของ Plesk
2. สั่ง Restart หรือ Rebuild Container:
   * **ผ่าน SSH**: `cd /var/www/vhosts/yourdomain.com/autoparts-app && docker compose up -d --build`
   * **ผ่าน Plesk Docker UI**: คลิกปุ่ม **Restart** ที่ Container `autoparts-app`
3. ข้อมูลทั้งหมด (บัญชีผู้ใช้, อะไหล่, ประวัติค้นหา) ในโฟลเดอร์ `/data` จะปลอดภัย 100% ไม่สูญหาย

---

# 🌐 ส่วนที่ 2: การติดตั้งบน Linux VPS ทั่วไป (Ubuntu + Docker Compose + Caddy Auto-SSL)

สำหรับกรณีติดตั้งบน Standalone Ubuntu Server ที่ไม่มี Control Panel:

## 2.1: เตรียมเซิร์ฟเวอร์และติดตั้ง Docker
```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

## 2.2: Clone Repository และตั้งค่า Environment
```bash
mkdir -p /opt/autoparts && cd /opt/autoparts
git clone <YOUR_REPOSITORY_URL> .
mkdir -p ./data ./logs/caddy
sudo chown -R 1000:1000 ./data
cp .env.production.example .env
nano .env
```

## 2.3: สั่งรัน Production Stack ด้วย Caddy Auto-SSL
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

# 🧭 สรุปโครงสร้างเส้นทางระบบ (Path Map)

| หน้าที่ | เส้นทาง URL | คำอธิบาย |
| :--- | :--- | :--- |
| **ค้นหาอะไหล่ (Customer)** | `/` หรือ `/search` | ค้นหาอะไหล่, เทียบเบอร์ OEM/Aftermarket, ถอดรหัส VIN |
| **แพ็กเกจราคา (Customer)** | `/pricing` | ตารางราคาแพ็กเกจ SaaS และอัปเกรด |
| **ตั้งค่าองค์กร (Customer)** | `/portal` | สมาชิกทีม, สิทธิ์ผู้ใช้, ใบเสร็จรับเงิน |
| **Command Center (Owner)** | `/owner` | **จัดการ AI Engine ยานยนต์**, Pricing Tier, CRM ลูกค้า 360, MRR/ARR |
| **Technical Control (SuperAdmin)** | `/superadmin` | ตรวจสอบ Platform Health, RBAC Matrix, Web Crawler |
| **Operations Hub (Admin)** | `/admin` | ตรวจสอบคิวข้อมูลอะไหล่ Master/Scraped Queue |
| **Task Workspace (Staff)** | `/staff` | รายการงานขายและตรวจสอบอะไหล่ |
| **Healthcheck** | `/health` | ตรวจสอบสถานะ Server และ Database สำหรับ Uptime Monitor |
