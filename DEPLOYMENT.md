# Automated EDA - Complete Deployment Guide

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Docker Deployment](#docker-deployment)
5. [Supabase Configuration](#supabase-configuration)
6. [Database Setup](#database-setup)
7. [Authentication Setup](#authentication-setup)
8. [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
9. [Production Deployment](#production-deployment)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Automated EDA** is a comprehensive web application for automated exploratory data analysis with:

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI + LangGraph + Groq AI
- **Database**: Supabase (PostgreSQL) with RLS
- **Authentication**: JWT + Supabase Auth
- **Cache**: Redis
- **Containers**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

---

## Prerequisites

### Required Tools

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Git** for version control
- **GitHub** account (for CI/CD)
- **Supabase** account (free tier available)
- **Groq API Key** (free from https://console.groq.com)

### System Requirements

- **Memory**: Minimum 4GB RAM, Recommended 8GB+
- **Disk Space**: 10GB+ available
- **OS**: Linux, macOS, or Windows (with WSL2 recommended for Windows)

---

## Local Development Setup

### Step 1: Clone and Setup Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd Automated_EDA

# Create environment file
cp server/.env.example server/.env
cp client/.env.example client/.env
```

### Step 2: Configure Local Environment

**Edit `server/.env`:**

```bash
# Database (local PostgreSQL)
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=automated_eda
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/automated_eda

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
GROQ_API_KEY=your_groq_api_key_here

# JWT
JWT_SECRET=your_local_secret_key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# For development, you can skip Supabase integration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
```

**Edit `client/.env`:**

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Step 3: Start Local Development Environment

```bash
# Using Docker Compose (Recommended)
docker-compose up -d

# Wait for services to be ready
docker-compose logs -f backend

# In a new terminal, the application will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Step 4: Verify Setup

```bash
# Check if all services are running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Test API health
curl http://localhost:8000/health
```

---

## Docker Deployment

### Understanding the Docker Setup

The project includes multiple Docker configurations:

1. **Dockerfile** - Multi-stage build combining frontend and backend
2. **Dockerfile.backend** - Backend-only image
3. **client/Dockerfile** - Frontend-only image
4. **docker-compose.yml** - Orchestrates all services

### Build Docker Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend

# Build with no cache
docker-compose build --no-cache
```

### Running with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: Deletes data)
docker-compose down -v

# Restart a service
docker-compose restart backend
```

### Environment Variables for Docker

Create `.env` file in project root:

```bash
# Database Configuration
DB_USER=postgres
DB_PASSWORD=secure_password_here
DB_NAME=automated_eda

# Redis
REDIS_PASSWORD=redis_password

# API Configuration
GROQ_API_KEY=your_api_key

# JWT
JWT_SECRET=your_jwt_secret_key

# CORS Origins
CORS_ORIGINS=https://yourdomain.com

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_key
SUPABASE_ANON_KEY=your_anon_key
```

---

## Supabase Configuration

### Step 1: Create Supabase Project

1. Go to https://supabase.com and sign up/login
2. Click "New Project"
3. Select organization and region
4. Create a strong database password
5. Wait for project to initialize (5-10 minutes)

### Step 2: Get API Keys

1. Go to **Project Settings > API**
2. Copy the following:
   - **Project URL** → `SUPABASE_URL`
   - **anon public key** → `VITE_SUPABASE_ANON_KEY`, `SUPABASE_KEY`
   - **service_role key** → `SUPABASE_SERVICE_ROLE_KEY`

### Step 3: Setup Database Tables

1. Go to **SQL Editor** in Supabase Dashboard
2. Create a new query and paste content from `server/scripts/init.sql`
3. Run the query
4. Verify tables are created under **Table Editor**

### Step 4: Enable RLS Policies

The init.sql script automatically enables Row Level Security (RLS) and creates policies. Verify:

1. Go to each table under **Authentication > Policies**
2. Ensure policies are enabled (green toggle)
3. Check that RLS is enabled (can see "RLS is ON" message)

### Step 5: Setup Storage Buckets (Optional)

For file storage in Supabase:

```sql
-- Create storage buckets
INSERT INTO storage.buckets (id, name, public)
VALUES ('datasets', 'datasets', false);

INSERT INTO storage.buckets (id, name, public)
VALUES ('dashboards', 'dashboards', false);
```

---

## Database Setup

### Using PostgreSQL Directly

If not using Docker:

```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql
# Windows: Download from https://www.postgresql.org/download/windows/

# Create database
createdb automated_eda

# Create user
createuser -d postgres

# Run migrations
cd server
alembic upgrade head
```

### Using SQLAlchemy Migrations

```bash
# Generate new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

---

## Authentication Setup

### Configure JWT Authentication

In `server/.env`:

```bash
JWT_SECRET=your_very_secure_random_string_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

Generate a secure secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Supabase Authentication Integration

The backend uses JWT tokens. To integrate with Supabase Auth:

1. Update `server/services/auth_service.py` with Supabase client
2. Enable authentication in Supabase dashboard
3. Configure email/password or OAuth providers

### Frontend Authentication Setup

The frontend uses Supabase Auth. Create `client/src/services/authService.js`:

```javascript
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

export const authService = {
  async signup(email, password) {
    return await supabase.auth.signUp({ email, password });
  },

  async login(email, password) {
    return await supabase.auth.signInWithPassword({ email, password });
  },

  async logout() {
    return await supabase.auth.signOut();
  },

  async getCurrentUser() {
    return await supabase.auth.getUser();
  },
};
```

---

## CI/CD Pipeline Configuration

### GitHub Actions Setup

1. **Commit the `.github/workflows/ci-cd.yml` file**

```bash
git add .github/workflows/ci-cd.yml
git commit -m "Add CI/CD pipeline"
git push origin main
```

2. **Configure GitHub Secrets**

Go to **GitHub Repository > Settings > Secrets and variables > Actions**

Add the following secrets:

```
DEPLOY_KEY          - SSH private key for deployment server
DEPLOY_HOST         - Deployment server hostname/IP
DEPLOY_USER         - SSH user on deployment server
DEPLOY_PATH         - Path where app is deployed
DOCKER_REGISTRY     - Docker registry URL (optional)
DOCKER_USERNAME     - Docker username (optional)
DOCKER_PASSWORD     - Docker password (optional)
```

### Pipeline Stages

1. **Test Backend** - Runs pytest, pylint
2. **Test Frontend** - Runs linting, build
3. **Build & Push** - Builds Docker images, pushes to registry
4. **Deploy** - Deploys to production (main branch only)
5. **Security Scan** - Trivy vulnerability scanning

### Manual Trigger

```bash
# Trigger workflow via GitHub CLI
gh workflow run ci-cd.yml
```

---

## Production Deployment

### Option 1: Deploy to VPS (Recommended)

#### Prerequisites

- Ubuntu 20.04+ VPS (DigitalOcean, Linode, AWS EC2, etc.)
- SSH access to VPS
- Domain name pointing to VPS IP

#### Deployment Steps

```bash
# 1. SSH into VPS
ssh root@your-vps-ip

# 2. Install Docker and Docker Compose
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# 3. Clone repository
cd /opt
git clone <your-repo-url> automated-eda
cd automated-eda

# 4. Setup environment
cp .env.production.example .env
nano .env  # Edit with your production values

# 5. Setup SSL Certificate (using Let's Encrypt)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d your-domain.com

# 6. Configure Nginx (optional, for reverse proxy)
# Copy nginx config from deployment/nginx.conf

# 7. Start services
docker-compose up -d

# 8. Verify
docker-compose ps
curl https://your-domain.com/health
```

### Option 2: Deploy to Railway, Render, or Fly.io

#### Railway.app Deployment

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Link to project
railway init

# 4. Add environment variables
railway variable set GROQ_API_KEY=...
railway variable set SUPABASE_URL=...

# 5. Deploy
railway up
```

#### Render.com Deployment

1. Push code to GitHub
2. Go to render.com and create new Web Service
3. Connect GitHub repository
4. Configure environment variables
5. Deploy

### Option 3: Kubernetes Deployment

```bash
# Prerequisites
# - kubectl installed
# - k8s cluster access

# 1. Build and push Docker image
docker build -t your-registry/automated-eda:latest .
docker push your-registry/automated-eda:latest

# 2. Create k8s deployment files (deployment/, service/, ingress/)
# 3. Deploy
kubectl apply -f deployment/

# 4. Check status
kubectl get pods
kubectl logs <pod-name>
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl https://your-domain.com/health

# API documentation
https://your-domain.com/docs

# Check Docker containers
docker-compose ps

# Check logs
docker-compose logs --tail=100 backend
```

### Database Backups

```bash
# Backup PostgreSQL database
docker-compose exec postgres pg_dump -U postgres automated_eda > backup.sql

# Restore from backup
docker-compose exec -T postgres psql -U postgres automated_eda < backup.sql

# Backup Supabase (automatic)
# Supabase provides automatic daily backups in the dashboard
```

### Performance Monitoring

Monitor using:

- **Supabase Dashboard** - Database metrics
- **Docker Stats** - Container resource usage
  ```bash
  docker stats
  ```
- **Application Logs** - Check for errors
  ```bash
  docker-compose logs -f --tail=50
  ```

### Updating the Application

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild containers
docker-compose build --no-cache

# 3. Restart services
docker-compose restart

# 4. Run database migrations (if any)
docker-compose exec backend alembic upgrade head

# 5. Verify
docker-compose ps
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use

```bash
# Find process using port
lsof -i :8000  # for port 8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

#### 2. Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose logs postgres

# Verify connection string
docker-compose exec backend python -c "from sqlalchemy import create_engine; engine = create_engine(os.getenv('DATABASE_URL')); engine.connect()"

# Restart database
docker-compose restart postgres
```

#### 3. CORS Errors

Update `CORS_ORIGINS` in `.env`:

```bash
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

#### 4. Authentication Failures

```bash
# Check JWT_SECRET is set
docker-compose exec backend python -c "import os; print(os.getenv('JWT_SECRET'))"

# Verify Supabase credentials
docker-compose exec backend python << 'EOF'
from supabase import create_client
client = create_client(
    "https://your-project.supabase.co",
    "your_key"
)
print("Connected successfully")
EOF
```

#### 5. Memory Issues

```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory

# Or limit container memory
# Update docker-compose.yml:
# services:
#   backend:
#     mem_limit: 2g
```

#### 6. Build Failures

```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache --pull

# Check logs
docker-compose build --progress=plain 2>&1 | tail -50
```

### Getting Help

1. **Check logs first**

   ```bash
   docker-compose logs -f <service-name>
   ```

2. **Check API documentation**

   - Go to http://localhost:8000/docs (Swagger UI)
   - Go to http://localhost:8000/redoc (ReDoc)

3. **Database issues**

   - Check Supabase dashboard
   - Verify RLS policies are not blocking queries

4. **Frontend issues**
   - Check browser console (F12)
   - Verify environment variables in `.env`
   - Check CORS settings

---

## Quick Commands Reference

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# View running services
docker-compose ps

# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec postgres psql -U postgres -d automated_eda

# Run migrations
docker-compose exec backend alembic upgrade head

# Rebuild services
docker-compose build --no-cache

# View container stats
docker stats

# Clean up everything
docker-compose down -v
docker system prune -a
```

---

## Next Steps

1. ✅ Set up Docker environment
2. ✅ Configure Supabase project
3. ✅ Setup authentication
4. ✅ Configure CI/CD pipeline
5. ✅ Deploy to production
6. 📊 Monitor application
7. 🔄 Set up automated backups
8. 📈 Scale based on usage

---

## Support and Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **Docker**: https://docs.docker.com
- **Supabase**: https://supabase.com/docs
- **React**: https://react.dev
- **Groq API**: https://console.groq.com/docs

---

**Last Updated**: December 23, 2025
**Version**: 1.0.0
