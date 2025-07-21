# Engineering Journal

## 2025-07-21 07:38

### HTTP Transport Default & crawl4ai 0.7.1 Update
- **What**: Updated CPU container configuration to use HTTP transport by default and upgraded to crawl4ai 0.7.1
- **Why**: HTTP transport provides persistent operation for local development, and 0.7.1 includes latest features and bug fixes
- **How**: Modified Dockerfile.cpu and docker-compose.cpu.yml to enable HTTP mode and specify exact version
- **Issues**: None - clean implementation
- **Result**: CPU containers now stay running on port 8000 with latest crawl4ai features

#### Technical Changes:
- **crawl4ai Version**: Updated from `>=0.3.0` to `==0.7.1` in Dockerfile.cpu
- **Transport Mode**: Changed from STDIO (exiting immediately) to HTTP (persistent)
- **Configuration**: Added MCP_TRANSPORT=http, MCP_HOST=0.0.0.0, MCP_PORT=8000 environment variables
- **Port Exposure**: Container now exposes port 8000 for HTTP access

#### Benefits:
- **Persistent Operation**: Container stays running instead of exiting immediately
- **Local Development**: Easy HTTP access at http://localhost:8000
- **Latest Features**: Access to crawl4ai 0.7.1 improvements and bug fixes
- **Better UX**: More intuitive for users expecting persistent server behavior

---

## 2025-07-20 21:30

### CPU-Only Container Optimization Implementation
- **What**: Created lightweight, CPU-optimized Docker containers excluding CUDA dependencies
- **Why**: Eliminate unnecessary CUDA/GPU packages for 50-70% smaller container images for local deployment
- **How**: Analyzed crawl4ai dependencies, created custom requirements files, and multiple optimized Dockerfiles
- **Issues**: sentence-transformers dependency was pulling in PyTorch with CUDA - resolved with --no-deps installation
- **Result**: Three container variants with significant size reduction and faster builds

#### Key Optimizations:
- **Dependency Analysis**: Identified sentence-transformers as CUDA source in crawl4ai's pyproject.toml
- **Custom Requirements**: `requirements-cpu.txt` with manually curated CPU-only dependencies
- **Multi-Stage Strategy**: Three optimization levels for different use cases
- **Environment Controls**: Runtime flags to disable ML features (`CRAWL4AI_DISABLE_SENTENCE_TRANSFORMERS=true`)

#### Container Variants Created:
1. **CPU-Optimized** (`Dockerfile.cpu` + `docker-compose.cpu.yml`): 1.5-2GB, 1GB memory limit
2. **Ultra-Lightweight** (`Dockerfile.lightweight`): 1-1.5GB, <1GB memory, explicit CUDA blocking
3. **Build Comparison Tool** (`scripts/build-cpu-containers.sh`): Automated size comparison testing

#### Technical Approach:
- **Staged Installation**: Install crawl4ai with `--no-deps` to avoid automatic ML dependencies
- **CPU-Only PyTorch**: Force CPU wheel installation (`--index-url https://download.pytorch.org/whl/cpu`)
- **Environment Isolation**: Block CUDA visibility with `CUDA_VISIBLE_DEVICES=""`
- **Resource Optimization**: Reduced memory limits and CPU allocations for lightweight deployment

#### Documentation Updates:
- **DOCKER.md**: Added container comparison table and usage recommendations
- **Build Instructions**: Clear guidance for local vs production deployment
- **Performance Matrix**: Expected size reductions and use case recommendations

---

## 2025-07-20 21:15

### Docker & RunPod Serverless Deployment Implementation
- **What**: Comprehensive containerization and serverless deployment pipeline
- **Why**: Enable scalable, cost-effective deployment on RunPod cloud platform
- **How**: Created Docker containers, GitHub Actions CI/CD, and RunPod-specific configuration
- **Issues**: Initial CUDA dependencies confusion - clarified project is CPU-only
- **Result**: Complete deployment pipeline with automated builds to `gemneye/crawl4ai-runpod-serverless`

#### Files Created/Modified:
- **Docker Configuration**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`
- **RunPod Deployment**: `Dockerfile.runpod`, `runpod_handler.py`, `runpod_test_input.json`
- **GitHub Actions**: `.github/workflows/build-runpod-docker.yml`, `.github/workflows/validate-config.yml`
- **Documentation**: `DOCKER.md`, `RUNPOD_DEPLOYMENT.md`, `GITHUB_ACTIONS.md`
- **Environment Config**: `.env.example` updated for Docker usage

#### Key Technical Decisions:
- **CPU-Only Architecture**: Confirmed no GPU dependencies despite CUDA packages in build
- **AMD64/X86_64 Restriction**: Platform locked for RunPod compatibility
- **Multi-Transport Support**: STDIO (default) and HTTP modes for different use cases
- **Automated CI/CD**: GitHub Actions builds on push/PR/release with Docker Hub integration
- **Security**: Non-root user, resource limits, health checks, network isolation

#### Deployment Options:
1. **Shared Network**: Local Docker with `shared_net` network (no localhost exposure)
2. **RunPod Serverless**: Auto-scaling cloud deployment with CPU-only workers
3. **GitHub Actions**: Automated builds to `docker.io/gemneye/crawl4ai-runpod-serverless:latest`

#### Performance Features:
- **Multi-stage build**: Optimized image size and build time
- **BuildKit cache**: GitHub Actions caching for faster builds
- **Health monitoring**: Container health checks and status validation
- **Resource controls**: Memory and CPU limits for stable operation

---

## 2025-07-21 05:42

### GitHub Actions YAML Syntax Fix
- **What**: Fixed invalid YAML syntax in build-runpod-docker.yml workflow file
- **Why**: GitHub Actions was failing with "Invalid workflow file" error on line 109
- **How**: Replaced multi-line Python script with single-line command using semicolons
- **Issues**: Multi-line string formatting was breaking YAML validation
- **Result**: Workflow now passes YAML validation and can run successfully

#### Technical Details:
- **Problem**: Multi-line Python script in docker run command had improper indentation
- **Solution**: Converted to single-line Python command with semicolon separators
- **Location**: `.github/workflows/build-runpod-docker.yml:109-114`
- **Impact**: Enables automated CI/CD builds to complete successfully

---

## 2025-07-20 20:37

### Documentation Framework Implementation
- **What**: Implemented Claude Conductor modular documentation system
- **Why**: Improve AI navigation and code maintainability
- **How**: Used `npx claude-conductor` to initialize framework
- **Issues**: None - clean implementation
- **Result**: Documentation framework successfully initialized

---
