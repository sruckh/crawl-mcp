# ARCHITECTURE.md

## Tech Stack

### Core Technologies
- **Language**: Python 3.11+ with asyncio for concurrency
- **Framework**: FastMCP (Model Context Protocol server framework)
- **Crawling Engine**: crawl4ai v0.3.0+ with Playwright browser automation
- **File Processing**: Microsoft MarkItDown for document conversion
- **Search Integration**: Google Search API with 31 genre filters
- **Video Processing**: youtube-transcript-api v1.1.0+ for transcript extraction

### Infrastructure & Deployment
- **Containerization**: Docker with multi-stage builds (4 container variants)
- **CI/CD**: GitHub Actions with automated builds to Docker Hub
- **Serverless**: RunPod cloud deployment with CPU-only workers
- **Networking**: Docker shared_net isolation, no localhost exposure
- **Caching**: 15-minute self-cleaning cache system

### Transport Protocols
- **STDIO**: Default MCP transport for Claude Desktop integration
- **HTTP**: Pure StreamableHTTP and Legacy SSE implementations
- **WebSocket**: Support via FastMCP framework

## Directory Structure

```
crawl4ai_mcp/
├── crawl4ai_mcp/           # Core MCP server package
│   ├── __init__.py         # Tool selection guide (lines 11-155)
│   ├── server.py           # Main MCP server (3,392 lines)
│   ├── config.py           # Configuration management (lines 1-397)
│   ├── strategies.py       # Extraction strategies (lines 1-273)
│   ├── file_processor.py   # Microsoft MarkItDown integration (lines 1-319)
│   ├── youtube_processor.py # YouTube transcript extraction (lines 1-607)
│   ├── google_search_processor.py # Google search with genres (lines 1-563)
│   └── suppress_output.py  # MCP protocol protection (lines 1-49)
├── examples/               # Transport protocol examples
│   ├── pure_streamable_http_server.py # Pure HTTP transport (lines 1-400)
│   ├── simple_pure_http_server.py     # Simple HTTP server
│   └── run_http_server.py             # HTTP server runner
├── scripts/                # Build and deployment automation
│   ├── setup.sh            # Linux/macOS environment setup
│   ├── setup_windows.bat   # Windows environment setup
│   ├── start_pure_http_server.sh # HTTP server startup
│   └── build-cpu-containers.sh   # Container comparison tool
├── configs/                # Claude Desktop integration configs
│   ├── claude_desktop_config.json          # Basic STDIO config
│   ├── claude_desktop_config_pure_http.json # HTTP transport config
│   └── claude_desktop_config_windows.json   # Windows-specific config
├── docs/                   # Documentation
│   ├── HTTP_API_GUIDE.md   # HTTP API documentation
│   ├── PURE_STREAMABLE_HTTP.md # Pure HTTP protocol guide
│   └── troubleshooting_ja.md    # Japanese troubleshooting
├── .github/workflows/      # GitHub Actions CI/CD
│   ├── build-runpod-docker.yml # Automated Docker builds
│   ├── validate-config.yml     # Configuration validation
│   └── .yamllint.yml           # YAML linting rules
├── Docker Infrastructure   # Container deployment
│   ├── Dockerfile          # Standard container (with potential CUDA)
│   ├── Dockerfile.cpu      # CPU-optimized (recommended for VPS)
│   ├── Dockerfile.lightweight # Ultra-minimal container
│   ├── Dockerfile.runpod   # RunPod serverless optimized
│   ├── docker-compose.yml  # Standard deployment
│   ├── docker-compose.cpu.yml # CPU-optimized deployment
│   └── .dockerignore       # Build optimization
└── Serverless Integration  # Cloud deployment
    ├── runpod_handler.py   # RunPod serverless worker (lines 1-200)
    ├── runpod_test_input.json # Test configuration
    └── requirements-cpu.txt   # CPU-only dependencies
```

## Key Architectural Decisions

### Decision 1: FastMCP Framework Adoption
**Context**: Need for standardized MCP protocol implementation with tool registration  
**Decision**: Use FastMCP framework for server implementation  
**Rationale**: Provides type-safe tool registration, automatic protocol handling, multiple transport support  
**Consequences**: Simplified development, consistent protocol compliance, extensible architecture

### Decision 2: Output Suppression System
**Context**: crawl4ai produces verbose output that corrupts MCP JSON responses  
**Decision**: Implement output suppression in `suppress_output.py`  
**Rationale**: Maintain MCP protocol integrity while preserving crawl4ai functionality  
**Consequences**: Clean MCP responses, requires careful management of suppression context

### Decision 3: Multi-Container Strategy
**Context**: Different deployment environments require different optimizations  
**Decision**: Four container variants (Standard, CPU-optimized, Lightweight, RunPod)  
**Rationale**: Optimize for specific use cases without compromising flexibility  
**Consequences**: Increased build complexity, better resource utilization, deployment flexibility

### Decision 4: CPU-Only Optimization
**Context**: Project doesn't require GPU but dependencies pull in CUDA libraries  
**Decision**: Create CPU-only builds with manual dependency curation  
**Rationale**: Reduce container size by 50-70% for VPS deployments  
**Consequences**: Custom requirements management, environment variable controls

### Decision 5: Serverless-First Design
**Context**: Need for scalable, cost-effective deployment options  
**Decision**: Design for serverless deployment on RunPod platform  
**Rationale**: Pay-per-use model, auto-scaling, reduced operational overhead  
**Consequences**: Stateless design requirements, cold start optimization

## Component Architecture

### MCP Server Core (crawl4ai_mcp/server.py) <!-- #mcp-server-core -->
```python
# Major classes with exact line numbers
class FastMCP { /* lines 229-250 */ }           # <!-- #fastmcp-instance -->
class CrawlRequest { /* lines 43-84 */ }        # <!-- #crawl-request-model -->
class StructuredExtractionRequest { /* lines 86-95 */ } # <!-- #extraction-model -->
class FileProcessRequest { /* lines 97-103 */ } # <!-- #file-process-model -->

# Tool implementations
@mcp.tool() crawl_url { /* lines 250-400 */ }              # <!-- #crawl-url-tool -->
@mcp.tool() deep_crawl_site { /* lines 500-650 */ }        # <!-- #deep-crawl-tool -->
@mcp.tool() intelligent_extract { /* lines 800-950 */ }    # <!-- #intelligent-extract -->
@mcp.tool() extract_entities { /* lines 1100-1250 */ }     # <!-- #entity-extraction -->
@mcp.tool() process_file { /* lines 1500-1650 */ }         # <!-- #file-processing -->
@mcp.tool() extract_youtube_transcript { /* lines 1800-1950 */ } # <!-- #youtube-tool -->
@mcp.tool() search_google { /* lines 2100-2250 */ }        # <!-- #google-search -->

# Server startup and configuration
def main() { /* lines 3349-3393 */ }           # <!-- #server-main -->
```

### File Processing System (file_processor.py) <!-- #file-processor -->
```python
# Microsoft MarkItDown integration
class FileProcessor { /* lines 1-50 */ }       # <!-- #file-processor-class -->
async def process_file_url { /* lines 51-150 */ } # <!-- #file-url-handler -->
async def process_zip_file { /* lines 151-250 */ } # <!-- #zip-processor -->
def get_supported_formats { /* lines 251-319 */ } # <!-- #format-detector -->
```

### YouTube Processing (youtube_processor.py) <!-- #youtube-processor -->
```python
# YouTube transcript extraction
class YouTubeProcessor { /* lines 1-100 */ }   # <!-- #youtube-class -->
async def extract_transcript { /* lines 101-300 */ } # <!-- #transcript-extractor -->
async def batch_extract { /* lines 301-450 */ } # <!-- #batch-processor -->
def get_video_info { /* lines 451-607 */ }     # <!-- #video-info -->
```

### Google Search Integration (google_search_processor.py) <!-- #google-search -->
```python
# Google search with genre filtering
class GoogleSearchProcessor { /* lines 1-100 */ } # <!-- #search-class -->
async def search_google { /* lines 101-250 */ }   # <!-- #search-function -->
async def search_and_crawl { /* lines 251-400 */ } # <!-- #search-crawl -->
def get_search_genres { /* lines 401-563 */ }     # <!-- #genre-definitions -->
```

### Containerization Architecture <!-- #container-architecture -->
```dockerfile
# Multi-stage build pattern
FROM python:3.11-slim as builder { /* Dockerfile lines 1-15 */ }    # <!-- #builder-stage -->
FROM python:3.11-slim as production { /* Dockerfile lines 16-50 */ } # <!-- #production-stage -->

# CPU optimization pattern  
ENV CRAWL4AI_DISABLE_SENTENCE_TRANSFORMERS=true { /* Dockerfile.cpu line 25 */ } # <!-- #cpu-optimization -->
RUN pip install --no-deps crawl4ai { /* Dockerfile.cpu line 30 */ } # <!-- #dependency-control -->
```

### Serverless Handler (runpod_handler.py) <!-- #serverless-handler -->
```python
# RunPod serverless integration
async def handle_crawl_request { /* lines 15-50 */ } # <!-- #request-handler -->
def handler(event) { /* lines 52-100 */ }           # <!-- #runpod-handler -->
EXAMPLE_INPUTS { /* lines 102-200 */ }              # <!-- #example-patterns -->
```

## System Flow Diagram

### MCP Protocol Flow
```
[Claude/Client] --> [FastMCP Server] --> [Tool Registry] --> [Tool Implementation]
                         |                     |                      |
                         v                     v                      v
                   [Transport Layer]    [Request Validation]   [crawl4ai Engine]
                    (STDIO/HTTP)        (Pydantic Models)     (Playwright Browser)
                         |                     |                      |
                         v                     v                      v
                   [Output Suppression] [Error Handling]    [Content Processing]
                         |                     |                      |
                         v                     v                      v
                   [JSON Response]      [Structured Data]    [Cache Management]
```

### Docker Deployment Flow
```
[GitHub Push] --> [GitHub Actions] --> [Docker Build] --> [Docker Hub Registry]
                        |                     |                     |
                        v                     v                     v
                 [Multi-Platform Build]  [4 Container Variants]  [gemneye/crawl4ai-*]
                 (AMD64/X86_64 only)    (Standard/CPU/Light/Pod) (Automated Tags)
                        |                     |                     |
                        v                     v                     v
                 [Build Validation]    [Health Checks]        [Deployment Ready]
```

### Serverless Execution Flow
```
[HTTP Request] --> [RunPod Worker] --> [Container Instance] --> [Handler Function]
                        |                     |                      |
                        v                     v                      v
                 [Auto-scaling]       [Resource Limits]      [MCP Tool Execution]
                 (CPU-only workers)   (1GB memory limit)     (Async Processing)
                        |                     |                      |
                        v                     v                      v
                 [Response Caching]    [Error Recovery]       [JSON Response]
```

## Common Patterns

### Tool Registration Pattern
**When to use**: Adding new MCP tools to the server  
**Implementation**:
```python
@mcp.tool(description="Tool description")
async def tool_name(param: Type = Field(description="Parameter description")) -> str:
    """Tool implementation with proper error handling"""
    try:
        with suppress_stdout_stderr():
            result = await some_operation(param)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
```

### Output Suppression Pattern
**When to use**: Any operation that uses crawl4ai or verbose libraries  
**Implementation**:
```python
from .suppress_output import suppress_stdout_stderr

async def some_function():
    with suppress_stdout_stderr():
        # All crawl4ai operations must be within this context
        result = await crawler.arun(url)
    return result  # Return after suppression context
```

### Container Optimization Pattern
**When to use**: Creating deployment-specific containers  
**Implementation**:
```dockerfile
# Stage 1: Dependency optimization
FROM python:3.11-slim as builder
COPY requirements-cpu.txt .
RUN pip install --no-cache-dir -r requirements-cpu.txt
RUN pip install --no-deps crawl4ai>=0.3.0

# Stage 2: Runtime optimization  
FROM python:3.11-slim
ENV CRAWL4AI_DISABLE_SENTENCE_TRANSFORMERS=true
ENV CUDA_VISIBLE_DEVICES=""
COPY --from=builder /opt/venv /opt/venv
```

### Serverless Handler Pattern
**When to use**: Adapting MCP tools for serverless deployment  
**Implementation**:
```python
def handler(event):
    input_data = event.get('input', {})
    operation = input_data.get('operation')
    params = input_data.get('params', {})
    
    result = asyncio.run(handle_crawl_request(operation, params))
    return result
```

### Error Recovery Pattern
**When to use**: Handling failures in distributed systems  
**Implementation**:
```python
async def resilient_operation(params):
    for attempt in range(3):
        try:
            return await primary_operation(params)
        except Exception as e:
            if attempt == 2:  # Last attempt
                return await fallback_operation(params, error=str(e))
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Performance Characteristics

### Container Comparison
| Variant | Size | Memory | CPU | Use Case |
|---------|------|--------|-----|----------|
| Standard | ~2-3GB | 2GB limit | 1.0 CPU | Full features |
| CPU-Optimized | ~1.5-2GB | 1GB limit | 0.5 CPU | VPS deployment |
| Lightweight | ~1-1.5GB | 512MB | 0.25 CPU | Resource constrained |
| RunPod | ~1.5-2GB | 1GB limit | Auto-scale | Serverless cloud |

### Scaling Characteristics
- **Cold Start**: 30-60 seconds (containers), 15-30 seconds (lightweight)
- **Warm Response**: 2-10 seconds per crawl operation
- **Concurrent Limits**: 3-5 operations (CPU-optimized), 5-10 (standard)
- **Memory Growth**: Linear with content size, managed by 15-minute cache

## Keywords <!-- #keywords -->
MCP, Model Context Protocol, FastMCP, crawl4ai, Playwright, Docker, serverless, RunPod, GitHub Actions, CPU optimization, container, web crawling, YouTube transcripts, file processing, Google search, MarkItDown, asyncio, Python, browser automation, CI/CD, infrastructure