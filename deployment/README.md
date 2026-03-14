# Deployment Files Guide

This directory contains all the necessary files and scripts for deploying Automated EDA to production.

## Files Overview

### Docker Configuration

- `Dockerfile` - Multi-stage production build (frontend + backend)
- `Dockerfile.backend` - Backend-only Docker image
- `client/Dockerfile` - Frontend production image
- `client/Dockerfile.dev` - Frontend development image with hot reload
- `docker-compose.yml` - Production orchestration
- `docker-compose.dev.yml` - Development with hot reload

### Deployment Scripts

- `deployment/deploy.sh` - Automated deployment script for VPS
- `deployment/backup.sh` - Database backup script (use with cron)
- `deployment/nginx.conf` - Nginx reverse proxy configuration

### Documentation

- `DEPLOYMENT.md` - Complete deployment guide
- `QUICK_START.md` - 5-minute quick start guide
- `deployment/MONITORING.md` - Monitoring setup guide

### Environment Configuration

- `server/.env.example` - Backend environment template
- `client/.env.example` - Frontend environment template
- `.env.production.example` - Production environment template

### CI/CD

- `.github/workflows/ci-cd.yml` - GitHub Actions pipeline

---

## Quick Deployment Options

### Option 1: Local Development (Docker)

```bash
# Start all services
docker-compose up -d

# Access
http://localhost:3000  # Frontend
http://localhost:8000  # API
```

### Option 2: VPS Production Deployment

```bash
# SSH into VPS
ssh root@your-vps-ip

# Run deployment script
curl https://raw.githubusercontent.com/your-repo/main/deployment/deploy.sh | bash
```

### Option 3: Docker with Development Mode

```bash
# With hot reload for development
docker-compose -f docker-compose.dev.yml up -d
```

---

## Key Environment Variables Required

Before deploying, you need to set up these variables:

### Essential (Required)

```bash
# Groq AI API
GROQ_API_KEY=your_groq_api_key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key

# JWT Token
JWT_SECRET=generate_random_secret
```

### Database

```bash
DB_USER=postgres
DB_PASSWORD=secure_password
DB_NAME=automated_eda
```

### Domain & CORS

```bash
CORS_ORIGINS=https://your-domain.com
```

See `.env.example` files for all available options.

---

## Services Included

### Backend Services

- **FastAPI** - API server (port 8000)
- **PostgreSQL** - Database (port 5432)
- **Redis** - Cache layer (port 6379)
- **Celery** - Task queue (optional)

### Frontend Services

- **Node.js** - Frontend dev server (port 3000)
- **Vite** - Build tool
- **React** - UI framework

### Reverse Proxy

- **Nginx** - Reverse proxy (ports 80, 443)

---

## Deployment Checklist

- [ ] Create Supabase account and project
- [ ] Get Groq API key
- [ ] Configure environment variables
- [ ] Setup domain name
- [ ] Setup SSL certificate
- [ ] Deploy Docker containers
- [ ] Run database migrations
- [ ] Test application
- [ ] Setup backups
- [ ] Configure CI/CD
- [ ] Monitor application

---

## Step-by-Step Deployment

### 1. Prepare Infrastructure

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io docker-compose

# Install Git
sudo apt-get install -y git
```

### 2. Setup Application

```bash
# Clone repository
git clone <your-repo-url> /opt/automated-eda
cd /opt/automated-eda

# Copy environment file
cp .env.production.example .env

# Edit with your values
nano .env
```

### 3. Setup Database

```bash
# Create Supabase project at supabase.com
# Copy database URL to .env

# Run migrations
docker-compose exec backend alembic upgrade head
```

### 4. Setup SSL

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d your-domain.com
```

### 5. Start Services

```bash
# Start all services
docker-compose up -d

# Verify
docker-compose ps

# Check logs
docker-compose logs -f backend
```

---

## Monitoring & Maintenance

### Check Application Health

```bash
# API health
curl https://your-domain.com/api/health

# View logs
docker-compose logs --tail=100 backend

# Check resources
docker stats
```

### Database Backup

```bash
# Manual backup
docker-compose exec postgres pg_dump -U postgres automated_eda > backup.sql

# Automatic backup (add to crontab)
0 2 * * * /opt/automated-eda/deployment/backup.sh
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

---

## Troubleshooting

### Port Already in Use

```bash
lsof -i :8000
kill -9 <PID>
```

### Database Connection Failed

```bash
docker-compose restart postgres
docker-compose logs postgres
```

### CORS Errors

```bash
# Update .env
CORS_ORIGINS=https://your-domain.com

# Restart backend
docker-compose restart backend
```

### Out of Memory

```bash
# Increase Docker memory limit
# Edit docker-compose.yml:
# services:
#   postgres:
#     mem_limit: 2g
```

---

## Performance Optimization

### Database

- Configure connection pooling
- Enable query caching with Redis
- Regular maintenance: VACUUM, ANALYZE
- Index optimization

### Backend

- Use async operations
- Configure Gunicorn workers
- Enable gzip compression
- Cache static assets

### Frontend

- Minify and compress assets
- Use CDN for static files
- Implement lazy loading
- Optimize images

---

## Security Best Practices

1. **SSL/TLS**: Always use HTTPS in production
2. **Environment Variables**: Never commit secrets
3. **Database**: Use strong passwords, enable RLS
4. **API**: Implement rate limiting, input validation
5. **Backups**: Regular automated backups
6. **Updates**: Keep dependencies updated
7. **Monitoring**: Setup alerts for issues
8. **Access Control**: Use SSH keys, not passwords

---

## Support Resources

- **Docker**: https://docs.docker.com
- **FastAPI**: https://fastapi.tiangolo.com
- **Supabase**: https://supabase.com/docs
- **Nginx**: https://nginx.org/en/docs
- **Let's Encrypt**: https://letsencrypt.org/docs

---

## Getting Help

1. Check logs: `docker-compose logs`
2. Review `DEPLOYMENT.md` for detailed guide
3. Check `QUICK_START.md` for quick reference
4. Visit API docs: http://localhost:8000/docs

---

**Last Updated**: December 23, 2025
**Version**: 1.0.0
