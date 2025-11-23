# Deployment Guide - Pharma AI Platform

## 📋 Prerequisites

- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- 8GB+ RAM
- SSL certificate (for production)

## 🚀 Quick Start

### Development

```bash
# 1. Clone and configure
git clone <repo-url>
cd BioPharma-LLM
cp .env.example .env

# 2. Update .env with your settings
# Edit .env and change default passwords

# 3. Start all services
make dev

# 4. Run migrations
make db-upgrade

# 5. Access the platform
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Production

```bash
# 1. Update environment variables
export ENVIRONMENT=production
export SECRET_KEY=$(openssl rand -hex 32)
export POSTGRES_PASSWORD=$(openssl rand -hex 16)
export REDIS_PASSWORD=$(openssl rand -hex 16)

# 2. Configure SSL certificates
mkdir -p infra/nginx/ssl
# Copy your SSL certificates to infra/nginx/ssl/

# 3. Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# 4. Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 5. Create admin user (optional)
docker-compose -f docker-compose.prod.yml exec backend python -m app.scripts.create_admin
```

## 🔐 Security Checklist

- [ ] Change all default passwords in .env
- [ ] Generate persistent SECRET_KEY
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure Sentry error tracking
- [ ] Set up database backups
- [ ] Review CORS settings
- [ ] Enable audit logging
- [ ] Implement IP whitelisting (if needed)

## 📊 Monitoring

### Health Checks

```bash
# Check all services
curl http://localhost:8000/api/v1/health

# Detailed health check
curl http://localhost:8000/api/v1/health/ready
```

### Logs

```bash
# View all logs
make logs

# View specific service
make logs-backend
make logs-frontend

# Follow logs in production
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔄 Updates & Maintenance

### Database Backups

```bash
# Backup database
docker-compose exec db pg_dump -U pharma_user pharma_db > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U pharma_user pharma_db < backup.sql
```

### Applying Updates

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild containers
docker-compose build

# 3. Run migrations
docker-compose exec backend alembic upgrade head

# 4. Restart services
docker-compose restart
```

## 🐛 Troubleshooting

### Common Issues

**Database connection refused**
```bash
# Check if database is running
docker-compose ps db

# Check logs
docker-compose logs db
```

**Migration errors**
```bash
# Check current version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history
```

**Out of memory**
```bash
# Check container stats
docker stats

# Increase memory limits in docker-compose.yml
```

For more help, see [docs/troubleshooting.md](docs/troubleshooting.md)
