#!/bin/bash

# Automated EDA - Linux/macOS Development Setup Script

set -e

echo ""
echo "==============================================="
echo "Automated EDA - Development Setup"
echo "==============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed!"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "[1/5] Docker is installed ✓"
echo ""

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed!"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "[2/5] Docker Compose is installed ✓"
echo ""

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "ERROR: Git is not installed!"
    echo "Please install Git from: https://git-scm.com/download/linux"
    exit 1
fi

echo "[3/5] Git is installed ✓"
echo ""

# Create environment files
if [ ! -f "server/.env" ]; then
    echo "[4/5] Creating server/.env file..."
    cp server/.env.example server/.env
    echo "Created server/.env - Please edit with your values!"
else
    echo "[4/5] server/.env already exists ✓"
fi
echo ""

if [ ! -f "client/.env" ]; then
    echo "[5/5] Creating client/.env file..."
    cp client/.env.example client/.env
    echo "Created client/.env - Please edit with your values!"
else
    echo "[5/5] client/.env already exists ✓"
fi
echo ""

# Start Docker Compose
echo "Starting Docker services..."
docker-compose up -d

echo ""
echo "==============================================="
echo "Setup Complete!"
echo "==============================================="
echo ""
echo "Your application is starting. Please wait 30 seconds for services to be ready..."
echo ""
echo "Access your application at:"
echo "  Frontend:   http://localhost:3000"
echo "  API:        http://localhost:8000"
echo "  API Docs:   http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  View logs:      docker-compose logs -f"
echo "  Stop services:  docker-compose down"
echo "  Restart:        docker-compose restart"
echo ""
