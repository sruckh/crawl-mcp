# Docker Deployment Guide for Crawl4AI MCP Server

This guide covers deploying the Crawl4AI MCP Server using Docker with secure network isolation.

## 🐳 Quick Start

### Option A: CPU-Only Lightweight Build (Recommended for Local)

```bash
# Build and start CPU-optimized container (no CUDA dependencies)
docker-compose -f docker-compose.cpu.yml build
docker-compose -f docker-compose.cpu.yml up -d

# Check status
docker-compose -f docker-compose.cpu.yml ps
docker-compose -f docker-compose.cpu.yml logs crawl4ai-mcp-cpu
```

### Option B: Standard Build (May Include CUDA)

```bash
# Build the standard image (includes potential CUDA dependencies)
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs crawl4ai-mcp-server
```

### Option C: Ultra-Lightweight Build

```bash
# Build minimal footprint container
docker build -f Dockerfile.lightweight -t crawl4ai-mcp:lightweight .
docker run -d --name crawl4ai-lightweight --network shared_net crawl4ai-mcp:lightweight
```

### 2. Test the Container

```bash
# Health check
docker-compose exec crawl4ai-mcp-server python -c "import asyncio; from crawl4ai_mcp.server import mcp; print('✅ Server healthy')"

# Test basic functionality
docker-compose exec crawl4ai-mcp-server python -c "from crawl4ai import AsyncWebCrawler; print('✅ Crawl4AI available')"
```

## 📊 Container Comparison

| Feature | Standard | CPU-Optimized | Ultra-Lightweight |
|---------|----------|---------------|-------------------|
| **Dockerfile** | `Dockerfile` | `Dockerfile.cpu` | `Dockerfile.lightweight` |
| **Compose File** | `docker-compose.yml` | `docker-compose.cpu.yml` | Manual `docker run` |
| **CUDA Dependencies** | ❌ May include | ✅ Excluded | ✅ Explicitly blocked |
| **ML Libraries** | Full sentence-transformers | Basic scikit-learn | CPU-only torch |
| **Image Size** | ~2-3GB | ~1.5-2GB | ~1-1.5GB |
| **Memory Usage** | 2GB limit | 1GB limit | <1GB |
| **Use Case** | Full features | Local development | Minimal footprint |
| **Build Time** | Longest | Medium | Fastest |

### Recommendations:
- **Local Development**: Use `docker-compose.cpu.yml` (CPU-optimized)
- **Resource Constrained**: Use `Dockerfile.lightweight` (Ultra-lightweight)
- **Production/RunPod**: Use `Dockerfile.runpod` (Serverless optimized)

### Quick Build Comparison:
```bash
# Run automated build comparison
./scripts/build-cpu-containers.sh
```

## 🔧 Configuration

### Environment Variables

Copy and configure the environment file:

```bash
cp .env.example .env
# Edit .env with your specific configuration
```

Key environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `FASTMCP_LOG_LEVEL` | `INFO` | Logging level |
| `MCP_TRANSPORT` | `stdio` | Transport protocol (stdio/http) |
| `MAX_FILE_SIZE_MB` | `100` | Maximum file processing size |
| `MAX_CONCURRENT_REQUESTS` | `5` | Concurrent request limit |
| `CACHE_TTL` | `900` | Cache time-to-live (seconds) |

### Optional LLM API Keys

For AI-powered features, configure these in your `.env` file:

```bash
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## 🌐 Network Configuration

### Shared Network Access

The container connects to the `shared_net` network without exposing ports to localhost:

- **Internal Access**: Available to other containers on `shared_net`
- **Service Name**: `crawl4ai-mcp-server`
- **Internal Ports**: 8000 (if HTTP transport enabled)

### Accessing from Other Containers

```yaml
# In another container's docker-compose.yml
services:
  your-app:
    networks:
      - shared_net
    environment:
      - MCP_SERVER_URL=http://crawl4ai-mcp-server:8000

networks:
  shared_net:
    external: true
```

## 🔒 Security Features

### Container Security

- **Non-root user**: Runs as user ID 1000
- **Read-only filesystem**: Application code is read-only
- **Resource limits**: Memory and CPU constraints
- **Health checks**: Automated container health monitoring

### Network Security

- **No localhost exposure**: Ports only accessible via Docker network
- **Network isolation**: Contained within `shared_net`
- **Safe mode**: Content filtering enabled by default

## 📊 Monitoring and Logs

### View Logs

```bash
# Real-time logs
docker-compose logs -f crawl4ai-mcp-server

# Last 100 lines
docker-compose logs --tail=100 crawl4ai-mcp-server
```

### Health Monitoring

```bash
# Check health status
docker-compose exec crawl4ai-mcp-server healthcheck

# Monitor resource usage
docker stats crawl4ai-mcp-server
```

### Persistent Data

The container uses Docker volumes for persistent data:

- `crawl4ai_cache`: Crawling cache data
- `crawl4ai_logs`: Application logs

## 🚀 HTTP Transport Mode

To enable HTTP API access, modify your `.env` file:

```bash
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

Then restart the container:

```bash
docker-compose down
docker-compose up -d
```

### HTTP API Testing

From another container on `shared_net`:

```bash
# Health check
curl http://crawl4ai-mcp-server:8000/health

# Example crawl request
curl -X POST http://crawl4ai-mcp-server:8000/tools/crawl_url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "generate_markdown": true}'
```

## 🔧 Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check build logs
docker-compose build --no-cache

# Check startup logs
docker-compose logs crawl4ai-mcp-server
```

**Playwright issues:**
```bash
# Rebuild with fresh Playwright installation
docker-compose build --no-cache
```

**Network connectivity:**
```bash
# Verify shared_net exists
docker network ls | grep shared_net

# Create network if missing
docker network create shared_net
```

**Permission issues:**
```bash
# Check file ownership
docker-compose exec crawl4ai-mcp-server ls -la /app

# Fix if needed (rebuild may be required)
docker-compose build --no-cache
```

### Performance Tuning

**Memory usage:**
```bash
# Monitor memory
docker stats crawl4ai-mcp-server

# Adjust limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G  # Increase if needed
```

**Concurrent requests:**
```bash
# Adjust in .env file
MAX_CONCURRENT_REQUESTS=10
```

## 🔄 Updates and Maintenance

### Update the Container

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Configuration

```bash
# Backup environment and compose files
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup

# Backup volumes
docker run --rm -v crawl4ai_cache:/source -v $(pwd):/backup alpine tar czf /backup/cache-backup.tar.gz -C /source .
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (careful - this deletes cached data)
docker-compose down -v

# Remove images
docker image rm crawl-mcp_crawl4ai-mcp-server
```

## 📚 Integration Examples

### With Claude Desktop

Configure Claude Desktop to use the containerized MCP server:

```json
{
  "mcpServers": {
    "crawl4ai-docker": {
      "command": "docker",
      "args": [
        "exec", "-i", "crawl4ai-mcp-server", 
        "python", "-m", "crawl4ai_mcp.server"
      ]
    }
  }
}
```

### With Other MCP Clients

For HTTP transport mode, use the internal service URL:

```
http://crawl4ai-mcp-server:8000/mcp
```

## 🔍 Advanced Configuration

### Custom Dockerfile Modifications

For custom requirements, modify the Dockerfile:

```dockerfile
# Add custom dependencies
RUN pip install your-custom-package

# Install additional system packages
RUN apt-get update && apt-get install -y your-package
```

### Multi-stage Development

```bash
# Development mode with volume mounting
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

This setup provides a secure, scalable, and maintainable deployment of the Crawl4AI MCP Server in a containerized environment.