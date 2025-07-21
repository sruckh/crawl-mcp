# CONTRIBUTING.md

## Welcome Contributors! 👋

We're excited that you're interested in contributing to the Crawl4AI MCP Server project. This guide provides comprehensive instructions for contributing to our Docker-based MCP server implementation.

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Docker Development Workflow](#docker-development-workflow)
4. [Development Environment](#development-environment)
5. [Code Style Guidelines](#code-style-guidelines)
6. [Testing Guidelines](#testing-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Release Process](#release-process)
9. [Getting Help](#getting-help)

## Code of Conduct

### Our Standards
- **Be respectful and inclusive** to all contributors
- **Welcome newcomers** and help them understand our MCP server architecture
- **Accept constructive criticism** gracefully and provide helpful feedback
- **Focus on what's best** for the MCP community and web crawling ecosystem
- **Show empathy** towards other contributors learning Docker and MCP concepts

### Unacceptable Behavior
- Harassment, discriminatory language, or personal attacks
- Publishing others' private information (API keys, credentials)
- Trolling or deliberately disruptive behavior
- Other conduct deemed inappropriate for a professional development environment

## Getting Started

### Prerequisites

#### Required Tools
```bash
# Core Requirements
- Python 3.11+ (with pip and venv support)
- Docker Desktop or Docker Engine (latest version with BuildKit)
- Git (for version control and CI/CD)
- GNU Make (for automation scripts)

# Development Platform
- Linux/macOS/Windows (with WSL2 for Windows)
- AMD64/X86_64 architecture (ARM64 support experimental)
```

#### Recommended Development Tools
```bash
# Code Editors
- VS Code with Python and Docker extensions
- PyCharm Professional or Community
- Any editor with Python syntax highlighting

# Terminal Tools
- curl or httpie (for API testing)
- jq (for JSON processing)
- Docker Compose v2.x
```

#### Optional Tools for Advanced Development
```bash
# GitHub Integration
- GitHub CLI (gh) for workflow management
- GitHub Desktop (optional GUI)

# Testing Tools
- Playwright browsers (auto-installed in containers)
- Postman or Insomnia (for HTTP transport testing)

# Monitoring Tools
- Docker Desktop Dashboard
- Portainer (for container management)
```

### Environment Setup

#### 1. Fork and Clone Repository
```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/crawl-mcp.git
cd crawl-mcp

# 3. Add upstream remote
git remote add upstream https://github.com/sruckh/crawl-mcp.git

# 4. Verify remotes
git remote -v
```

#### 2. Initial Environment Setup
```bash
# Run automated setup (Linux/macOS)
./setup.sh

# OR run setup manually
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

#### 3. Docker Environment Setup
```bash
# Create shared Docker network
docker network create shared_net

# Copy environment configuration
cp .env.example .env
# Edit .env with your specific settings

# Verify Docker setup
docker --version
docker-compose --version
```

## Docker Development Workflow

### Container Development Strategy
Our project uses a multi-container strategy optimized for different development and deployment scenarios.

#### Development Containers Overview
| Container | Dockerfile | Use Case | Build Time | Image Size |
|-----------|------------|----------|------------|------------|
| **Standard** | `Dockerfile` | Full features + potential CUDA | 8-12 min | ~2-3GB |
| **CPU-Optimized** | `Dockerfile.cpu` | Local development (recommended) | 6-9 min | ~1.5-2GB |
| **Lightweight** | `Dockerfile.lightweight` | Resource-constrained environments | 4-6 min | ~1-1.5GB |
| **RunPod** | `Dockerfile.runpod` | Serverless cloud deployment | 6-9 min | ~1.5-2GB |

### Local Development Workflow

#### 1. Start Development Environment
```bash
# Option A: CPU-optimized (recommended for most development)
docker-compose -f docker-compose.cpu.yml build
docker-compose -f docker-compose.cpu.yml up -d

# Option B: Standard build (if you need full features)
docker-compose build
docker-compose up -d

# Option C: Lightweight (for testing minimal configurations)
docker build -f Dockerfile.lightweight -t crawl4ai-mcp:dev .
docker run -d --name crawl4ai-dev --network shared_net crawl4ai-mcp:dev
```

#### 2. Development Testing
```bash
# Health check
docker-compose exec crawl4ai-mcp-server python -c "
from crawl4ai_mcp.server import mcp
print('✅ MCP server healthy')
"

# Test basic crawling functionality
docker-compose exec crawl4ai-mcp-server python -c "
from crawl4ai import AsyncWebCrawler
print('✅ Crawl4AI engine available')
"

# Test MCP tools
docker-compose exec crawl4ai-mcp-server python -m crawl4ai_mcp.server --help
```

#### 3. Live Development with Volume Mounting
```bash
# Create development override
cat > docker-compose.dev.yml << EOF
version: '3.8'
services:
  crawl4ai-mcp-server:
    volumes:
      - ./crawl4ai_mcp:/app/crawl4ai_mcp:ro
      - ./examples:/app/examples:ro
    environment:
      - FASTMCP_LOG_LEVEL=DEBUG
      - PYTHONPATH=/app
EOF

# Start with development overrides
docker-compose -f docker-compose.cpu.yml -f docker-compose.dev.yml up -d
```

### Branch Development Workflow

#### Branch Naming Conventions
```bash
# Feature development
feature/mcp-tool-enhancement
feature/youtube-transcript-improvement
feature/docker-optimization

# Bug fixes
fix/playwright-timeout-issue
fix/memory-leak-in-cache
fix/container-startup-failure

# Infrastructure changes
infra/github-actions-optimization
infra/runpod-deployment-update
infra/container-security-hardening

# Documentation updates
docs/api-reference-update
docs/docker-setup-guide
docs/troubleshooting-improvements
```

#### Development Branch Workflow
```bash
# 1. Update your fork
git fetch upstream
git checkout main
git merge upstream/main
git push origin main

# 2. Create feature branch
git checkout -b feature/your-amazing-feature

# 3. Set up development environment for your branch
docker-compose -f docker-compose.cpu.yml down  # Stop existing containers
docker-compose -f docker-compose.cpu.yml build --no-cache  # Clean build
docker-compose -f docker-compose.cpu.yml up -d

# 4. Make your changes and test
# Edit files, test in container...

# 5. Rebuild and test after changes
docker-compose -f docker-compose.cpu.yml build
docker-compose -f docker-compose.cpu.yml restart
```

### Container Testing and Validation

#### 1. Build Testing
```bash
# Test all container variants
./scripts/build-cpu-containers.sh

# Manual build testing
docker build -f Dockerfile.cpu -t crawl4ai-test:cpu .
docker build -f Dockerfile.lightweight -t crawl4ai-test:light .
docker build -f Dockerfile.runpod -t crawl4ai-test:runpod .
```

#### 2. Functionality Testing
```bash
# Test MCP server startup
docker run --rm crawl4ai-test:cpu python -c "
from crawl4ai_mcp.server import mcp
print('MCP server can initialize')
"

# Test tool availability
docker run --rm --network shared_net crawl4ai-test:cpu python -c "
import asyncio
from crawl4ai_mcp.server import *
print('All MCP tools available')
"
```

#### 3. Integration Testing
```bash
# Test with Claude Desktop configuration
# Copy appropriate config from configs/ directory
cp configs/claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json

# Test HTTP transport mode
docker run -d --name test-http --network shared_net -e MCP_TRANSPORT=http crawl4ai-test:cpu
curl http://test-http:8000/health

# Cleanup test containers
docker rm -f test-http
```

## Development Environment

### Configuration Management

#### Environment Variables for Development
```bash
# Copy and customize environment file
cp .env.example .env.dev

# Key development variables
FASTMCP_LOG_LEVEL=DEBUG              # Detailed logging
MCP_TRANSPORT=stdio                  # Default for Claude Desktop
MAX_CONCURRENT_REQUESTS=3            # Conservative for development
CACHE_TTL=300                        # Short cache for testing
SAFE_MODE=false                      # Allow broader testing
```

#### Development vs Production Configuration
```bash
# Development configuration (relaxed limits)
MAX_FILE_SIZE_MB=50                  # Smaller for faster testing
PLAYWRIGHT_TIMEOUT=30                # Shorter for quicker feedback
ENABLE_FILE_PROCESSING=true          # Test all features
CRAWL4AI_DISABLE_SENTENCE_TRANSFORMERS=true  # CPU-only for speed

# Production configuration (secure and optimized)
MAX_FILE_SIZE_MB=100                 # Full size support
PLAYWRIGHT_TIMEOUT=60                # More patience for complex sites
SAFE_MODE=true                       # Enhanced security
RATE_LIMIT_ENABLED=true              # Protect against abuse
```

### IDE Setup and Configuration

#### VS Code Configuration
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "docker.defaultPlatform": "linux/amd64",
  "files.associations": {
    "Dockerfile*": "dockerfile",
    "docker-compose*.yml": "docker-compose"
  }
}
```

#### VS Code Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-azuretools.vscode-docker",
    "ms-vscode.makefile-tools",
    "yzhang.markdown-all-in-one",
    "redhat.vscode-yaml"
  ]
}
```

## Code Style Guidelines

### Python Code Style
We follow PEP 8 with specific adaptations for MCP server development.

#### Import Organization
```python
# Standard library imports
import asyncio
import json
import os
from typing import Dict, List, Optional
from pathlib import Path

# Third-party imports
from pydantic import BaseModel, Field
import aiohttp
from fastmcp import FastMCP

# Local application imports
from .config import ConfigManager
from .suppress_output import suppress_stdout_stderr
from .strategies import ExtractionStrategy
```

#### MCP Tool Development Pattern
```python
@mcp.tool(description="Clear, descriptive tool description")
async def your_mcp_tool(
    param1: str = Field(description="Clear parameter description"),
    param2: Optional[int] = Field(default=None, description="Optional parameter"),
) -> str:
    """
    Detailed docstring explaining tool functionality.
    
    Args:
        param1: Detailed parameter explanation
        param2: Optional parameter explanation
        
    Returns:
        JSON string with tool results
        
    Raises:
        Exception: When operation fails
    """
    try:
        # Always use output suppression for crawl4ai operations
        with suppress_stdout_stderr():
            # Your tool implementation here
            result = await some_async_operation(param1, param2)
            
        # Return JSON-encoded results
        return json.dumps({
            "success": True,
            "data": result,
            "metadata": {
                "timestamp": "...",
                "tool": "your_mcp_tool"
            }
        }, ensure_ascii=False)
        
    except Exception as e:
        # Always return JSON-encoded errors
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }, ensure_ascii=False)
```

#### Error Handling Patterns
```python
# MCP-specific error handling
async def robust_mcp_operation():
    """Example of robust error handling for MCP tools."""
    try:
        # Primary operation
        with suppress_stdout_stderr():
            result = await primary_operation()
        return success_response(result)
        
    except TimeoutError as e:
        # Handle timeout specifically
        return error_response(f"Operation timed out: {e}")
        
    except aiohttp.ClientError as e:
        # Handle network errors
        return error_response(f"Network error: {e}")
        
    except Exception as e:
        # Generic fallback
        return error_response(f"Unexpected error: {e}")

def success_response(data):
    """Standardized success response format."""
    return json.dumps({
        "success": True,
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    }, ensure_ascii=False)

def error_response(message):
    """Standardized error response format."""
    return json.dumps({
        "success": False,
        "error": message,
        "timestamp": asyncio.get_event_loop().time()
    }, ensure_ascii=False)
```

### Docker and Configuration Style

#### Dockerfile Best Practices
```dockerfile
# Use specific Python version
FROM python:3.11-slim

# Set working directory early
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements*.txt ./

# Install dependencies in single layer
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-deps crawl4ai>=0.3.0

# Copy application code
COPY . .

# Use non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "from crawl4ai_mcp.server import mcp; print('OK')"
```

#### Environment Variable Naming
```bash
# Use consistent naming patterns
CRAWL4AI_*           # crawl4ai-specific settings
MCP_*                # MCP protocol settings  
FASTMCP_*            # FastMCP framework settings
PLAYWRIGHT_*         # Browser automation settings
MAX_*                # Resource limits
ENABLE_*             # Feature toggles
```

### File Organization and Naming

#### Project Structure Conventions
```
crawl4ai_mcp/
├── __init__.py              # Tool selection guide
├── server.py                # Main MCP server (keep monolithic for now)
├── config.py                # Configuration management
├── strategies.py            # Extraction strategies
├── file_processor.py        # File processing utilities
├── youtube_processor.py     # YouTube-specific processor
├── google_search_processor.py # Google search integration
└── suppress_output.py       # Output suppression utility

docker/                      # Docker-related files
├── Dockerfile               # Standard container
├── Dockerfile.cpu           # CPU-optimized
├── Dockerfile.lightweight   # Minimal container
├── Dockerfile.runpod        # Serverless optimized
├── docker-compose.yml       # Standard deployment
├── docker-compose.cpu.yml   # CPU-optimized deployment
└── .dockerignore            # Build optimization

tests/                       # Test organization
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── containers/              # Container-specific tests
└── mcp/                     # MCP protocol tests
```

#### Naming Conventions
```python
# Files and modules
file_processor.py            # Snake case for modules
youtube_processor.py         # Descriptive, specific names
google_search_processor.py   # Full name clarity

# Classes
class YouTubeProcessor:      # PascalCase for classes
class ConfigManager:         # Clear, descriptive names
class ExtractionStrategy:    # Interface naming

# Functions and methods
async def extract_transcript():      # Snake case, async prefix
def get_supported_formats():        # Verb + noun pattern
async def search_and_crawl():       # Action-oriented names

# Constants
MAX_FILE_SIZE_MB = 100              # UPPER_SNAKE_CASE
DEFAULT_CACHE_TTL = 900             # Clear, specific names
SUPPORTED_VIDEO_PLATFORMS = [...]    # Descriptive constant names
```

## Testing Guidelines

### Testing Strategy
Our testing approach covers multiple layers: unit tests, integration tests, container tests, and MCP protocol tests.

#### Unit Testing
```python
# test_file_processor.py
import pytest
from unittest.mock import AsyncMock, patch
from crawl4ai_mcp.file_processor import FileProcessor

class TestFileProcessor:
    @pytest.fixture
    def file_processor(self):
        return FileProcessor()
    
    @pytest.mark.asyncio
    async def test_process_pdf_file(self, file_processor):
        # Arrange
        test_url = "https://example.com/test.pdf"
        
        # Act
        result = await file_processor.process_file_url(test_url)
        
        # Assert
        assert result["success"] is True
        assert "content" in result["data"]
        assert result["data"]["file_type"] == "pdf"
    
    @pytest.mark.asyncio
    async def test_process_unsupported_file(self, file_processor):
        # Arrange
        test_url = "https://example.com/test.xyz"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported file type"):
            await file_processor.process_file_url(test_url)
```

#### Integration Testing
```python
# test_mcp_integration.py
import pytest
import asyncio
from crawl4ai_mcp.server import mcp

class TestMCPIntegration:
    @pytest.mark.asyncio
    async def test_crawl_url_tool(self):
        # Test the actual MCP tool
        result = await crawl_url("https://httpbin.org/html")
        
        # Parse JSON response
        response = json.loads(result)
        assert response["success"] is True
        assert "content" in response["data"]
    
    @pytest.mark.asyncio
    async def test_file_processing_integration(self):
        # Test file processing end-to-end
        result = await process_file("https://example.com/test.pdf")
        
        response = json.loads(result)
        assert response["success"] is True
        assert response["data"]["file_type"] == "pdf"
```

#### Container Testing
```bash
# tests/test_containers.py
#!/bin/bash

# Test CPU-optimized container
test_cpu_container() {
    echo "Testing CPU-optimized container..."
    
    # Build container
    docker build -f Dockerfile.cpu -t test-cpu .
    
    # Test basic functionality
    docker run --rm test-cpu python -c "
    from crawl4ai_mcp.server import mcp
    print('✅ CPU container: MCP server loads')
    "
    
    # Test crawl4ai availability
    docker run --rm test-cpu python -c "
    from crawl4ai import AsyncWebCrawler
    print('✅ CPU container: Crawl4AI available')
    "
    
    # Cleanup
    docker image rm test-cpu
}

# Test lightweight container
test_lightweight_container() {
    echo "Testing lightweight container..."
    
    docker build -f Dockerfile.lightweight -t test-light .
    
    # Test resource constraints
    docker run --rm --memory=512m test-light python -c "
    import psutil
    memory_mb = psutil.virtual_memory().total / 1024 / 1024
    assert memory_mb <= 600, f'Memory too high: {memory_mb}MB'
    print('✅ Lightweight container: Memory constraints OK')
    "
    
    docker image rm test-light
}

# Run tests
test_cpu_container
test_lightweight_container
echo "✅ All container tests passed"
```

#### MCP Protocol Testing
```python
# test_mcp_protocol.py
import pytest
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class TestMCPProtocol:
    @pytest.mark.asyncio
    async def test_mcp_server_tools(self):
        """Test MCP server exposes expected tools."""
        # Start MCP server in test mode
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "crawl4ai_mcp.server"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize MCP session
                await session.initialize()
                
                # List available tools
                tools = await session.list_tools()
                
                # Verify expected tools are available
                tool_names = [tool.name for tool in tools.tools]
                expected_tools = [
                    "crawl_url",
                    "deep_crawl_site", 
                    "intelligent_extract",
                    "extract_entities",
                    "process_file",
                    "extract_youtube_transcript",
                    "search_google"
                ]
                
                for tool in expected_tools:
                    assert tool in tool_names, f"Missing tool: {tool}"
    
    @pytest.mark.asyncio
    async def test_crawl_url_mcp_call(self):
        """Test actual MCP tool call."""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "crawl4ai_mcp.server"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Call crawl_url tool
                result = await session.call_tool(
                    "crawl_url",
                    {"url": "https://httpbin.org/html"}
                )
                
                # Verify response structure
                assert result.content is not None
                response = json.loads(result.content[0].text)
                assert response["success"] is True
                assert "data" in response
```

### Test Execution

#### Running Tests Locally
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run unit tests
pytest tests/unit/ -v

# Run integration tests (requires containers)
pytest tests/integration/ -v

# Run container tests
pytest tests/containers/ -v

# Run all tests with coverage
pytest --cov=crawl4ai_mcp --cov-report=html

# Run specific test categories
pytest -m "unit" -v          # Only unit tests
pytest -m "integration" -v   # Only integration tests
pytest -m "slow" -v          # Only slow/heavy tests
```

#### Docker Test Environment
```bash
# Test in clean container environment
docker run --rm -v $(pwd):/app -w /app python:3.11-slim bash -c "
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
"

# Test specific container builds
./scripts/test-all-containers.sh

# Test MCP protocol compliance
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Test Quality Standards
- **Coverage**: Aim for 80%+ code coverage
- **Speed**: Unit tests <1s each, integration tests <30s each
- **Isolation**: Each test should be independent and repeatable
- **Documentation**: Test names should clearly describe what they test
- **Realism**: Integration tests should use realistic data and scenarios

## Pull Request Process

### Before Submitting a PR

#### Pre-submission Checklist
- [ ] **Code Quality**
  - [ ] Code follows Python PEP 8 and project style guidelines
  - [ ] All functions have appropriate docstrings
  - [ ] Error handling follows MCP pattern (JSON responses)
  - [ ] No hardcoded credentials or sensitive data

- [ ] **Testing**
  - [ ] Unit tests added for new functionality
  - [ ] Integration tests pass
  - [ ] Container builds successfully
  - [ ] MCP protocol compliance verified

- [ ] **Docker & Infrastructure**
  - [ ] All container variants build successfully
  - [ ] Docker Compose configurations updated if needed
  - [ ] Environment variables documented in CONFIG.md
  - [ ] No breaking changes to existing container interfaces

- [ ] **Documentation**
  - [ ] README.md updated if needed
  - [ ] API documentation updated for new tools
  - [ ] CHANGELOG.md updated with changes
  - [ ] Configuration examples provided

- [ ] **Security**
  - [ ] No API keys or secrets committed
  - [ ] Input validation implemented
  - [ ] Output sanitization in place
  - [ ] Container security best practices followed

#### Local Testing Before PR
```bash
# 1. Run full test suite
pytest tests/ -v --cov=crawl4ai_mcp

# 2. Build and test all container variants
./scripts/build-cpu-containers.sh

# 3. Test MCP protocol compliance
python -m crawl4ai_mcp.server --test-mode

# 4. Lint and format code
black crawl4ai_mcp/
flake8 crawl4ai_mcp/
mypy crawl4ai_mcp/

# 5. Test with Claude Desktop (if available)
# Update claude_desktop_config.json and test tools

# 6. Security scan
bandit -r crawl4ai_mcp/
```

### PR Template

When creating a pull request, use this template:

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that causes existing functionality to change)
- [ ] 📚 Documentation update
- [ ] 🏗️ Infrastructure change (Docker, CI/CD, deployment)
- [ ] 🧪 Test improvements
- [ ] 🔧 Maintenance/refactoring

## MCP Tools Affected
- [ ] `crawl_url` - Web page crawling
- [ ] `deep_crawl_site` - Multi-page crawling  
- [ ] `intelligent_extract` - AI-powered extraction
- [ ] `extract_entities` - Named entity recognition
- [ ] `process_file` - File processing (PDF, Office, etc.)
- [ ] `extract_youtube_transcript` - YouTube transcripts
- [ ] `search_google` - Google search integration
- [ ] New tool: `tool_name` - Description

## Container Impact
- [ ] Standard container (`Dockerfile`)
- [ ] CPU-optimized container (`Dockerfile.cpu`)
- [ ] Lightweight container (`Dockerfile.lightweight`)
- [ ] RunPod serverless container (`Dockerfile.runpod`)
- [ ] Docker Compose configurations
- [ ] No container changes

## Testing Completed
- [ ] Unit tests pass (`pytest tests/unit/`)
- [ ] Integration tests pass (`pytest tests/integration/`)
- [ ] Container builds successful (`./scripts/build-cpu-containers.sh`)
- [ ] MCP protocol compliance verified
- [ ] Manual testing with Claude Desktop completed
- [ ] Performance impact assessed

## Documentation Updates
- [ ] Code docstrings updated
- [ ] API documentation updated
- [ ] README.md updated
- [ ] CONFIG.md updated with new environment variables
- [ ] CHANGELOG.md updated
- [ ] No documentation changes needed

## Security Considerations
- [ ] No sensitive data exposed
- [ ] Input validation implemented
- [ ] Output sanitization in place
- [ ] Container security best practices followed
- [ ] No new security vulnerabilities introduced

## Breaking Changes
If this PR introduces breaking changes, describe:
- What breaks
- Migration path for users
- Version bump required

## Performance Impact
- [ ] Performance improved
- [ ] No performance impact
- [ ] Performance regression (justified because...)

## Related Issues
Fixes #(issue number)
Closes #(issue number)
Relates to #(issue number)

## Additional Context
Add any other context, screenshots, or notes about the PR here.
```

### Review Process

#### What Reviewers Look For
1. **Code Quality**: Clean, readable, well-documented code
2. **MCP Compliance**: Proper tool signatures and JSON responses
3. **Container Compatibility**: Works across all container variants
4. **Security**: No vulnerabilities or data leaks
5. **Performance**: No unexpected resource usage
6. **Documentation**: Clear documentation for new features

#### Addressing Review Feedback
```bash
# Make requested changes
git add .
git commit -m "Address review feedback: improve error handling"

# Update PR branch
git push origin feature/your-feature

# If major changes requested, squash commits
git rebase -i HEAD~n  # where n is number of commits
git push --force-with-lease origin feature/your-feature
```

### Post-Merge Process
```bash
# After merge, clean up
git checkout main
git pull upstream main
git branch -d feature/your-feature
git remote prune origin

# Update CHANGELOG if not done in PR
# Tag release if this was a major feature
```

## Release Process

### Versioning Strategy
We use [Semantic Versioning](https://semver.org/) with Docker-specific considerations:

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes to MCP API, container interfaces, or deployment requirements
- **MINOR** (1.0.0 → 1.1.0): New MCP tools, container optimizations, new features
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, security patches, documentation updates

### Release Workflow

#### 1. Pre-Release Preparation
```bash
# Update version in key files
VERSION="1.2.0"

# Update version references
echo $VERSION > VERSION
sed -i "s/version = .*/version = \"$VERSION\"/" pyproject.toml

# Update CHANGELOG.md with release notes
# Update CLAUDE.md with version reference

# Build and test all containers
./scripts/build-cpu-containers.sh
```

#### 2. Container Release Process
```bash
# Tag containers for release
docker build -f Dockerfile.cpu -t crawl4ai-mcp:$VERSION .
docker build -f Dockerfile.lightweight -t crawl4ai-mcp:$VERSION-light .
docker build -f Dockerfile.runpod -t crawl4ai-mcp:$VERSION-runpod .

# Test release containers
docker run --rm crawl4ai-mcp:$VERSION python -c "
from crawl4ai_mcp.server import mcp
print(f'Release {VERSION} container test passed')
"
```

#### 3. GitHub Actions Release
Our automated release process triggers on tag creation:

```bash
# Create and push release tag
git tag v$VERSION
git push upstream v$VERSION

# This triggers .github/workflows/build-runpod-docker.yml which:
# 1. Builds all container variants
# 2. Pushes to Docker Hub with version tags
# 3. Creates GitHub release with artifacts
```

#### 4. Release Notes Template
```markdown
# Release v1.2.0

## 🚀 New Features
- New MCP tool: `extract_structured_data` for JSON schema extraction
- CPU-optimized container now 30% smaller
- Added support for batch file processing

## 🐛 Bug Fixes
- Fixed memory leak in YouTube transcript processor
- Resolved container startup issues on ARM64 systems
- Fixed timeout handling in deep crawl operations

## 🔧 Infrastructure
- Updated to Python 3.11.7 base image
- Improved GitHub Actions build performance
- Enhanced container security with non-root user

## 📚 Documentation
- Added comprehensive Docker deployment guide
- Updated API documentation with new examples
- Improved troubleshooting section

## 🔄 Breaking Changes
None in this release.

## 📦 Container Images
- `docker.io/gemneye/crawl4ai-runpod-serverless:v1.2.0`
- `docker.io/gemneye/crawl4ai-runpod-serverless:1.2`
- `docker.io/gemneye/crawl4ai-runpod-serverless:1`
- `docker.io/gemneye/crawl4ai-runpod-serverless:latest`

## 🔧 Migration Guide
No migration steps required for this release.

## 📊 Performance Improvements
- 25% faster container builds
- 15% reduction in memory usage
- Improved cache hit rates
```

### Docker Hub Release Management

#### Automated Builds
Our GitHub Actions workflow automatically builds and pushes to Docker Hub:
- **Repository**: `docker.io/gemneye/crawl4ai-runpod-serverless`
- **Tags**: `latest`, `v1.2.0`, `1.2`, `1`
- **Platform**: `linux/amd64` (AMD64/X86_64 only)

#### Manual Release (if needed)
```bash
# Login to Docker Hub
docker login

# Build and push specific version
docker build -f Dockerfile.runpod -t gemneye/crawl4ai-runpod-serverless:v1.2.0 .
docker push gemneye/crawl4ai-runpod-serverless:v1.2.0

# Tag and push additional tags
docker tag gemneye/crawl4ai-runpod-serverless:v1.2.0 gemneye/crawl4ai-runpod-serverless:latest
docker push gemneye/crawl4ai-runpod-serverless:latest
```

## Getting Help

### Resources and Support

#### Primary Documentation
- **[Project README](./README.md)**: Overview and quick start
- **[Architecture Guide](./ARCHITECTURE.md)**: Technical architecture and design decisions
- **[Configuration Guide](./CONFIG.md)**: Environment variables and settings
- **[Build Guide](./BUILD.md)**: Build processes and deployment strategies
- **[Docker Guide](./DOCKER.md)**: Docker-specific deployment instructions

#### Community and Support
- **[GitHub Issues](https://github.com/sruckh/crawl-mcp/issues)**: Bug reports and feature requests
- **[GitHub Discussions](https://github.com/sruckh/crawl-mcp/discussions)**: Questions and community discussions
- **[MCP Community](https://github.com/modelcontextprotocol)**: Model Context Protocol community resources

#### Getting Help Effectively

#### For Bug Reports
```markdown
**Bug Report Template**

## Environment
- Container variant: [Standard/CPU/Lightweight/RunPod]
- Docker version: [output of `docker --version`]
- OS: [Linux/macOS/Windows with WSL2]
- Python version: [if running locally]

## Expected Behavior
Clear description of what should happen.

## Actual Behavior
Clear description of what actually happens.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Error Messages
```
Paste error messages here
```

## Additional Context
Any other context, screenshots, or files that might help.
```

#### For Feature Requests
```markdown
**Feature Request Template**

## Problem Statement
Describe the problem this feature would solve.

## Proposed Solution
Describe your proposed solution or approach.

## Alternatives Considered
What other approaches did you consider?

## Additional Context
Any other context, mockups, or examples.

## MCP Integration
How should this integrate with existing MCP tools?

## Container Impact
Which containers would be affected by this change?
```

#### For Questions
- **Search first**: Check existing issues and discussions
- **Be specific**: Include relevant context about your setup
- **Provide examples**: Show what you're trying to accomplish
- **Tag appropriately**: Use labels like `question`, `docker`, `mcp-tool`

### Beginner-Friendly Issues
We welcome first-time contributors! Look for issues labeled:
- **`good first issue`**: Perfect for newcomers
- **`help wanted`**: Community help needed
- **`documentation`**: Improve our docs
- **`container-optimization`**: Docker/containerization improvements
- **`mcp-tool`**: New MCP tool development

#### First Contribution Workflow
```bash
# 1. Find a good first issue
# Browse: https://github.com/sruckh/crawl-mcp/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22

# 2. Comment on the issue to express interest
# 3. Fork and clone the repository
# 4. Set up development environment (see above)
# 5. Create feature branch and implement changes
# 6. Test thoroughly (unit + container tests)
# 7. Submit pull request using our template
# 8. Respond to review feedback
```

### Recognition and Community

#### Contributor Recognition
All contributors are recognized in:
- **README.md contributors section**: Public recognition
- **GitHub contributors graph**: Automatic tracking
- **Release notes**: Major contributors highlighted
- **Hall of Fame**: Outstanding contributors featured

#### Community Values
- **Inclusive environment**: Everyone welcome regardless of experience level
- **Learning-focused**: Help others learn Docker, MCP, and web crawling
- **Quality-oriented**: Maintain high standards while being supportive
- **Innovation-driven**: Encourage creative solutions and improvements

## Keywords <!-- #keywords -->
contributing, development workflow, Docker containers, MCP server, Python development, testing guidelines, pull requests, code review, release process, community guidelines, containerization, FastMCP, crawl4ai, GitHub Actions, CI/CD, debugging, troubleshooting