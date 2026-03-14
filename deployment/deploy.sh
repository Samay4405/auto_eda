#!/bin/bash

# Automated EDA - Production Deployment Script
# This script deploys the application to a production VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Automated EDA Production Deployment ===${NC}\n"

# Check if running with root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}This script must be run with sudo${NC}"
    exit 1
fi

# Configuration
DEPLOY_DIR="/opt/automated-eda"
DOMAIN="${1:-localhost}"
ENVIRONMENT="${2:-production}"

echo -e "${YELLOW}Configuration:${NC}"
echo "Deploy Directory: $DEPLOY_DIR"
echo "Domain: $DOMAIN"
echo "Environment: $ENVIRONMENT"
echo ""

# Step 1: Install Docker
echo -e "${YELLOW}Step 1: Installing Docker and Docker Compose...${NC}"
apt-get update
apt-get install -y docker.io docker-compose git curl
usermod -aG docker root

# Step 2: Clone repository
echo -e "${YELLOW}Step 2: Setting up application directory...${NC}"
if [ ! -d "$DEPLOY_DIR" ]; then
    read -p "Enter GitHub repository URL: " REPO_URL
    git clone "$REPO_URL" "$DEPLOY_DIR"
else
    cd "$DEPLOY_DIR"
    git pull origin main
fi

cd "$DEPLOY_DIR"

# Step 3: Create environment file
echo -e "${YELLOW}Step 3: Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.production.example .env
    
    echo -e "${YELLOW}Please edit .env with your production values:${NC}"
    echo "1. GROQ_API_KEY"
    echo "2. SUPABASE_URL and SUPABASE_KEY"
    echo "3. Database password"
    echo "4. JWT_SECRET"
    echo ""
    echo "Launching editor..."
    nano .env
else
    echo -e "${GREEN}.env file already exists${NC}"
fi

# Step 4: Setup SSL certificate
echo -e "${YELLOW}Step 4: Setting up SSL certificate...${NC}"
if [ "$DOMAIN" != "localhost" ]; then
    apt-get install -y certbot python3-certbot-nginx
    
    if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos -m admin@"$DOMAIN"
    else
        echo -e "${GREEN}Certificate already exists${NC}"
    fi
fi

# Step 5: Setup Nginx
echo -e "${YELLOW}Step 5: Setting up Nginx reverse proxy...${NC}"
apt-get install -y nginx

# Create nginx config
cat > /etc/nginx/sites-available/automated-eda << EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/automated-eda /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Step 6: Start Docker containers
echo -e "${YELLOW}Step 6: Starting Docker containers...${NC}"
docker-compose up -d
sleep 30

# Step 7: Run migrations
echo -e "${YELLOW}Step 7: Running database migrations...${NC}"
docker-compose exec -T backend alembic upgrade head

# Step 8: Verification
echo -e "${YELLOW}Step 8: Verifying deployment...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo -e "${GREEN}Your application is now available at:${NC}"
echo "  - Frontend: https://$DOMAIN"
echo "  - API: https://$DOMAIN/api"
echo "  - Docs: https://$DOMAIN/api/docs"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "1. Check logs: docker-compose logs -f"
echo "2. Monitor: docker stats"
echo "3. Backups: Set up automated database backups"
echo "4. SSL Renewal: certbot will auto-renew (usually enabled)"
echo ""
