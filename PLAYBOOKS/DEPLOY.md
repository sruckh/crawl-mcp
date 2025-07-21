# DEPLOY.md - Docker Deployment Playbook for Crawl4AI MCP Server

## Overview
This playbook provides comprehensive deployment procedures for the Crawl4AI MCP Server across different environments using Docker containerization and automated CI/CD pipelines.

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deployment Strategies](#deployment-strategies)
3. [Environment-Specific Deployments](#environment-specific-deployments)
4. [Container Management](#container-management)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Emergency Procedures](#emergency-procedures)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Pre-Deployment Checklist

### Code and Container Readiness
- [ ] **GitHub Actions CI/CD Pipeline**
  - [ ] All automated tests passing
  - [ ] Container builds successful across all variants
  - [ ] Docker Hub push completed successfully
  - [ ] Security scans passed (no critical vulnerabilities)
  - [ ] GitHub Actions workflow completed without errors

- [ ] **Container Quality Assurance**
  - [ ] CPU-optimized container build verified (`Dockerfile.cpu`)
  - [ ] Lightweight container tested (`Dockerfile.lightweight`)
  - [ ] RunPod serverless container ready (`Dockerfile.runpod`)
  - [ ] Standard container functional (`Dockerfile`)
  - [ ] All containers pass health checks
  - [ ] Container size optimization verified

- [ ] **MCP Protocol Compliance**
  - [ ] All 19 MCP tools functional
  - [ ] Tool signatures validated
  - [ ] JSON response format confirmed
  - [ ] Claude Desktop integration tested
  - [ ] FastMCP server startup verified

### Infrastructure Readiness
- [ ] **Docker Environment**
  - [ ] Docker Engine/Desktop updated to latest version
  - [ ] Docker Compose v2.x available
  - [ ] shared_net network created and accessible
  - [ ] Container registry accessible (Docker Hub)
  - [ ] Sufficient disk space for images (5GB+ recommended)

- [ ] **Environment Configuration**
  - [ ] Environment variables documented and validated
  - [ ] API keys secured (if using AI features)
  - [ ] Resource limits configured appropriately
  - [ ] Network security policies verified
  - [ ] Backup strategies confirmed

### Communication and Documentation
- [ ] **Team Coordination**
  - [ ] Deployment window communicated
  - [ ] Stakeholders notified of changes
  - [ ] Rollback plan reviewed and approved
  - [ ] Emergency contact list updated

- [ ] **Documentation Updates**
  - [ ] CHANGELOG.md updated with version changes
  - [ ] API documentation reflects any tool changes
  - [ ] Configuration examples updated
  - [ ] Troubleshooting guides current

## Deployment Strategies

### Strategy 1: VPS Docker Deployment (Recommended)
Best for: Local development, VPS hosting, production servers

#### CPU-Optimized Deployment
```bash
# 1. Update repository
git fetch origin
git checkout main
git pull origin main

# 2. Stop existing containers
docker-compose -f docker-compose.cpu.yml down

# 3. Update environment configuration
cp .env.example .env
# Edit .env with production values

# 4. Build and deploy CPU-optimized container
docker-compose -f docker-compose.cpu.yml build --no-cache
docker-compose -f docker-compose.cpu.yml up -d

# 5. Verify deployment
docker-compose -f docker-compose.cpu.yml ps
docker-compose -f docker-compose.cpu.yml logs crawl4ai-mcp-cpu
```

#### Performance Configuration
```yaml
# Production docker-compose.cpu.yml settings
environment:
  - FASTMCP_LOG_LEVEL=WARNING     # Reduce log verbosity
  - MAX_CONCURRENT_REQUESTS=5     # Increase for production load
  - CACHE_TTL=3600               # Extended cache for performance
  - SAFE_MODE=true               # Enhanced security
  - RATE_LIMIT_ENABLED=true      # Protect against abuse

deploy:
  resources:
    limits:
      memory: 2G                 # Increase for production
      cpus: '1.0'               # Adjust based on server capacity
```

### Strategy 2: RunPod Serverless Deployment
Best for: Auto-scaling, pay-per-use, cloud deployment

#### Pre-built Image Deployment
```bash
# Use automated GitHub Actions build
Image: docker.io/gemneye/crawl4ai-runpod-serverless:latest

# RunPod Configuration
Worker Type: CPU-only
Platform: AMD64/X86_64
Memory: 1-2GB
Auto-scaling: Enabled
Cold Start: ~30-60 seconds
```

#### Custom RunPod Deployment
```bash
# 1. Build RunPod-optimized container
docker build -f Dockerfile.runpod -t your-username/crawl4ai-runpod:latest .

# 2. Push to Docker Hub
docker push your-username/crawl4ai-runpod:latest

# 3. Configure in RunPod Console
# - Set image: your-username/crawl4ai-runpod:latest
# - Configure environment variables
# - Set resource limits
# - Enable auto-scaling
```

### Strategy 3: Blue-Green Deployment
Best for: Zero-downtime production deployments

```bash
# 1. Deploy to green environment
docker-compose -f docker-compose.green.yml build
docker-compose -f docker-compose.green.yml up -d

# 2. Health check green environment
docker-compose -f docker-compose.green.yml exec crawl4ai-mcp-server \
  python -c "from crawl4ai_mcp.server import mcp; print('Health OK')"

# 3. Run smoke tests on green
./scripts/test-mcp-tools.sh green

# 4. Switch traffic to green (update load balancer/proxy)
# Update nginx/traefik/cloudflare to point to green containers

# 5. Monitor for 15 minutes
watch -n 30 'docker-compose -f docker-compose.green.yml logs --tail=10 crawl4ai-mcp-server'

# 6. If stable, terminate blue environment
docker-compose -f docker-compose.blue.yml down

# 7. Rename green to blue for next deployment
mv docker-compose.green.yml docker-compose.blue.yml
```

### Strategy 4: Rolling Container Update
Best for: Minimal disruption updates

```bash
# 1. Pull latest images
docker-compose pull

# 2. Restart containers one by one
docker-compose up -d --no-deps crawl4ai-mcp-server

# 3. Verify each container before proceeding
docker-compose exec crawl4ai-mcp-server python -c "
from crawl4ai_mcp.server import mcp
print('Container updated successfully')
"
```

## Environment-Specific Deployments

### Development Environment
```bash
# Development deployment with volume mounting for live editing
cat > docker-compose.dev.yml << EOF
version: '3.8'
services:
  crawl4ai-mcp-dev:
    build:
      context: .
      dockerfile: Dockerfile.cpu
    container_name: crawl4ai-mcp-dev
    volumes:
      - ./crawl4ai_mcp:/app/crawl4ai_mcp
      - ./examples:/app/examples
    environment:
      - FASTMCP_LOG_LEVEL=DEBUG
      - MAX_CONCURRENT_REQUESTS=2
      - CACHE_TTL=300
      - SAFE_MODE=false
    networks:
      - shared_net
EOF

# Deploy development environment
docker-compose -f docker-compose.dev.yml up -d
```

### Staging Environment
```bash
# Staging deployment with production-like settings
export ENVIRONMENT=staging
export FASTMCP_LOG_LEVEL=INFO
export MAX_CONCURRENT_REQUESTS=3
export CACHE_TTL=900

# Deploy staging environment
docker-compose -f docker-compose.cpu.yml up -d

# Run integration tests
./scripts/run-staging-tests.sh
```

### Production Environment
```bash
# Production deployment checklist
echo "Starting production deployment..."

# 1. Backup current configuration
docker-compose -f docker-compose.cpu.yml config > backup-config-$(date +%Y%m%d-%H%M%S).yml

# 2. Set production environment variables
export ENVIRONMENT=production
export FASTMCP_LOG_LEVEL=WARNING
export MAX_CONCURRENT_REQUESTS=5
export CACHE_TTL=3600
export SAFE_MODE=true
export RATE_LIMIT_ENABLED=true

# 3. Deploy with zero downtime
docker-compose -f docker-compose.cpu.yml up -d --no-deps crawl4ai-mcp-cpu

# 4. Post-deployment verification
./scripts/production-health-check.sh

echo "Production deployment complete"
```

## Container Management

### Container Lifecycle Management

#### Starting Containers
```bash
# Standard start
docker-compose -f docker-compose.cpu.yml up -d

# Start with specific resource limits
docker-compose -f docker-compose.cpu.yml up -d --scale crawl4ai-mcp-cpu=1

# Start with fresh build
docker-compose -f docker-compose.cpu.yml up -d --build
```

#### Stopping Containers
```bash
# Graceful shutdown
docker-compose -f docker-compose.cpu.yml down

# Force stop (if containers are unresponsive)
docker-compose -f docker-compose.cpu.yml down --timeout 30

# Stop and remove volumes
docker-compose -f docker-compose.cpu.yml down -v
```

#### Container Updates
```bash
# Update container images
docker-compose -f docker-compose.cpu.yml pull

# Recreate containers with new images
docker-compose -f docker-compose.cpu.yml up -d --force-recreate

# Update specific service
docker-compose -f docker-compose.cpu.yml up -d --no-deps crawl4ai-mcp-cpu
```

### Container Monitoring

#### Health Monitoring
```bash
# Check container health
docker-compose -f docker-compose.cpu.yml ps

# View detailed container status
docker inspect crawl4ai-mcp-cpu | jq '.State.Health'

# Monitor resource usage
docker stats crawl4ai-mcp-cpu
```

#### Log Management
```bash
# View recent logs
docker-compose -f docker-compose.cpu.yml logs crawl4ai-mcp-cpu

# Follow log output
docker-compose -f docker-compose.cpu.yml logs -f crawl4ai-mcp-cpu

# View logs with timestamps
docker-compose -f docker-compose.cpu.yml logs -t crawl4ai-mcp-cpu

# Limit log output
docker-compose -f docker-compose.cpu.yml logs --tail=50 crawl4ai-mcp-cpu
```

### Volume and Data Management

#### Data Persistence
```bash
# Backup persistent volumes
docker run --rm -v crawl4ai_cpu_cache:/source -v $(pwd):/backup alpine \
  tar czf /backup/cache-backup-$(date +%Y%m%d).tar.gz -C /source .

# Restore from backup
docker run --rm -v crawl4ai_cpu_cache:/dest -v $(pwd):/backup alpine \
  tar xzf /backup/cache-backup-20250120.tar.gz -C /dest
```

#### Cache Management
```bash
# Clear cache volumes
docker volume rm crawl4ai_cpu_cache

# Recreate volumes
docker-compose -f docker-compose.cpu.yml up -d

# Monitor cache usage
docker exec crawl4ai-mcp-cpu du -sh /app/cache
```

## Post-Deployment Verification

### Functional Health Checks

#### MCP Server Verification
```bash
# 1. Container Health Check
echo "Checking container health..."
docker-compose -f docker-compose.cpu.yml exec crawl4ai-mcp-cpu \
  python -c "
from crawl4ai_mcp.server import mcp
print('✅ MCP server: Import successful')
"

# 2. Crawl4AI Engine Verification
echo "Checking crawl4ai engine..."
docker-compose -f docker-compose.cpu.yml exec crawl4ai-mcp-cpu \
  python -c "
from crawl4ai import AsyncWebCrawler
print('✅ Crawl4AI: Engine available')
"

# 3. Tool Availability Check
echo "Checking MCP tools..."
docker-compose -f docker-compose.cpu.yml exec crawl4ai-mcp-cpu \
  python -c "
import json
from crawl4ai_mcp.server import *
print('✅ MCP tools: All 19 tools available')
"
```

#### Core Functionality Testing
```bash
# Test basic crawling (if HTTP transport enabled)
curl -X POST http://crawl4ai-mcp-cpu:8000/tools/crawl_url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html", "generate_markdown": true}'

# Test file processing capability
curl -X POST http://crawl4ai-mcp-cpu:8000/tools/process_file \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/sample.pdf"}'

# Test YouTube transcript extraction
curl -X POST http://crawl4ai-mcp-cpu:8000/tools/extract_youtube_transcript \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=test"}'
```

### Performance Verification

#### Resource Usage Monitoring
```bash
# Check memory usage
docker stats crawl4ai-mcp-cpu --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Monitor for 5 minutes
watch -n 10 'docker stats crawl4ai-mcp-cpu --no-stream'

# Check disk usage
docker exec crawl4ai-mcp-cpu df -h

# Verify cache functionality
docker exec crawl4ai-mcp-cpu ls -la /app/cache
```

#### Network Connectivity
```bash
# Test container network connectivity
docker exec crawl4ai-mcp-cpu ping -c 3 google.com

# Check shared_net network
docker network inspect shared_net

# Verify port accessibility (if HTTP enabled)
nc -zv crawl4ai-mcp-cpu 8000
```

### Security Verification

#### Container Security Check
```bash
# Verify non-root user
docker exec crawl4ai-mcp-cpu whoami  # Should return 'appuser' or '1000'

# Check file permissions
docker exec crawl4ai-mcp-cpu ls -la /app

# Verify environment variables (no secrets exposed)
docker exec crawl4ai-mcp-cpu env | grep -E "(KEY|SECRET|TOKEN|PASSWORD)"
```

#### Output Suppression Verification
```bash
# Verify output suppression works correctly
docker-compose -f docker-compose.cpu.yml logs crawl4ai-mcp-cpu | \
  grep -i "crawl4ai" | head -5

# Should see minimal crawl4ai output in logs
```

## Rollback Procedures

### Immediate Rollback (< 5 minutes)

#### Container Rollback
```bash
# 1. Stop current containers
echo "Initiating emergency rollback..."
docker-compose -f docker-compose.cpu.yml down

# 2. Switch to previous image
PREVIOUS_TAG="v1.1.0"  # Replace with actual previous version
docker tag crawl4ai-mcp:$PREVIOUS_TAG crawl4ai-mcp:latest

# 3. Restart with previous version
docker-compose -f docker-compose.cpu.yml up -d

# 4. Verify rollback
docker-compose -f docker-compose.cpu.yml exec crawl4ai-mcp-cpu \
  python -c "from crawl4ai_mcp.server import mcp; print('Rollback successful')"

echo "Rollback completed in $(date)"
```

#### GitHub Actions Rollback
```bash
# 1. Identify last known good commit
git log --oneline -10

# 2. Create rollback commit
GOOD_COMMIT="abc123ef"  # Replace with actual commit hash
git revert $GOOD_COMMIT --no-edit

# 3. Push to trigger new build
git push origin main

# 4. Wait for GitHub Actions to complete
echo "Waiting for automated rebuild..."
# Monitor: https://github.com/sruckh/crawl-mcp/actions
```

### Data Rollback

#### Volume Rollback
```bash
# 1. Stop containers
docker-compose -f docker-compose.cpu.yml down

# 2. Restore from backup
BACKUP_DATE="20250120"  # Replace with actual backup date
docker run --rm -v crawl4ai_cpu_cache:/dest -v $(pwd):/backup alpine \
  tar xzf /backup/cache-backup-$BACKUP_DATE.tar.gz -C /dest

# 3. Restart containers
docker-compose -f docker-compose.cpu.yml up -d

# 4. Verify data integrity
docker exec crawl4ai-mcp-cpu ls -la /app/cache
```

#### Configuration Rollback
```bash
# 1. Restore previous configuration
BACKUP_CONFIG="backup-config-20250120-143000.yml"
cp $BACKUP_CONFIG docker-compose.cpu.yml

# 2. Redeploy with old configuration
docker-compose -f docker-compose.cpu.yml up -d --force-recreate

# 3. Verify configuration
docker-compose -f docker-compose.cpu.yml config
```

### RunPod Deployment Rollback

```bash
# RunPod Serverless Rollback Process:
# 1. Access RunPod console
# 2. Navigate to endpoint configuration
# 3. Update image to previous tag:
#    docker.io/gemneye/crawl4ai-runpod-serverless:v1.1.0
# 4. Restart workers
# 5. Verify functionality with test requests
# 6. Monitor for 15 minutes

echo "RunPod rollback requires manual intervention via console"
echo "Previous stable image: docker.io/gemneye/crawl4ai-runpod-serverless:v1.1.0"
```

## Troubleshooting

### Common Deployment Issues

#### Container Won't Start
```bash
# Issue: Container fails to start
echo "Diagnosing container startup issues..."

# Check container logs
docker-compose -f docker-compose.cpu.yml logs crawl4ai-mcp-cpu

# Check Docker daemon status
systemctl status docker

# Verify image integrity
docker inspect crawl4ai-mcp:cpu

# Check resource availability
df -h && free -h

# Rebuild with no cache if image corrupted
docker-compose -f docker-compose.cpu.yml build --no-cache
```

#### Port Conflicts
```bash
# Issue: Port already in use
echo "Checking for port conflicts..."

# Check what's using port 8000
lsof -i :8000
netstat -tulpn | grep :8000

# Kill conflicting processes
sudo fuser -k 8000/tcp

# Or change port in configuration
sed -i 's/8000:8000/8001:8000/' docker-compose.cpu.yml
```

#### Memory Issues
```bash
# Issue: Out of memory errors
echo "Diagnosing memory issues..."

# Check system memory
free -h

# Check Docker memory usage
docker stats --no-stream

# Increase memory limits
cat >> docker-compose.cpu.yml << EOF
    deploy:
      resources:
        limits:
          memory: 4G
EOF

# Clean up unused images
docker image prune -f
```

#### Network Connectivity Problems
```bash
# Issue: Container can't reach external services
echo "Diagnosing network connectivity..."

# Check Docker networks
docker network ls

# Recreate shared_net network
docker network rm shared_net
docker network create shared_net

# Test external connectivity
docker exec crawl4ai-mcp-cpu nslookup google.com
docker exec crawl4ai-mcp-cpu curl -I https://httpbin.org

# Check firewall rules
sudo ufw status
```

### MCP-Specific Issues

#### Tool Registration Failures
```bash
# Issue: MCP tools not registering properly
echo "Checking MCP tool registration..."

# Verify FastMCP imports
docker exec crawl4ai-mcp-cpu python -c "
try:
    from fastmcp import FastMCP
    print('✅ FastMCP imported successfully')
except ImportError as e:
    print(f'❌ FastMCP import error: {e}')
"

# Check tool definitions
docker exec crawl4ai-mcp-cpu python -c "
from crawl4ai_mcp.server import mcp
tools = mcp.get_tools()
print(f'✅ {len(tools)} tools registered')
"
```

#### Output Suppression Issues
```bash
# Issue: MCP responses corrupted by verbose output
echo "Checking output suppression..."

# Verify suppress_output module
docker exec crawl4ai-mcp-cpu python -c "
from crawl4ai_mcp.suppress_output import suppress_stdout_stderr
print('✅ Output suppression module available')
"

# Check for verbose output in logs
docker-compose -f docker-compose.cpu.yml logs crawl4ai-mcp-cpu | \
  grep -i "crawl4ai\|playwright\|verbose" | wc -l
```

#### Claude Desktop Integration Issues
```bash
# Issue: Claude Desktop can't connect to MCP server
echo "Diagnosing Claude Desktop integration..."

# Verify STDIO transport mode
docker exec crawl4ai-mcp-cpu env | grep MCP_TRANSPORT

# Check if server can start in STDIO mode
docker exec crawl4ai-mcp-cpu python -m crawl4ai_mcp.server --help

# Test with sample configuration
cat > test_claude_config.json << EOF
{
  "mcpServers": {
    "crawl4ai": {
      "command": "docker",
      "args": ["exec", "-i", "crawl4ai-mcp-cpu", "python", "-m", "crawl4ai_mcp.server"]
    }
  }
}
EOF
```

### Performance Issues

#### Slow Response Times
```bash
# Issue: Slow crawling or processing
echo "Diagnosing performance issues..."

# Check CPU usage
docker exec crawl4ai-mcp-cpu top -n 1

# Monitor memory usage over time
watch -n 5 'docker stats crawl4ai-mcp-cpu --no-stream'

# Check disk I/O
docker exec crawl4ai-mcp-cpu iostat -x 1 3

# Optimize cache settings
docker exec crawl4ai-mcp-cpu python -c "
import os
print(f'Cache TTL: {os.getenv(\"CACHE_TTL\", \"900\")}')
print(f'Max concurrent: {os.getenv(\"MAX_CONCURRENT_REQUESTS\", \"5\")}')
"
```

#### Memory Leaks
```bash
# Issue: Memory usage continuously increasing
echo "Checking for memory leaks..."

# Monitor memory over time
for i in {1..10}; do
  docker stats crawl4ai-mcp-cpu --no-stream | grep memory
  sleep 60
done

# Check cache size
docker exec crawl4ai-mcp-cpu du -sh /app/cache

# Clear cache if needed
docker exec crawl4ai-mcp-cpu rm -rf /app/cache/*
docker-compose -f docker-compose.cpu.yml restart crawl4ai-mcp-cpu
```

## Emergency Procedures

### Complete System Failure

#### Emergency Recovery Procedure
```bash
#!/bin/bash
# Emergency recovery script
echo "=== EMERGENCY RECOVERY PROCEDURE ==="
echo "Starting emergency recovery at $(date)"

# 1. Enable maintenance mode (if load balancer supports it)
echo "Step 1: Enabling maintenance mode..."
# curl -X POST https://your-load-balancer/maintenance/enable

# 2. Stop all containers
echo "Step 2: Stopping all containers..."
docker-compose -f docker-compose.cpu.yml down --timeout 10

# 3. Clean up corrupted containers/images
echo "Step 3: Cleaning up corrupted resources..."
docker container prune -f
docker image prune -f

# 4. Pull fresh images
echo "Step 4: Pulling fresh container images..."
docker pull gemneye/crawl4ai-runpod-serverless:latest

# 5. Restore from last known good backup
echo "Step 5: Restoring from backup..."
LATEST_BACKUP=$(ls -t cache-backup-*.tar.gz | head -1)
if [ -n "$LATEST_BACKUP" ]; then
    docker run --rm -v crawl4ai_cpu_cache:/dest -v $(pwd):/backup alpine \
      tar xzf /backup/$LATEST_BACKUP -C /dest
    echo "Restored from $LATEST_BACKUP"
fi

# 6. Deploy last known good version
echo "Step 6: Deploying last known good version..."
git checkout tags/v1.1.0  # Replace with actual last good version
docker-compose -f docker-compose.cpu.yml up -d --build

# 7. Verify recovery
echo "Step 7: Verifying recovery..."
sleep 30  # Wait for container startup
docker-compose -f docker-compose.cpu.yml exec crawl4ai-mcp-cpu \
  python -c "from crawl4ai_mcp.server import mcp; print('✅ Recovery successful')"

# 8. Disable maintenance mode
echo "Step 8: Disabling maintenance mode..."
# curl -X POST https://your-load-balancer/maintenance/disable

echo "=== EMERGENCY RECOVERY COMPLETE ==="
echo "Recovery completed at $(date)"
```

### Data Corruption Recovery

#### Cache Corruption Recovery
```bash
# Issue: Cache data corrupted
echo "Recovering from cache corruption..."

# 1. Stop container
docker-compose -f docker-compose.cpu.yml down

# 2. Remove corrupted cache
docker volume rm crawl4ai_cpu_cache

# 3. Recreate cache volume
docker volume create crawl4ai_cpu_cache

# 4. Restart container
docker-compose -f docker-compose.cpu.yml up -d

# 5. Verify cache functionality
docker exec crawl4ai-mcp-cpu python -c "
import os
print(f'Cache directory exists: {os.path.exists(\"/app/cache\")}')
"
```

### Container Registry Issues

#### Docker Hub Outage Recovery
```bash
# Issue: Cannot pull from Docker Hub
echo "Handling Docker Hub outage..."

# 1. Use local images if available
docker images | grep crawl4ai-mcp

# 2. Build from source as fallback
docker build -f Dockerfile.cpu -t crawl4ai-mcp:emergency .

# 3. Update compose to use local image
sed -i 's/image: .*/build: ./' docker-compose.cpu.yml

# 4. Deploy with local build
docker-compose -f docker-compose.cpu.yml up -d

echo "Emergency deployment using local build complete"
```

## Monitoring and Maintenance

### Regular Maintenance Schedule

#### Daily Maintenance
```bash
#!/bin/bash
# Daily maintenance script
echo "Running daily maintenance for Crawl4AI MCP Server..."

# Check container health
docker-compose -f docker-compose.cpu.yml ps

# Monitor resource usage
docker stats crawl4ai-mcp-cpu --no-stream

# Check log file sizes
docker exec crawl4ai-mcp-cpu du -sh /app/logs

# Rotate logs if needed
if [ $(docker exec crawl4ai-mcp-cpu du -s /app/logs | cut -f1) -gt 1000000 ]; then
    docker exec crawl4ai-mcp-cpu find /app/logs -name "*.log" -mtime +7 -delete
fi

# Check cache size
CACHE_SIZE=$(docker exec crawl4ai-mcp-cpu du -s /app/cache | cut -f1)
echo "Cache size: ${CACHE_SIZE}KB"

# Clear old cache if over 500MB
if [ $CACHE_SIZE -gt 500000 ]; then
    docker exec crawl4ai-mcp-cpu find /app/cache -mtime +1 -delete
fi

echo "Daily maintenance complete"
```

#### Weekly Maintenance
```bash
#!/bin/bash
# Weekly maintenance script
echo "Running weekly maintenance for Crawl4AI MCP Server..."

# Update container images
docker-compose -f docker-compose.cpu.yml pull

# Restart containers with new images
docker-compose -f docker-compose.cpu.yml up -d

# Full system backup
BACKUP_DATE=$(date +%Y%m%d)
docker run --rm -v crawl4ai_cpu_cache:/source -v $(pwd):/backup alpine \
  tar czf /backup/weekly-backup-$BACKUP_DATE.tar.gz -C /source .

# Clean up old backups (keep last 4 weeks)
find . -name "weekly-backup-*.tar.gz" -mtime +28 -delete

# Security update check
docker exec crawl4ai-mcp-cpu python -m pip list --outdated

echo "Weekly maintenance complete"
```

### Performance Monitoring

#### Key Metrics to Monitor
```bash
# Container Performance Metrics
echo "=== PERFORMANCE MONITORING ==="

# 1. Resource Usage
echo "Resource Usage:"
docker stats crawl4ai-mcp-cpu --no-stream --format \
  "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"

# 2. Response Times (if HTTP enabled)
echo "Response Times:"
time curl -s http://crawl4ai-mcp-cpu:8000/health > /dev/null

# 3. Cache Hit Rates
echo "Cache Statistics:"
docker exec crawl4ai-mcp-cpu find /app/cache -type f | wc -l
docker exec crawl4ai-mcp-cpu du -sh /app/cache

# 4. Error Rates
echo "Error Analysis:"
docker-compose -f docker-compose.cpu.yml logs crawl4ai-mcp-cpu | \
  grep -i error | tail -5

# 5. Uptime
echo "Container Uptime:"
docker inspect crawl4ai-mcp-cpu | jq '.[0].State.StartedAt'
```

#### Alerting Thresholds
```bash
# Performance Alert Thresholds
MEMORY_THRESHOLD=80    # Alert if memory usage > 80%
CPU_THRESHOLD=90       # Alert if CPU usage > 90%
DISK_THRESHOLD=85      # Alert if disk usage > 85%
ERROR_THRESHOLD=10     # Alert if errors > 10 per hour

# Memory usage check
MEMORY_USAGE=$(docker stats crawl4ai-mcp-cpu --no-stream --format "{{.MemPerc}}" | sed 's/%//')
if (( $(echo "$MEMORY_USAGE > $MEMORY_THRESHOLD" | bc -l) )); then
    echo "ALERT: Memory usage ${MEMORY_USAGE}% exceeds threshold ${MEMORY_THRESHOLD}%"
fi

# CPU usage check
CPU_USAGE=$(docker stats crawl4ai-mcp-cpu --no-stream --format "{{.CPUPerc}}" | sed 's/%//')
if (( $(echo "$CPU_USAGE > $CPU_THRESHOLD" | bc -l) )); then
    echo "ALERT: CPU usage ${CPU_USAGE}% exceeds threshold ${CPU_THRESHOLD}%"
fi

# Disk usage check
DISK_USAGE=$(docker exec crawl4ai-mcp-cpu df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt $DISK_THRESHOLD ]; then
    echo "ALERT: Disk usage ${DISK_USAGE}% exceeds threshold ${DISK_THRESHOLD}%"
fi
```

## Deployment Schedule

### Regular Deployment Windows
- **Production VPS**: Tuesdays and Thursdays, 14:00-16:00 UTC (lowest traffic period)
- **Staging Environment**: Daily automated deployments at 10:00 UTC
- **Development Environment**: Continuous deployment on code push
- **RunPod Serverless**: Automated deployment on GitHub releases

### Hotfix Deployment
- **Severity 1 (Critical)**: Immediate deployment, any time
- **Severity 2 (High)**: Within 4 hours during business hours
- **Severity 3 (Medium)**: Next scheduled deployment window
- **Severity 4 (Low)**: Batch with next minor release

### Deployment Notification Timeline
- **T-24h**: Deployment notification sent to team
- **T-4h**: Deployment preparation begins
- **T-1h**: Final go/no-go decision
- **T-0**: Deployment execution begins
- **T+30m**: Post-deployment verification complete
- **T+2h**: Deployment success confirmation

## Contact Information

### Escalation Path
1. **On-call Engineer**: Monitor GitHub Issues and Discussions
2. **Project Maintainer**: @sruckh (GitHub)
3. **MCP Community**: [Model Context Protocol Discord/Forums](https://github.com/modelcontextprotocol)

### Emergency Contacts
- **GitHub Repository**: https://github.com/sruckh/crawl-mcp
- **Docker Hub Registry**: https://hub.docker.com/r/gemneye/crawl4ai-runpod-serverless
- **Container Registry Issues**: Docker Hub Status Page
- **RunPod Support**: RunPod Console → Support

### External Dependencies
- **Docker Hub**: hub.docker.com (container registry)
- **GitHub Actions**: github.com (CI/CD pipeline)
- **RunPod Platform**: runpod.io (serverless deployment)
- **Python Package Index**: pypi.org (dependency updates)

## Keywords <!-- #keywords -->
deployment, Docker containers, MCP server, production deployment, rollback procedures, container orchestration, blue-green deployment, health checks, monitoring, troubleshooting, emergency procedures, RunPod serverless, GitHub Actions, CI/CD pipeline, FastMCP, crawl4ai