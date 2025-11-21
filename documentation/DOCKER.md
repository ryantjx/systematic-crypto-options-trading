# Docker Infrastructure Guide

This document provides comprehensive information about the Docker containers used in the systematic crypto options trading system, including setup instructions, configurations, and deployment guidelines.

---

## Overview

The system uses a microservices architecture with containerized components for data storage, streaming, monitoring, and application logic. All services are orchestrated using Docker Compose for development and Docker Swarm/Kubernetes for production deployments.

---

## Container Images

### Core Services

#### QuestDB - Time-Series Database
**Image**: `questdb/questdb:latest`

**Description**: High-throughput time-series database for storing tick data, OHLCV data, and options quotes.

**Ports**:
- `9000` - Web Console UI
- `8812` - PostgreSQL wire protocol
- `9009` - InfluxDB line protocol (for high-speed ingestion)

**Volumes**:
- `/var/lib/questdb` - Database storage

**Configuration**:
```yaml
environment:
  - QDB_CAIRO_COMMIT_LAG=1000
  - QDB_PG_NET_ACTIVE_CONNECTION_LIMIT=64
  - QDB_HTTP_BIND_TO=0.0.0.0:9000
```

**Resource Limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

---

#### Redis - In-Memory Cache
**Image**: `redis:7-alpine`

**Description**: Sub-millisecond caching layer for live trading state, current Greeks, and volatility surface snapshots.

**Ports**:
- `6379` - Redis server

**Volumes**:
- `/data` - Persistence storage

**Configuration**:
```yaml
command: >
  redis-server
  --appendonly yes
  --appendfsync everysec
  --maxmemory 2gb
  --maxmemory-policy allkeys-lru
```

**Resource Limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 1G
```

---

#### Apache Kafka - Streaming Platform
**Image**: `confluentinc/cp-kafka:latest` (with Zookeeper)

**Description**: Distributed streaming platform for decoupled, fault-tolerant data pipelines.

**Ports**:
- `9092` - Kafka broker
- `2181` - Zookeeper (if using separate container)

**Volumes**:
- `/var/lib/kafka/data` - Kafka logs and topics

**Configuration**:
```yaml
environment:
  KAFKA_BROKER_ID: 1
  KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
  KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
  KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
  KAFKA_LOG_RETENTION_HOURS: 168
  KAFKA_LOG_RETENTION_BYTES: 10737418240
```

**Resource Limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

---

### Monitoring & Visualization

#### Grafana - Dashboards
**Image**: `grafana/grafana:latest`

**Description**: Real-time dashboards for volatility surfaces, Greeks evolution, and system metrics.

**Ports**:
- `3000` - Web UI

**Volumes**:
- `/var/lib/grafana` - Dashboard configurations and data
- `/etc/grafana/provisioning` - Provisioning configs (datasources, dashboards)

**Configuration**:
```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=<set-in-.env>
  - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
  - GF_SERVER_ROOT_URL=https://grafana.yourdomain.com
```

**Resource Limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

#### Prometheus - Metrics Collection
**Image**: `prom/prometheus:latest`

**Description**: Time-series metrics collection for API latency, processing time, and error rates.

**Ports**:
- `9090` - Web UI and API

**Volumes**:
- `/prometheus` - Metrics storage
- `/etc/prometheus/prometheus.yml` - Configuration file

**Configuration** (`prometheus.yml`):
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'trading-app'
    static_configs:
      - targets: ['app:8000']
  
  - job_name: 'questdb'
    static_configs:
      - targets: ['questdb:9003']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

**Resource Limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 1G
```

---

### Application

#### Trading Application
**Image**: `systematic-crypto-trading:latest` (custom build)

**Description**: Main application container running data ingestion, surface calculation, and trading logic.

**Build Context**:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY configs/ ./configs/

# Set Python path
ENV PYTHONPATH=/app

# Run application
CMD ["python", "-m", "src.main"]
```

**Ports**:
- `8000` - API server (if applicable)
- `8001` - Metrics endpoint for Prometheus

**Volumes**:
- `/app/logs` - Application logs
- `/app/config` - Runtime configuration files
- `/app/data` - Local data cache (if needed)

**Environment Variables** (stored in `.env`):
```bash
# Deribit API
DERIBIT_API_KEY=<your-api-key>
DERIBIT_API_SECRET=<your-api-secret>
DERIBIT_TESTNET=false

# Database
QUESTDB_HOST=questdb
QUESTDB_PORT=8812
QUESTDB_DATABASE=qdb

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Telegram
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_CHAT_ID=<your-chat-id>

# Logging
LOG_LEVEL=INFO
```

**Resource Limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
    reservations:
      cpus: '2.0'
      memory: 4G
```

---

## Docker Compose Configuration

### Development Setup

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  questdb:
    image: questdb/questdb:latest
    container_name: questdb
    ports:
      - "9000:9000"
      - "8812:8812"
      - "9009:9009"
    volumes:
      - questdb-data:/var/lib/questdb
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
    restart: unless-stopped

  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - kafka-data:/var/lib/kafka/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./configs/grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
      - questdb
    restart: unless-stopped

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: trading-app
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./configs:/app/configs:ro
    depends_on:
      - questdb
      - redis
      - kafka
    restart: unless-stopped

volumes:
  questdb-data:
  redis-data:
  zookeeper-data:
  kafka-data:
  prometheus-data:
  grafana-data:

networks:
  default:
    name: trading-network
```

---

## Deployment Instructions

### Local Development

1. **Prerequisites**:
   ```bash
   # Install Docker and Docker Compose
   docker --version
   docker compose version
   ```

2. **Environment Setup**:
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your credentials
   vim .env
   ```

3. **Start Services**:
   ```bash
   # Start all services
   docker compose up -d
   
   # View logs
   docker compose logs -f app
   
   # Check status
   docker compose ps
   ```

4. **Access Services**:
   - QuestDB Console: http://localhost:9000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

5. **Stop Services**:
   ```bash
   docker compose down
   
   # Remove volumes (WARNING: deletes all data)
   docker compose down -v
   ```

---

### Production Deployment (AWS EC2)

1. **Server Setup**:
   ```bash
   # SSH into EC2 instance
   ssh -i your-key.pem ec2-user@your-instance-ip
   
   # Install Docker
   sudo yum update -y
   sudo yum install -y docker
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/systematic-crypto-options-trading.git
   cd systematic-crypto-options-trading
   ```

3. **Configure Production Environment**:
   ```bash
   # Create production .env
   cp .env.example .env
   vim .env  # Update with production credentials
   
   # Set appropriate permissions
   chmod 600 .env
   ```

4. **Deploy**:
   ```bash
   # Build and start
   docker compose -f docker-compose.prod.yml up -d --build
   
   # Verify
   docker compose ps
   docker compose logs -f
   ```

5. **Enable Auto-Restart on Boot**:
   ```bash
   # Create systemd service
   sudo vim /etc/systemd/system/trading-app.service
   ```
   
   Content:
   ```ini
   [Unit]
   Description=Trading Application Docker Compose
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/home/ec2-user/systematic-crypto-options-trading
   ExecStart=/usr/local/bin/docker-compose up -d
   ExecStop=/usr/local/bin/docker-compose down

   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable:
   ```bash
   sudo systemctl enable trading-app.service
   sudo systemctl start trading-app.service
   ```

---

## Maintenance

### Updating Containers

```bash
# Pull latest images
docker compose pull

# Restart with new images
docker compose up -d
```

### Backup & Restore

**QuestDB**:
```bash
# Backup
docker exec questdb tar czf /var/lib/questdb/backup.tar.gz /var/lib/questdb/db
docker cp questdb:/var/lib/questdb/backup.tar.gz ./backups/

# Restore
docker cp ./backups/backup.tar.gz questdb:/var/lib/questdb/
docker exec questdb tar xzf /var/lib/questdb/backup.tar.gz -C /var/lib/questdb/
```

**Redis**:
```bash
# Backup
docker exec redis redis-cli BGSAVE
docker cp redis:/data/dump.rdb ./backups/

# Restore
docker cp ./backups/dump.rdb redis:/data/
docker compose restart redis
```

### Monitoring Container Health

```bash
# View resource usage
docker stats

# View logs
docker compose logs -f [service-name]

# Check container health
docker compose ps
docker inspect [container-name]
```

---

## Troubleshooting

### Common Issues

**Issue**: Kafka fails to start
```bash
# Solution: Clear Kafka data
docker compose down
docker volume rm systematic-crypto-options-trading_kafka-data
docker compose up -d
```

**Issue**: QuestDB out of memory
```bash
# Solution: Increase memory limit in docker-compose.yml
# Or clear old data with retention policy
```

**Issue**: Container restart loops
```bash
# Check logs
docker compose logs [service-name]

# Check resource constraints
docker stats
```

---

## Resource Planning

### Minimum Requirements (Development)
- **CPU**: 4 cores
- **RAM**: 16 GB
- **Disk**: 100 GB SSD

### Recommended Production Setup
- **EC2 Instance**: t3.xlarge (4 vCPU, 16 GB RAM)
- **Storage**: 500 GB EBS SSD (gp3)
- **Estimated Monthly Cost**: ~$150-200

### Scaling Considerations
- Add more Kafka brokers for higher throughput
- Use managed services (AWS RDS, ElastiCache) for databases
- Consider Kubernetes for multi-instance orchestration