# Monitoring Configuration for Automated EDA

## Server Monitoring

### 1. Setup Prometheus + Grafana

```yaml
# Add to docker-compose.yml

prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./deployment/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
```

### 2. Monitor Containers

```bash
# View resource usage
docker stats

# View detailed metrics
docker inspect <container_name>
```

### 3. Monitor Application

```bash
# Check API health
curl https://your-domain.com/api/health

# View error logs
docker-compose logs --tail=100 backend

# Check database
docker-compose exec postgres psql -U postgres -c "
  SELECT pid, usename, application_name, state
  FROM pg_stat_activity;
"
```

## Alerting Setup

### Email Alerts

```bash
# Install mailx
apt-get install -y mailx

# Create alert script
cat > /opt/automated-eda/monitoring/check_health.sh << 'EOF'
#!/bin/bash
if ! curl -f http://localhost:8000/health; then
  echo "Application health check failed!" | \
    mail -s "Alert: Automated EDA Down" admin@domain.com
fi
EOF

# Add to crontab
* * * * * /opt/automated-eda/monitoring/check_health.sh
```

### Slack Alerts

```python
import requests

def send_slack_alert(message):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    requests.post(webhook_url, json={"text": message})
```

## Log Management

### Centralized Logging with ELK Stack

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
  environment:
    - discovery.type=single-node

kibana:
  image: docker.elastic.co/kibana/kibana:7.14.0
  ports:
    - "5601:5601"

filebeat:
  image: docker.elastic.co/beats/filebeat:7.14.0
  volumes:
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
    - /var/run/docker.sock:/var/run/docker.sock:ro
```

## Performance Tuning

### Database Connection Pooling

```python
from sqlalchemy import create_engine, pool

engine = create_engine(
    DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Redis Optimization

```bash
# Check memory usage
redis-cli INFO memory

# Configure maxmemory policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Uptime Monitoring

Use services like:

- UptimeRobot (https://uptimerobot.com)
- Better Uptime (https://betterstack.com)
- Pingdom (https://www.pingdom.com)

Configure to check:

- https://your-domain.com/api/health
- https://your-domain.com (frontend)
