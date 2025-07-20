# GitHub Actions CI/CD for RunPod Deployment

Automated Docker image building and deployment pipeline for the Crawl4AI MCP Server on RunPod.

## 🚀 Overview

The GitHub Actions workflow automatically builds and pushes the RunPod serverless container image to Docker Hub whenever changes are made to the codebase.

## 📋 Workflow Features

### Automated Triggers
- **Push to main/feature branches**: Builds on code changes
- **Pull requests**: Validates builds for PRs
- **Releases**: Creates tagged versions
- **Manual dispatch**: Allows custom builds with tags

### Platform Restriction
- **AMD64/X86_64 only**: Optimized for RunPod's infrastructure
- **No ARM64 support**: Ensures compatibility with RunPod workers

### Docker Hub Integration
- **Repository**: `gemneye/crawl4ai-runpod-serverless`
- **Authentication**: Uses `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets
- **Multi-tag strategy**: Automatic versioning and latest tags

## 🔧 Setup Requirements

### 1. Docker Hub Secrets
Configure these secrets in your GitHub repository:

```
Settings → Secrets and variables → Actions → New repository secret
```

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKER_USERNAME` | Docker Hub username | `gemneye` |
| `DOCKER_PASSWORD` | Docker Hub access token | `dckr_pat_...` |

### 2. Docker Hub Repository
Ensure the repository `gemneye/crawl4ai-runpod-serverless` exists on Docker Hub with appropriate permissions.

## 📊 Workflow Details

### Build Matrix
```yaml
strategy:
  matrix:
    platform: [linux/amd64]  # AMD64/X86_64 only
```

### Image Tags
The workflow creates multiple tags automatically:

| Trigger | Tag Examples |
|---------|--------------|
| Main branch push | `latest`, `main-abc1234` |
| Feature branch | `feature-development`, `feature-development-abc1234` |
| Pull request | `pr-123` |
| Release v1.2.3 | `v1.2.3`, `1.2`, `1`, `latest` |
| Manual dispatch | Custom tag specified |

### Build Optimization
- **BuildKit cache**: Speeds up subsequent builds
- **Multi-stage caching**: Efficient layer reuse
- **Inline cache**: GitHub Actions cache integration

## 🎯 Usage Examples

### Automatic Build (Push to Main)
```bash
git add .
git commit -m "Update RunPod handler functionality"
git push origin main
# → Triggers build and pushes gemneye/crawl4ai-runpod-serverless:latest
```

### Manual Build with Custom Tag
```bash
# Go to GitHub Actions tab → "Build and Push RunPod Serverless Container"
# Click "Run workflow"
# Enter custom tag: "v1.0.0-beta"
# → Builds gemneye/crawl4ai-runpod-serverless:v1.0.0-beta
```

### Release Build
```bash
git tag v1.2.3
git push origin v1.2.3
# → Creates GitHub release
# → Triggers build with version tags: v1.2.3, 1.2, 1, latest
```

## 📈 Monitoring and Status

### Build Status Badge
Add to your README.md:
```markdown
[![Build RunPod Container](https://github.com/sruckh/crawl-mcp/actions/workflows/build-runpod-docker.yml/badge.svg)](https://github.com/sruckh/crawl-mcp/actions/workflows/build-runpod-docker.yml)
```

### Workflow Outputs
Each successful build provides:
- ✅ Container health check results
- 📝 Deployment instructions
- 🔗 Direct Docker Hub image URLs
- 📊 Build summary and metadata

## 🔒 Security Features

### Secrets Management
- No secrets exposed in logs
- Docker Hub authentication via secure tokens
- Limited permission scopes

### Image Security
- Non-root user execution
- Minimal base image (python:3.11-slim)
- Security-focused Dockerfile practices

### Build Isolation
- Fresh environment for each build
- No persistent state between runs
- Secure credential handling

## 🚀 RunPod Deployment Integration

After successful builds, use the generated image in RunPod:

### Console Configuration
```
Image URL: docker.io/gemneye/crawl4ai-runpod-serverless:latest
Worker Type: CPU-only
Platform: AMD64/X86_64
Auto-scaling: Enabled
```

### API Deployment
```bash
curl -X POST https://api.runpod.ai/graphql \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { 
      createEndpoint(
        input: {
          name: \"crawl4ai-mcp-server\"
          dockerImage: \"docker.io/gemneye/crawl4ai-runpod-serverless:latest\"
          gpuCount: 0
          cpuCount: 4
          memoryInGb: 8
        }
      ) { 
        id 
        name 
      } 
    }"
  }'
```

## 🔧 Troubleshooting

### Common Issues

**Build Failures:**
```bash
# Check workflow logs in GitHub Actions tab
# Common issues:
# 1. Docker Hub authentication failed
# 2. Platform compatibility issues
# 3. Dockerfile syntax errors
```

**Authentication Problems:**
```bash
# Verify secrets are set correctly:
# Settings → Secrets → DOCKER_USERNAME and DOCKER_PASSWORD
# Ensure Docker Hub token has push permissions
```

**Platform Issues:**
```bash
# Workflow is restricted to AMD64/X86_64
# ARM64 builds are intentionally disabled
# This ensures RunPod compatibility
```

### Testing Locally
```bash
# Test the workflow locally using act
npm install -g @github/act
act -j build-and-push -s DOCKER_USERNAME=your-username -s DOCKER_PASSWORD=your-token
```

## 📚 Related Documentation

- [RunPod Deployment Guide](RUNPOD_DEPLOYMENT.md)
- [Docker Configuration](DOCKER.md)
- [Project Architecture](ARCHITECTURE.md)

This automated pipeline ensures consistent, tested deployments of the Crawl4AI MCP Server for RunPod serverless infrastructure.