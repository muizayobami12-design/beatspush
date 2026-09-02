# Fan Club System - Deployment Runbook

**Last Updated:** August 31, 2026  
**Environment:** Production  
**Status:** Ready for Deployment

---

## Pre-Deployment Checklist

- [ ] All tests passing (280+ tests)
- [ ] Code review completed
- [ ] Database migrations prepared
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Backup strategy tested
- [ ] Monitoring configured
- [ ] Team trained on procedures

---

## System Requirements

### Hardware
- **CPU:** 4+ cores
- **RAM:** 8GB+ (16GB recommended)
- **Storage:** 100GB+ SSD
- **Network:** 1Gbps+ connection

### Software
- **OS:** Ubuntu 20.04 LTS or newer
- **Python:** 3.9+
- **PostgreSQL:** 12+
- **Redis:** 6+
- **Docker:** 20.10+ (optional)

### External Services
- **Stripe:** Production account configured
- **Paystack:** Production account configured
- **Email Service:** SendGrid or similar
- **CDN:** Cloudflare or similar (optional)

---

## Environment Setup

### 1. Create Application Directory

```bash
mkdir -p /var/www/beatpush
cd /var/www/beatpush
git clone https://github.com/beatpush/beatpush.git .
cd backend
```

### 2. Create Virtual Environment

```bash
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
cat > .env << EOF
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/beatpush_prod

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Paystack
PAYSTACK_SECRET_KEY=sk_live_...
PAYSTACK_WEBHOOK_SECRET=...

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# App
ENVIRONMENT=production
DEBUG=False
HOST=0.0.0.0
PORT=8000
API_V1_STR=/api/v1

# CORS
BACKEND_CORS_ORIGINS=["https://beatpush.com"]

# Email
SENDGRID_API_KEY=SG...

# Logging
LOG_LEVEL=info
EOF

chmod 600 .env
```

### 4. Setup PostgreSQL Database

```bash
sudo -u postgres psql << EOF
CREATE DATABASE beatpush_prod;
CREATE USER beatpush_user WITH PASSWORD 'secure_password';
ALTER ROLE beatpush_user SET client_encoding TO 'utf8';
ALTER ROLE beatpush_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE beatpush_user SET default_transaction_deferrable TO on;
ALTER ROLE beatpush_user SET default_transaction_read_committed TO on;
GRANT ALL PRIVILEGES ON DATABASE beatpush_prod TO beatpush_user;
EOF
```

### 5. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Create initial data
python -m app.cli init-db
```

### 6. Setup Redis

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: maxmemory-policy allkeys-lru
# Set: maxmemory 2gb

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

---

## Application Deployment

### Using Gunicorn + Supervisor

#### 1. Install Gunicorn

```bash
pip install gunicorn
```

#### 2. Create Supervisor Config

```bash
sudo nano /etc/supervisor/conf.d/beatpush.conf
```

```ini
[program:beatpush]
directory=/var/www/beatpush/backend
command=/var/www/beatpush/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 120
autostart=true
autorestart=true
stderr_logfile=/var/log/beatpush/error.log
stdout_logfile=/var/log/beatpush/access.log

[program:beatpush-scheduler]
directory=/var/www/beatpush/backend
command=/var/www/beatpush/backend/venv/bin/python -m app.jobs.scheduler
autostart=true
autorestart=true
stderr_logfile=/var/log/beatpush/scheduler_error.log
stdout_logfile=/var/log/beatpush/scheduler.log
```

#### 3. Start Services

```bash
sudo systemctl restart supervisor
sudo supervisorctl status
```

### Using Docker (Alternative)

#### 1. Build Docker Image

```bash
docker build -t beatpush:latest -f Dockerfile .
```

#### 2. Create Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: beatpush_prod
      POSTGRES_USER: beatpush_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    image: beatpush:latest
    environment:
      DATABASE_URL: postgresql://beatpush_user:${DB_PASSWORD}@postgres:5432/beatpush_prod
      REDIS_HOST: redis
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    command: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

volumes:
  postgres_data:
  redis_data:
```

#### 3. Deploy

```bash
docker-compose up -d
```

---

## Nginx Configuration

### 1. Install Nginx

```bash
sudo apt-get install nginx
```

### 2. Create Config

```bash
sudo nano /etc/nginx/sites-available/beatpush
```

```nginx
upstream beatpush {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.beatpush.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.beatpush.com;

    ssl_certificate /etc/letsencrypt/live/api.beatpush.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.beatpush.com/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://beatpush;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    location /static/ {
        alias /var/www/beatpush/backend/static/;
        expires 30d;
    }
}
```

### 3. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/beatpush /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Setup SSL (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.beatpush.com
```

---

## Monitoring & Logging

### 1. Setup Logging

```bash
mkdir -p /var/log/beatpush
touch /var/log/beatpush/{access.log,error.log,scheduler.log}
chown beatpush:beatpush /var/log/beatpush -R
```

### 2. Configure Log Rotation

```bash
sudo nano /etc/logrotate.d/beatpush
```

```
/var/log/beatpush/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 beatpush beatpush
    sharedscripts
    postrotate
        supervisorctl restart beatpush
    endscript
}
```

### 3. Setup Health Checks

```bash
# Health check endpoint
curl https://api.beatpush.com/api/v1/health

# Monitor logs
tail -f /var/log/beatpush/access.log
tail -f /var/log/beatpush/error.log
```

### 4. Setup Monitoring (Prometheus/Grafana)

```bash
# Install Prometheus
sudo apt-get install prometheus

# Install Grafana
sudo apt-get install grafana-server
```

---

## Database Backups

### 1. Daily Backup Script

```bash
cat > /usr/local/bin/backup-beatpush.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/beatpush"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/beatpush_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

# Backup database
pg_dump beatpush_prod | gzip > $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x /usr/local/bin/backup-beatpush.sh
```

### 2. Schedule with Cron

```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup-beatpush.sh
```

### 3. S3 Backup (Optional)

```bash
# Install AWS CLI
pip install awscli

# Add to backup script
aws s3 cp $BACKUP_FILE s3://beatpush-backups/
```

---

## Performance Tuning

### 1. PostgreSQL Optimization

```sql
-- Increase work_mem
ALTER SYSTEM SET work_mem = '256MB';

-- Increase shared_buffers
ALTER SYSTEM SET shared_buffers = '2GB';

-- Increase effective_cache_size
ALTER SYSTEM SET effective_cache_size = '6GB';

-- Create indexes
CREATE INDEX idx_subscription_status ON subscription(status);
CREATE INDEX idx_subscription_dates ON subscription(started_at, cancelled_at);
CREATE INDEX idx_payment_status ON subscription_payment(status, subscription_id);
```

### 2. Redis Optimization

```conf
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
tcp-keepalive 300
```

### 3. Application Tuning

```python
# main.py - Adjust worker count
gunicorn main:app --workers 8 --worker-class uvicorn.workers.UvicornWorker
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 2. SSH Hardening

```bash
# Disable password authentication
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Disable root login
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart ssh
```

### 3. Environment Variable Protection

```bash
# Ensure .env is protected
chmod 600 /var/www/beatpush/backend/.env
chown beatpush:beatpush /var/www/beatpush/backend/.env

# Don't commit .env to git
echo ".env" >> .gitignore
```

---

## Post-Deployment Verification

### 1. Health Check

```bash
curl https://api.beatpush.com/api/v1/health
# Expected: {"status": "healthy", "database": "connected"}
```

### 2. Database Connectivity

```bash
psql postgresql://user:password@localhost/beatpush_prod -c "SELECT 1;"
# Expected: 1
```

### 3. Redis Connectivity

```bash
redis-cli ping
# Expected: PONG
```

### 4. API Test

```bash
curl -X POST https://api.beatpush.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

### 5. Run Test Suite

```bash
cd /var/www/beatpush/backend
pytest tests/ -q --tb=short
# Expected: All tests pass
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
tail -100 /var/log/beatpush/error.log

# Test database connection
psql $DATABASE_URL -c "SELECT 1;"

# Test Redis connection
redis-cli ping

# Check environment variables
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

### High Memory Usage

```bash
# Check what's using memory
free -h
top -b -o %MEM | head -20

# Clear Redis cache
redis-cli FLUSHDB

# Restart application
sudo supervisorctl restart beatpush
```

### Slow API Responses

```bash
# Check query performance
EXPLAIN ANALYZE SELECT * FROM subscription WHERE status = 'active';

# Check Redis cache hit rate
redis-cli INFO stats | grep keyspace_hits

# Check database connections
psql -U beatpush_user -d beatpush_prod -c "SELECT datname, usename, application_name, count(*) FROM pg_stat_activity GROUP BY datname, usename, application_name;"
```

---

## Rollback Procedure

### 1. Database Rollback

```bash
# List migrations
alembic history

# Rollback to previous version
alembic downgrade -1

# Or to specific version
alembic downgrade 123abc456def
```

### 2. Application Rollback

```bash
# Revert to previous git commit
git checkout previous_commit_hash

# Restart application
sudo supervisorctl restart beatpush
```

### 3. Restore from Backup

```bash
# Drop current database
dropdb beatpush_prod

# Restore from backup
gunzip -c /backups/beatpush/beatpush_YYYYMMDD_HHMMSS.sql.gz | psql beatpush_prod
```

---

## Scaling for Production

### Horizontal Scaling

```bash
# Add more Gunicorn workers
--workers 16

# Setup load balancer (HAProxy)
sudo apt-get install haproxy

# Configure in /etc/haproxy/haproxy.cfg
backend api_servers
    balance roundrobin
    server api1 127.0.0.1:8001
    server api2 127.0.0.1:8002
    server api3 127.0.0.1:8003
    server api4 127.0.0.1:8004
```

### Database Scaling

```bash
# Read replicas for reporting
# Configure in PostgreSQL replication.conf

# Connection pooling (PgBouncer)
sudo apt-get install pgbouncer

# Configure in /etc/pgbouncer/pgbouncer.ini
[databases]
beatpush_prod = host=localhost port=5432 dbname=beatpush_prod

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
```

### Redis Scaling

```bash
# Redis Cluster for high availability
# Setup multiple Redis instances with cluster mode enabled

# Or Redis Sentinel for failover
redis-sentinel /etc/redis/sentinel.conf
```

---

## Maintenance Schedule

**Daily:**
- Monitor logs for errors
- Check application health
- Verify database backups

**Weekly:**
- Review performance metrics
- Check SSL certificate expiry
- Test backup restoration

**Monthly:**
- Update security patches
- Analyze usage patterns
- Plan scaling needs

---

**Status:** Ready for Production ✅  
**Last Updated:** August 31, 2026
