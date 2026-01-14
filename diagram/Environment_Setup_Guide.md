# HƯỚNG DẪN THIẾT LẬP MÔI TRƯỜNG VÀ YÊU CẦU HỆ THỐNG
# Environment Setup & System Requirements Guide

## Hệ thống UIT APS - Advanced Planning & Scheduling
### Module Lập lịch Sản xuất Nâng cao cho ERPNext Manufacturing

---

**Phiên bản:** 1.0
**Ngày cập nhật:** 13/01/2026

---

## MỤC LỤC

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Cài đặt môi trường phát triển](#2-cài-đặt-môi-trường-phát-triển)
3. [Cài đặt môi trường production](#3-cài-đặt-môi-trường-production)
4. [Cấu hình hệ thống](#4-cấu-hình-hệ-thống)
5. [Kiểm tra và xác nhận](#5-kiểm-tra-và-xác-nhận)
6. [Xử lý sự cố](#6-xử-lý-sự-cố)

---

## 1. YÊU CẦU HỆ THỐNG

### 1.1. Yêu cầu phần cứng

#### 1.1.1. Môi trường Development (Tối thiểu)

| Thành phần | Yêu cầu tối thiểu | Khuyến nghị |
|------------|-------------------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Storage | 20 GB SSD | 50 GB SSD |
| Network | 10 Mbps | 100 Mbps |

#### 1.1.2. Môi trường Production

| Thành phần | Yêu cầu tối thiểu | Khuyến nghị | Ghi chú |
|------------|-------------------|-------------|---------|
| CPU | 4 cores | 8+ cores | OR-Tools solver cần nhiều CPU |
| RAM | 8 GB | 16 GB | RL Training cần nhiều RAM |
| Storage | 50 GB SSD | 100 GB SSD | NVMe SSD cho database |
| Network | 100 Mbps | 1 Gbps | Cho multi-user access |

#### 1.1.3. Yêu cầu đặc biệt cho các module

| Module | CPU | RAM | GPU | Ghi chú |
|--------|-----|-----|-----|---------|
| Forecasting (ARIMA/LR) | 2 cores | 2 GB | Không cần | Chạy nhanh |
| Forecasting (Prophet) | 4 cores | 4 GB | Không cần | Stan compiler cần RAM |
| Scheduling (OR-Tools) | 4-8 cores | 4 GB | Không cần | Parallel solving |
| RL Training | 4 cores | 8 GB | Optional (CUDA) | PyTorch training |
| AI Analysis | 1 core | 1 GB | Không cần | API call only |

### 1.2. Yêu cầu phần mềm

#### 1.2.1. Hệ điều hành

| OS | Version | Hỗ trợ | Ghi chú |
|----|---------|--------|---------|
| Ubuntu | 20.04 LTS, 22.04 LTS | Chính thức | Khuyến nghị cho production |
| Debian | 10, 11 | Chính thức | |
| CentOS | 7, 8 | Hỗ trợ | |
| macOS | 11+ (Big Sur) | Development | Không khuyến nghị cho production |
| Windows | 10, 11 | Development | Qua WSL2 |

#### 1.2.2. Software Stack

| Component | Version | Bắt buộc | Ghi chú |
|-----------|---------|----------|---------|
| Python | 3.10 - 3.11 | Có | Python 3.12 chưa hỗ trợ đầy đủ |
| Node.js | 18.x LTS | Có | Cho Frappe frontend |
| MariaDB | 10.6+ | Có | Hoặc MySQL 8.0+ |
| Redis | 6.0+ | Có | Cache và queue |
| nginx | 1.18+ | Có (Production) | Reverse proxy |
| Supervisor | 4.0+ | Có (Production) | Process management |
| Git | 2.30+ | Có | Version control |
| wkhtmltopdf | 0.12.6+ | Tùy chọn | PDF generation |

#### 1.2.3. Frappe/ERPNext Stack

| Component | Version | Ghi chú |
|-----------|---------|---------|
| Frappe Framework | 14.x hoặc 15.x | Core framework |
| ERPNext | 14.x hoặc 15.x | Phải cùng major version với Frappe |
| Bench | 5.x | Frappe CLI tool |

### 1.3. Python Dependencies

#### 1.3.1. Core Dependencies (Bắt buộc)

```txt
# Frappe/ERPNext (tự động cài qua bench)
frappe>=14.0.0

# Optimization
ortools>=9.5.0

# Machine Learning - Forecasting
statsmodels>=0.14.0
prophet>=1.1.4
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0

# Utilities
python-dateutil>=2.8.0
pytz>=2023.3
```

#### 1.3.2. Optional Dependencies

```txt
# Reinforcement Learning (cho Tier 2)
torch>=2.0.0
gymnasium>=0.29.0
stable-baselines3>=2.1.0

# AI Analysis
openai>=1.0.0

# Visualization
matplotlib>=3.7.0
plotly>=5.15.0

# Development
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
```

### 1.4. Yêu cầu Network/Ports

| Port | Service | Môi trường | Ghi chú |
|------|---------|------------|---------|
| 8000-8005 | Frappe/Gunicorn | Dev | Development servers |
| 9000-9005 | Frappe Socketio | Dev | Realtime |
| 11000-11005 | Frappe Schedule | Dev | Background jobs |
| 80 | nginx HTTP | Production | |
| 443 | nginx HTTPS | Production | SSL/TLS |
| 3306 | MariaDB/MySQL | Internal | Database |
| 6379 | Redis | Internal | Cache/Queue |

### 1.5. Yêu cầu External Services

| Service | Bắt buộc | Mục đích | Ghi chú |
|---------|----------|----------|---------|
| OpenAI API | Không | AI Analysis | Cần API key nếu dùng |
| SMTP Server | Không | Email notifications | Cấu hình trong ERPNext |

---

## 2. CÀI ĐẶT MÔI TRƯỜNG PHÁT TRIỂN

### 2.1. Cài đặt trên Ubuntu/Debian

#### 2.1.1. Cập nhật hệ thống

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 2.1.2. Cài đặt dependencies

```bash
# Install Python 3.10
sudo apt-get install -y python3.10 python3.10-dev python3.10-venv python3-pip

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install MariaDB
sudo apt-get install -y mariadb-server mariadb-client

# Install Redis
sudo apt-get install -y redis-server

# Install other dependencies
sudo apt-get install -y \
    git \
    curl \
    wget \
    software-properties-common \
    libffi-dev \
    libssl-dev \
    libmysqlclient-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    xvfb \
    libfontconfig
```

#### 2.1.3. Cài đặt wkhtmltopdf (Optional)

```bash
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo apt-get install -f -y
```

#### 2.1.4. Cấu hình MariaDB

```bash
# Secure installation
sudo mysql_secure_installation

# Login to MySQL
sudo mysql -u root -p

# Create user and database
CREATE USER 'frappe'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON *.* TO 'frappe'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

```bash
# Edit MariaDB config
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

Thêm vào section `[mysqld]`:

```ini
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
```

```bash
# Restart MariaDB
sudo systemctl restart mariadb
```

#### 2.1.5. Cài đặt Bench

```bash
# Install bench
pip3 install frappe-bench

# Verify installation
bench --version
```

### 2.2. Khởi tạo Frappe Bench

#### 2.2.1. Tạo bench mới

```bash
# Create bench directory
cd ~
bench init --frappe-branch version-14 frappe-bench

# Navigate to bench
cd frappe-bench
```

#### 2.2.2. Tạo site mới

```bash
# Create new site
bench new-site uit-aps.local --admin-password admin --mariadb-root-password your_password

# Set as default site
bench use uit-aps.local
```

#### 2.2.3. Cài đặt ERPNext

```bash
# Get ERPNext app
bench get-app --branch version-14 erpnext

# Install ERPNext on site
bench --site uit-aps.local install-app erpnext
```

### 2.3. Cài đặt UIT APS App

#### 2.3.1. Clone repository

```bash
# Navigate to apps directory
cd ~/frappe-bench

# Clone UIT APS (từ git repository)
bench get-app uit_aps https://github.com/your-repo/uit_aps.git

# Hoặc từ local path
bench get-app uit_aps /path/to/uit_aps
```

#### 2.3.2. Cài đặt dependencies

```bash
# Install Python dependencies
cd ~/frappe-bench/apps/uit_aps
pip3 install -r requirements.txt
```

**Nội dung file `requirements.txt`:**

```txt
# requirements.txt for UIT APS

# Optimization
ortools>=9.5.0

# Machine Learning - Forecasting
statsmodels>=0.14.0
prophet>=1.1.4
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0

# Reinforcement Learning (Optional)
torch>=2.0.0
gymnasium>=0.29.0
stable-baselines3>=2.1.0

# AI Analysis (Optional)
openai>=1.0.0

# Utilities
python-dateutil>=2.8.0
pytz>=2023.3
```

#### 2.3.3. Cài đặt app vào site

```bash
cd ~/frappe-bench

# Install UIT APS
bench --site uit-aps.local install-app uit_aps

# Run migrations
bench --site uit-aps.local migrate

# Build assets
bench build
```

### 2.4. Chạy Development Server

```bash
cd ~/frappe-bench

# Start development server
bench start
```

Truy cập: `http://localhost:8000`

### 2.5. Cài đặt trên Windows (WSL2)

#### 2.5.1. Cài đặt WSL2

```powershell
# PowerShell (Administrator)
wsl --install -d Ubuntu-22.04
```

#### 2.5.2. Tiếp tục theo hướng dẫn Ubuntu

Sau khi WSL2 được cài đặt, mở Ubuntu terminal và làm theo các bước ở mục 2.1.

### 2.6. Cài đặt trên macOS

#### 2.6.1. Cài đặt Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2.6.2. Cài đặt dependencies

```bash
# Install dependencies
brew install python@3.10 node@18 mariadb redis git

# Start services
brew services start mariadb
brew services start redis

# Install bench
pip3 install frappe-bench
```

Tiếp tục từ bước 2.2.

---

## 3. CÀI ĐẶT MÔI TRƯỜNG PRODUCTION

### 3.1. Chuẩn bị Server

#### 3.1.1. Tạo user frappe

```bash
# Create frappe user
sudo adduser frappe
sudo usermod -aG sudo frappe

# Switch to frappe user
su - frappe
```

#### 3.1.2. Cài đặt dependencies

Làm theo bước 2.1.2 - 2.1.4.

### 3.2. Setup Production

#### 3.2.1. Khởi tạo bench cho production

```bash
cd /home/frappe
bench init --frappe-branch version-14 frappe-bench --python python3.10
cd frappe-bench
```

#### 3.2.2. Cấu hình DNS

Đảm bảo domain đã trỏ về IP server:
```
A record: aps.yourdomain.com -> your_server_ip
```

#### 3.2.3. Tạo site production

```bash
bench new-site aps.yourdomain.com \
    --admin-password 'strong_password' \
    --mariadb-root-password 'db_root_password'

bench use aps.yourdomain.com
```

#### 3.2.4. Cài đặt apps

```bash
# Get and install ERPNext
bench get-app --branch version-14 erpnext
bench --site aps.yourdomain.com install-app erpnext

# Get and install UIT APS
bench get-app uit_aps /path/to/uit_aps
pip3 install -r apps/uit_aps/requirements.txt
bench --site aps.yourdomain.com install-app uit_aps

# Migrate and build
bench --site aps.yourdomain.com migrate
bench build --production
```

### 3.3. Setup Supervisor và nginx

#### 3.3.1. Auto-generate configs

```bash
# Setup production (generates nginx and supervisor configs)
sudo bench setup production frappe --yes
```

#### 3.3.2. Manual nginx config (nếu cần)

```bash
sudo nano /etc/nginx/conf.d/frappe-bench.conf
```

```nginx
upstream frappe-bench-frappe {
    server 127.0.0.1:8000 fail_timeout=0;
}

upstream frappe-bench-socketio-server {
    server 127.0.0.1:9000 fail_timeout=0;
}

server {
    listen 80;
    server_name aps.yourdomain.com;

    root /home/frappe/frappe-bench/sites;

    location /assets {
        try_files $uri =404;
    }

    location ~ ^/protected/(.*) {
        internal;
        try_files /$1 =404;
    }

    location /socket.io {
        proxy_pass http://frappe-bench-socketio-server;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Frappe-Site-Name aps.yourdomain.com;
        proxy_set_header Origin $scheme://$http_host;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://frappe-bench-frappe;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Frappe-Site-Name aps.yourdomain.com;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

#### 3.3.3. Manual supervisor config (nếu cần)

```bash
sudo nano /etc/supervisor/conf.d/frappe-bench.conf
```

```ini
[program:frappe-bench-frappe-web]
command=/home/frappe/frappe-bench/env/bin/gunicorn -b 127.0.0.1:8000 -w 4 -t 120 frappe.app:application --preload
priority=4
autostart=true
autorestart=true
stdout_logfile=/home/frappe/frappe-bench/logs/web.log
stderr_logfile=/home/frappe/frappe-bench/logs/web.error.log
user=frappe
directory=/home/frappe/frappe-bench/sites

[program:frappe-bench-frappe-schedule]
command=/home/frappe/frappe-bench/env/bin/bench schedule
priority=3
autostart=true
autorestart=true
stdout_logfile=/home/frappe/frappe-bench/logs/schedule.log
stderr_logfile=/home/frappe/frappe-bench/logs/schedule.error.log
user=frappe
directory=/home/frappe/frappe-bench

[program:frappe-bench-frappe-default-worker]
command=/home/frappe/frappe-bench/env/bin/bench worker --queue default
priority=4
autostart=true
autorestart=true
stdout_logfile=/home/frappe/frappe-bench/logs/worker.log
stderr_logfile=/home/frappe/frappe-bench/logs/worker.error.log
user=frappe
stopwaitsecs=1560
directory=/home/frappe/frappe-bench
killasgroup=true
numprocs=1
process_name=%(program_name)s-%(process_num)d

[program:frappe-bench-frappe-short-worker]
command=/home/frappe/frappe-bench/env/bin/bench worker --queue short
priority=4
autostart=true
autorestart=true
stdout_logfile=/home/frappe/frappe-bench/logs/worker.log
stderr_logfile=/home/frappe/frappe-bench/logs/worker.error.log
user=frappe
stopwaitsecs=360
directory=/home/frappe/frappe-bench
killasgroup=true
numprocs=1
process_name=%(program_name)s-%(process_num)d

[program:frappe-bench-frappe-long-worker]
command=/home/frappe/frappe-bench/env/bin/bench worker --queue long
priority=4
autostart=true
autorestart=true
stdout_logfile=/home/frappe/frappe-bench/logs/worker.log
stderr_logfile=/home/frappe/frappe-bench/logs/worker.error.log
user=frappe
stopwaitsecs=1560
directory=/home/frappe/frappe-bench
killasgroup=true
numprocs=1
process_name=%(program_name)s-%(process_num)d

[program:frappe-bench-node-socketio]
command=/usr/bin/node /home/frappe/frappe-bench/apps/frappe/socketio.js
priority=4
autostart=true
autorestart=true
stdout_logfile=/home/frappe/frappe-bench/logs/node-socketio.log
stderr_logfile=/home/frappe/frappe-bench/logs/node-socketio.error.log
user=frappe
directory=/home/frappe/frappe-bench

[group:frappe-bench-web]
programs=frappe-bench-frappe-web,frappe-bench-node-socketio

[group:frappe-bench-workers]
programs=frappe-bench-frappe-schedule,frappe-bench-frappe-default-worker,frappe-bench-frappe-short-worker,frappe-bench-frappe-long-worker
```

#### 3.3.4. Restart services

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all
sudo systemctl restart nginx
```

### 3.4. Setup SSL với Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d aps.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

### 3.5. Backup Configuration

#### 3.5.1. Setup automatic backups

```bash
# Add to crontab
crontab -e
```

```cron
# Daily backup at 2 AM
0 2 * * * cd /home/frappe/frappe-bench && bench --site aps.yourdomain.com backup --with-files >> /home/frappe/backup.log 2>&1

# Weekly cleanup of old backups (keep 7 days)
0 3 * * 0 find /home/frappe/frappe-bench/sites/aps.yourdomain.com/private/backups -type f -mtime +7 -delete
```

---

## 4. CẤU HÌNH HỆ THỐNG

### 4.1. Cấu hình ERPNext

#### 4.1.1. Setup Wizard

Sau khi cài đặt, truy cập web và hoàn thành Setup Wizard:

1. **Company Information**
   - Company Name
   - Country
   - Default Currency
   - Chart of Accounts

2. **Manufacturing Setup**
   - Enable Manufacturing Module
   - Setup Workstations
   - Setup Operations
   - Create BOMs

### 4.2. Cấu hình UIT APS

#### 4.2.1. Cấu hình API Key cho AI Analysis

1. Truy cập: **UIT APS > APS Chatgpt Settings**
2. Nhập OpenAI API Key
3. Save

```python
# Hoặc qua bench console
bench --site aps.yourdomain.com console

>>> from frappe import get_doc
>>> settings = get_doc("APS Chatgpt Settings")
>>> settings.api_key = "sk-your-openai-api-key"
>>> settings.save()
```

#### 4.2.2. Cấu hình Ca làm việc

1. Truy cập: **UIT APS > APS Work Shift**
2. Tạo các ca làm việc:

| Shift Name | Start Time | End Time | Is Night Shift |
|------------|------------|----------|----------------|
| Ca sáng | 06:00 | 14:00 | No |
| Ca chiều | 14:00 | 22:00 | No |
| Ca đêm | 22:00 | 06:00 | Yes |

#### 4.2.3. Cấu hình Scheduler Timeout

Chỉnh sửa `site_config.json`:

```bash
nano ~/frappe-bench/sites/aps.yourdomain.com/site_config.json
```

```json
{
    "db_name": "...",
    "db_password": "...",
    "scheduler_tick_interval": 60,
    "background_workers": 4,
    "gunicorn_workers": 4
}
```

### 4.3. Cấu hình Performance

#### 4.3.1. MariaDB Tuning

```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

```ini
[mysqld]
# InnoDB settings
innodb_buffer_pool_size = 2G  # 50-70% of RAM
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# Query cache
query_cache_type = 1
query_cache_size = 128M

# Connection
max_connections = 200
wait_timeout = 28800

# Temp tables
tmp_table_size = 64M
max_heap_table_size = 64M
```

#### 4.3.2. Redis Tuning

```bash
sudo nano /etc/redis/redis.conf
```

```ini
maxmemory 512mb
maxmemory-policy allkeys-lru
```

#### 4.3.3. Gunicorn Workers

```bash
# Tính số workers tối ưu
# workers = (2 × CPU cores) + 1
# Ví dụ: 8 cores → 17 workers

bench setup supervisor --yes
```

### 4.4. Cấu hình Logging

#### 4.4.1. Enable detailed logging

```bash
nano ~/frappe-bench/sites/aps.yourdomain.com/site_config.json
```

```json
{
    "logging": 1,
    "developer_mode": 0,
    "enable_frappe_logger": true
}
```

#### 4.4.2. Log rotation

```bash
sudo nano /etc/logrotate.d/frappe-bench
```

```
/home/frappe/frappe-bench/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 frappe frappe
}
```

---

## 5. KIỂM TRA VÀ XÁC NHẬN

### 5.1. Checklist cài đặt

```bash
# 1. Check Python version
python3 --version  # Should be 3.10.x

# 2. Check Node.js version
node --version  # Should be 18.x

# 3. Check MariaDB
mysql --version
sudo systemctl status mariadb

# 4. Check Redis
redis-cli ping  # Should return PONG
sudo systemctl status redis

# 5. Check Bench
bench --version

# 6. Check site
bench --site aps.yourdomain.com list-apps
# Should show: frappe, erpnext, uit_aps

# 7. Check workers
sudo supervisorctl status
```

### 5.2. Test các module

#### 5.2.1. Test Forecasting

```python
bench --site aps.yourdomain.com console

>>> from uit_aps.uit_aps.utils.forecasting import test_arima
>>> test_arima()  # Should return forecast results
```

#### 5.2.2. Test OR-Tools

```python
>>> from ortools.sat.python import cp_model
>>> model = cp_model.CpModel()
>>> print("OR-Tools is working!")
```

#### 5.2.3. Test AI Analysis (nếu có API key)

```python
>>> from uit_aps.uit_aps.utils.ai_analysis import test_openai
>>> test_openai()  # Should return AI response
```

### 5.3. Performance Testing

```bash
# Benchmark database
mysqlslap --user=frappe --password=your_password --concurrency=50 --iterations=10 --auto-generate-sql

# Check response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/method/frappe.ping
```

### 5.4. Health Check Script

Tạo file `health_check.sh`:

```bash
#!/bin/bash

echo "=== UIT APS Health Check ==="
echo ""

# Check services
echo "1. Services Status:"
systemctl is-active --quiet mariadb && echo "   MariaDB: OK" || echo "   MariaDB: FAILED"
systemctl is-active --quiet redis && echo "   Redis: OK" || echo "   Redis: FAILED"
systemctl is-active --quiet nginx && echo "   nginx: OK" || echo "   nginx: FAILED"
systemctl is-active --quiet supervisor && echo "   Supervisor: OK" || echo "   Supervisor: FAILED"

# Check Frappe
echo ""
echo "2. Frappe Status:"
cd /home/frappe/frappe-bench
bench --site aps.yourdomain.com doctor 2>/dev/null || echo "   Run 'bench doctor' for details"

# Check disk space
echo ""
echo "3. Disk Space:"
df -h / | tail -1 | awk '{print "   Used: " $5 " (" $3 " of " $2 ")"}'

# Check memory
echo ""
echo "4. Memory Usage:"
free -h | grep Mem | awk '{print "   Used: " $3 " of " $2}'

# Check load
echo ""
echo "5. System Load:"
uptime | awk -F'load average:' '{print "   Load:" $2}'

echo ""
echo "=== Check Complete ==="
```

```bash
chmod +x health_check.sh
./health_check.sh
```

---

## 6. XỬ LÝ SỰ CỐ

### 6.1. Các lỗi thường gặp

#### 6.1.1. Module import error

**Lỗi:**
```
ModuleNotFoundError: No module named 'ortools'
```

**Giải pháp:**
```bash
cd ~/frappe-bench
./env/bin/pip install ortools
bench restart
```

#### 6.1.2. Database connection error

**Lỗi:**
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
```

**Giải pháp:**
```bash
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

#### 6.1.3. Redis connection error

**Lỗi:**
```
redis.exceptions.ConnectionError: Error connecting to localhost:6379
```

**Giải pháp:**
```bash
sudo systemctl start redis
sudo systemctl enable redis
```

#### 6.1.4. Permission denied

**Lỗi:**
```
PermissionError: [Errno 13] Permission denied
```

**Giải pháp:**
```bash
sudo chown -R frappe:frappe /home/frappe/frappe-bench
```

#### 6.1.5. OR-Tools solver timeout

**Lỗi:**
```
Solver reached time limit without finding optimal solution
```

**Giải pháp:**
- Tăng `time_limit_seconds` trong Scheduling Run
- Giảm số lượng Job Cards
- Tăng resources (CPU/RAM)

#### 6.1.6. Prophet installation error

**Lỗi:**
```
Error during Prophet installation
```

**Giải pháp:**
```bash
# Install cmdstan first
pip install cmdstanpy
python -c "import cmdstanpy; cmdstanpy.install_cmdstan()"

# Then install prophet
pip install prophet
```

### 6.2. Log Files

| Log | Location | Mục đích |
|-----|----------|----------|
| Frappe Log | `~/frappe-bench/logs/frappe.log` | Application errors |
| Worker Log | `~/frappe-bench/logs/worker.log` | Background job errors |
| Scheduler Log | `~/frappe-bench/logs/schedule.log` | Scheduled job errors |
| nginx Access | `/var/log/nginx/access.log` | HTTP requests |
| nginx Error | `/var/log/nginx/error.log` | nginx errors |
| MariaDB | `/var/log/mysql/error.log` | Database errors |

### 6.3. Useful Commands

```bash
# Restart all services
bench restart

# Clear cache
bench --site aps.yourdomain.com clear-cache

# Rebuild assets
bench build --force

# Run migrations
bench --site aps.yourdomain.com migrate

# Check background jobs
bench --site aps.yourdomain.com show-pending-jobs

# View logs in realtime
tail -f ~/frappe-bench/logs/frappe.log

# Database backup
bench --site aps.yourdomain.com backup --with-files

# Restore from backup
bench --site aps.yourdomain.com restore /path/to/backup.sql.gz
```

### 6.4. Liên hệ hỗ trợ

- **GitHub Issues:** https://github.com/your-repo/uit_aps/issues
- **ERPNext Forum:** https://discuss.frappe.io
- **Email:** support@yourdomain.com

---

## PHỤ LỤC

### A. Tài liệu tham khảo

- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com)
- [OR-Tools Documentation](https://developers.google.com/optimization)
- [Prophet Documentation](https://facebook.github.io/prophet/)
- [PyTorch Documentation](https://pytorch.org/docs)

### B. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 13/01/2026 | UIT | Initial version |

---

*Tài liệu này được tạo cho mục đích Đồ án tốt nghiệp - UIT*
