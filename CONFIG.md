# CONFIG.md

## Environment Variables

### MCP Server Core Configuration
Core MCP (Model Context Protocol) server settings for transport and logging.

```bash
# MCP Transport Protocol
MCP_TRANSPORT=stdio                    # stdio (default) | http | websocket
MCP_HOST=0.0.0.0                      # HTTP transport host (if http enabled)
MCP_PORT=8000                         # HTTP transport port (if http enabled)

# Python Environment
FASTMCP_LOG_LEVEL=INFO                # DEBUG | INFO | WARNING | ERROR
PYTHONPATH=/app                       # Container application path
PYTHONUNBUFFERED=1                    # Force unbuffered output for containers
```

### AI Model Configuration (Optional)
LLM API keys for AI-powered extraction features. All features work without these keys.

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-key-here  # Get from: https://platform.openai.com/api-keys
OPENAI_BASE_URL=https://api.openai.com/v1  # Custom endpoint (optional)

# Anthropic Configuration  
ANTHROPIC_API_KEY=sk-ant-your-key-here # Get from: https://console.anthropic.com/

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Google/Gemini Configuration
GOOGLE_API_KEY=your-google-api-key-here
```

### Performance & Resource Limits
Configure resource usage and performance parameters.

```bash
# File Processing Limits
MAX_FILE_SIZE_MB=100                   # Maximum file size for processing
MAX_CONCURRENT_REQUESTS=5              # Concurrent request limit (3 for CPU-only)
CACHE_TTL=900                         # Cache time-to-live in seconds (15 minutes)

# Browser Automation
PLAYWRIGHT_TIMEOUT=60                  # Browser operation timeout in seconds
PLAYWRIGHT_HEADLESS=true              # Run browser in headless mode

# Memory Management
CRAWL4AI_CACHE_SIZE=1000              # Number of cached pages
CRAWL4AI_CACHE_TTL=3600               # Cache expiration in seconds
```

### CPU-Only Optimization Settings
Environment variables for disabling GPU/ML features in CPU-optimized containers.

```bash
# Disable Heavy ML Features (CPU-only containers)
CRAWL4AI_DISABLE_SENTENCE_TRANSFORMERS=true  # Disable sentence transformers
CRAWL4AI_DISABLE_TORCH=true                  # Disable PyTorch features
CUDA_VISIBLE_DEVICES=""                      # Block CUDA device access

# Alternative: Force CPU-only mode
TORCH_DEVICE=cpu                             # Force CPU for PyTorch operations
```

### Feature Toggles
Enable or disable specific MCP tools and features.

```bash
# Tool Availability
ENABLE_FILE_PROCESSING=true           # PDF, Office, ZIP file processing
ENABLE_YOUTUBE_TRANSCRIPTS=true       # YouTube transcript extraction
ENABLE_GOOGLE_SEARCH=true            # Google search integration
ENABLE_BATCH_PROCESSING=true          # Batch operation support

# Content Processing Features
ENABLE_INTELLIGENT_EXTRACTION=true    # AI-powered content extraction
ENABLE_ENTITY_EXTRACTION=true         # Named entity recognition
ENABLE_STRUCTURED_EXTRACTION=true     # JSON schema extraction
```

### Security Configuration
Security-related settings for safe operation.

```bash
# Content Safety
SAFE_MODE=true                        # Enable content filtering
BLOCK_PRIVATE_IPS=true               # Block private IP addresses
ALLOWED_DOMAINS=""                    # Comma-separated allowed domains (empty = all)
BLOCKED_DOMAINS=""                    # Comma-separated blocked domains

# Rate Limiting
RATE_LIMIT_ENABLED=true              # Enable rate limiting
RATE_LIMIT_REQUESTS=100              # Requests per window
RATE_LIMIT_WINDOW=3600               # Rate limit window in seconds (1 hour)

# Network Security
USER_AGENT="Crawl4AI-MCP/1.0"       # Custom User-Agent string
RESPECT_ROBOTS_TXT=true              # Respect robots.txt files
```

## Docker Environment Configuration

### Container-Specific Variables
Variables specific to Docker deployment with different optimization levels.

#### Standard Container (`Dockerfile`)
```bash
# Full-featured container with potential CUDA dependencies
MCP_TRANSPORT=stdio
FASTMCP_LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=5
MEMORY_LIMIT=2G
CPU_LIMIT=1.0
```

#### CPU-Optimized Container (`Dockerfile.cpu`)
```bash
# Optimized for VPS deployment without GPU
CRAWL4AI_DISABLE_SENTENCE_TRANSFORMERS=true
CRAWL4AI_DISABLE_TORCH=true
MAX_CONCURRENT_REQUESTS=3
MEMORY_LIMIT=1G
CPU_LIMIT=0.5
```

#### Lightweight Container (`Dockerfile.lightweight`)
```bash
# Minimal footprint container
CRAWL4AI_DISABLE_SENTENCE_TRANSFORMERS=true
CRAWL4AI_DISABLE_TORCH=true
CUDA_VISIBLE_DEVICES=""
TORCH_DEVICE=cpu
MAX_CONCURRENT_REQUESTS=2
MEMORY_LIMIT=512M
CPU_LIMIT=0.25
```

#### RunPod Serverless (`Dockerfile.runpod`)
```bash
# RunPod serverless optimization
CRAWL4AI_DISABLE_SENTENCE_TRANSFORMERS=true
PLATFORM=linux/amd64
AUTO_SCALING=true
MEMORY_LIMIT=1G
```

### Docker Compose Configuration
Environment precedence and inheritance in Docker Compose deployments.

#### Standard Deployment (`docker-compose.yml`)
```yaml
environment:
  - FASTMCP_LOG_LEVEL=INFO
  - PYTHONPATH=/app
  - PYTHONUNBUFFERED=1
  - MAX_FILE_SIZE_MB=100
  - MAX_CONCURRENT_REQUESTS=5
  - CACHE_TTL=900
```

#### CPU-Optimized Deployment (`docker-compose.cpu.yml`)
```yaml
environment:
  - FASTMCP_LOG_LEVEL=INFO
  - PYTHONPATH=/app
  - PYTHONUNBUFFERED=1
  - CRAWL4AI_DISABLE_SENTENCE_TRANSFORMERS=true
  - CRAWL4AI_DISABLE_TORCH=true
  - MAX_CONCURRENT_REQUESTS=3
  - CACHE_TTL=900
```

### Environment File Management
Configuration file hierarchy and precedence rules.

#### `.env` File Priority
1. **Container environment variables** (highest priority)
2. **Docker Compose environment section**
3. **`.env` file in project root**
4. **Default values in code** (lowest priority)

#### Environment File Example
```bash
# Copy .env.example to .env and customize
cp .env.example .env

# Key variables to customize:
FASTMCP_LOG_LEVEL=DEBUG              # For development
MCP_TRANSPORT=http                   # For HTTP API access
OPENAI_API_KEY=sk-proj-your-key      # For AI features
MAX_CONCURRENT_REQUESTS=10           # For high-traffic deployment
```

## Claude Desktop Integration

### MCP Client Configuration
Configuration for Claude Desktop and other MCP clients.

#### STDIO Transport (Default)
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "docker",
      "args": [
        "exec", "-i", "crawl4ai-mcp-server",
        "python", "-m", "crawl4ai_mcp.server"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### HTTP Transport
```json
{
  "mcpServers": {
    "crawl4ai-http": {
      "command": "node",
      "args": ["-e", "require('http').get('http://crawl4ai-mcp-server:8000/mcp')"],
      "env": {
        "MCP_TRANSPORT": "http"
      }
    }
  }
}
```

### Transport Protocol Configuration
Configure different transport methods for various deployment scenarios.

| Transport | Use Case | Configuration | Performance |
|-----------|----------|---------------|-------------|
| **STDIO** | Claude Desktop, local clients | Default, no network config | Fastest |
| **HTTP** | Web integration, REST API | `MCP_TRANSPORT=http` + port | Good |
| **WebSocket** | Real-time applications | `MCP_TRANSPORT=websocket` | Good |

## GitHub Actions CI/CD Configuration

### Build Environment Variables
Variables used in automated builds and deployments.

#### Automated Docker Builds (`.github/workflows/build-runpod-docker.yml`)
```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: gemneye/crawl4ai-runpod-serverless
  PLATFORMS: linux/amd64

secrets:
  DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
  DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

#### Build Matrix Configuration
```yaml
strategy:
  matrix:
    container_variant: [standard, cpu, lightweight, runpod]
    include:
      - container_variant: cpu
        dockerfile: Dockerfile.cpu
        memory_limit: 1G
      - container_variant: lightweight  
        dockerfile: Dockerfile.lightweight
        memory_limit: 512M
```

### Deployment Configuration
Environment-specific deployment configurations.

#### Development Environment
```bash
FASTMCP_LOG_LEVEL=DEBUG
MCP_TRANSPORT=http
SAFE_MODE=false
ENABLE_FILE_PROCESSING=true
CACHE_TTL=300  # 5 minutes for faster testing
```

#### Staging Environment
```bash
FASTMCP_LOG_LEVEL=INFO
MCP_TRANSPORT=stdio
SAFE_MODE=true
ENABLE_FILE_PROCESSING=true
CACHE_TTL=900  # 15 minutes
```

#### Production Environment
```bash
FASTMCP_LOG_LEVEL=WARNING
MCP_TRANSPORT=stdio
SAFE_MODE=true
ENABLE_FILE_PROCESSING=true
CACHE_TTL=3600  # 1 hour
RATE_LIMIT_ENABLED=true
```

## Performance Tuning

### Resource Optimization Matrix
Configure resources based on deployment scenario and expected load.

| Scenario | Memory | CPU | Concurrent | Cache TTL | Use Case |
|----------|--------|-----|------------|-----------|----------|
| **Development** | 512MB | 0.25 | 2 | 300s | Local testing |
| **VPS (CPU-only)** | 1GB | 0.5 | 3 | 900s | Production deployment |
| **Standard** | 2GB | 1.0 | 5 | 900s | Full features |
| **High Traffic** | 4GB | 2.0 | 10 | 3600s | Heavy usage |
| **RunPod** | 1GB | Auto | 5 | 900s | Serverless scaling |

### Browser Performance Configuration
Playwright browser automation performance settings.

```bash
# Browser Resource Limits
PLAYWRIGHT_TIMEOUT=60                 # Total operation timeout
PLAYWRIGHT_NAVIGATION_TIMEOUT=30      # Page navigation timeout
PLAYWRIGHT_WAIT_TIMEOUT=10           # Element wait timeout

# Browser Pool Management
BROWSER_POOL_SIZE=3                  # Number of browser instances
BROWSER_REUSE_PAGES=true            # Reuse browser pages
BROWSER_HEADLESS=true               # Headless mode for performance

# Memory Management
BROWSER_MAX_PAGES=10                # Max pages per browser instance
BROWSER_PAGE_TIMEOUT=300            # Page idle timeout in seconds
```

### Cache Configuration
Multi-layer caching strategy for optimal performance.

```bash
# Memory Cache (fastest)
MEMORY_CACHE_SIZE=100               # Number of items in memory cache
MEMORY_CACHE_TTL=300                # Memory cache TTL in seconds

# Disk Cache (persistent)
DISK_CACHE_SIZE=1000                # Number of items in disk cache
DISK_CACHE_TTL=3600                 # Disk cache TTL in seconds
DISK_CACHE_PATH=/app/cache          # Cache directory path

# Redis Cache (distributed)
REDIS_URL=redis://localhost:6379    # Redis connection URL
REDIS_CACHE_TTL=1800                # Redis cache TTL in seconds
REDIS_KEY_PREFIX=crawl4ai:           # Key prefix for namespacing
```

## Configuration Validation

### Startup Validation
Automated validation of configuration values during server startup.

```bash
# Enable configuration validation
VALIDATE_CONFIG=true                 # Validate config on startup
STRICT_VALIDATION=false              # Fail on warnings (false for warnings only)

# Validation Rules
MIN_MEMORY_MB=256                    # Minimum required memory
MIN_DISK_SPACE_MB=1000              # Minimum required disk space
REQUIRED_VARS="FASTMCP_LOG_LEVEL"   # Comma-separated required variables
```

### Health Check Configuration
Container health monitoring and status reporting.

```bash
# Health Check Settings
HEALTH_CHECK_ENABLED=true           # Enable container health checks
HEALTH_CHECK_INTERVAL=30            # Check interval in seconds
HEALTH_CHECK_TIMEOUT=10             # Check timeout in seconds
HEALTH_CHECK_RETRIES=3              # Number of retries before unhealthy

# Health Check Endpoints (HTTP mode)
HEALTH_ENDPOINT=/health             # Health check endpoint path
METRICS_ENDPOINT=/metrics           # Metrics endpoint path
STATUS_ENDPOINT=/status             # Status endpoint path
```

## Security Best Practices

### API Key Management
Secure handling of API keys and sensitive configuration.

```bash
# Development (local only)
OPENAI_API_KEY=sk-proj-dev-key      # Direct key for development

# Production (recommended)
OPENAI_API_KEY_FILE=/run/secrets/openai_key   # Docker secret file
ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_key

# Environment-based (staging)
export OPENAI_API_KEY=$(vault kv get -field=key secret/openai)
```

### Network Security Configuration
Secure network access and content filtering.

```bash
# Network Access Control
ALLOWED_PROTOCOLS=http,https         # Allowed URL protocols
BLOCKED_TLD=.onion,.bit             # Blocked top-level domains
MAX_REDIRECT_HOPS=5                 # Maximum redirect following
DNS_TIMEOUT=10                      # DNS resolution timeout

# Content Security Policy
MAX_RESPONSE_SIZE_MB=50             # Maximum response size
BLOCK_EXECUTABLE_CONTENT=true       # Block executable downloads
SCAN_CONTENT_FOR_MALWARE=false      # Enable malware scanning (if available)
```

## Troubleshooting Configuration

### Common Configuration Issues

**Issue**: Container fails to start with "Permission denied"  
**Solution**: Check user permissions and file ownership
```bash
# Fix ownership issues
docker-compose exec crawl4ai-mcp-server chown -R 1000:1000 /app
```

**Issue**: Out of memory errors during processing  
**Solution**: Increase memory limits or reduce concurrent requests
```bash
# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G
```

**Issue**: API keys not being recognized  
**Solution**: Verify environment variable names and values
```bash
# Debug environment variables
docker-compose exec crawl4ai-mcp-server printenv | grep API_KEY
```

**Issue**: Slow performance with large files  
**Solution**: Adjust timeout and concurrency settings
```bash
MAX_FILE_SIZE_MB=50        # Reduce from 100MB
MAX_CONCURRENT_REQUESTS=3  # Reduce from 5
PLAYWRIGHT_TIMEOUT=120     # Increase from 60s
```

### Configuration Debugging
Enable detailed logging and diagnostics for configuration issues.

```bash
# Debug Configuration
FASTMCP_LOG_LEVEL=DEBUG             # Enable debug logging
CONFIG_DEBUG=true                   # Log configuration loading
VALIDATE_CONFIG=true                # Enable startup validation
TRACE_REQUESTS=true                 # Log all requests

# Performance Debugging
PROFILE_REQUESTS=true               # Enable request profiling
LOG_MEMORY_USAGE=true              # Log memory usage
LOG_PERFORMANCE_METRICS=true       # Log performance metrics
```

## Keywords <!-- #keywords -->
environment variables, configuration, Docker, MCP server, FastMCP, performance tuning, security, API keys, transport protocols, container optimization, CPU-only, cache configuration, health checks, troubleshooting, Claude Desktop, GitHub Actions, deployment, validation