# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-prod] - 2024-06-25

### Added
- **Production Docker Configuration**
  - `docker-compose.prod.yml` - Production compose with resources limits
  - `backend/Dockerfile.prod` - Optimized multi-stage build with uvicorn workers
  - `frontend/Dockerfile.prod` - Next.js standalone build

- **Production Environment**
  - `.env.production.example` - Production environment template
  - `deploy.sh` - Automated deployment script
  - `deploy/nginx.conf` - Nginx reverse proxy configuration

- **Production Optimizations**
  - Railway: 2 replicas, 4 uvicorn workers
  - Vercel: Regional deployment (iad1), security headers
  - Next.js: Standalone output for Docker

### Changed
- Updated `railway.json` with `Dockerfile.prod` and production settings
- Updated `vercel.json` with security headers and regional config
- Updated `next.config.js` with standalone output
- Updated `deploy/README.md` with comprehensive deployment guide

### Security
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Rate limiting in nginx configuration
- CORS properly configured for production domains
- Health checks for all services

## [1.0.0-agents] - 2024-06-25

### Added
- **OpenHands Integration**: Complete skill system for autonomous agent development
  - `.openhands/skills/main.md` - Main project skill
  - `.openhands/skills/docker.md` - Docker management skill
  - `.openhands/skills/backend-dev.md` - Backend development skill
  - `.openhands/skills/frontend-dev.md` - Frontend development skill

- **Auto-Executable Scripts**: One-command setup and deployment
  - `setup.sh` - First-time setup and installation
  - `start.sh` - Quick start/stop script with health checks

- **Documentation**: 
  - `README_AGENTS.md` - Comprehensive agents branch documentation
  - Updated `README.md` with agent-optimized quick start
  - `CHANGELOG.md` - Version tracking

- **Docker Compose Optimization**:
  - `docker-compose.agents.yml` - Agents-optimized compose file
  - Updated `docker-compose.yml` with agents branch optimizations
  - OPENAI_API_KEY support in Docker environment

- **Environment Configuration**:
  - Enhanced `.env.example` with all required variables
  - Comprehensive `.gitignore` for agents workflow

### Changed
- Updated `AGENTS.md` with Memoria protocol documentation
- Enhanced docker-compose with async database drivers
- Improved README with clearer quick start instructions

### Fixed
- Database URL format for asyncpg driver
- CORS configuration for development

### Features
- Health check commands in start.sh
- Log streaming support
- Service reset capability
- Multiple environment support

## [0.1.0] - Previous Version

See git history for previous changes.
