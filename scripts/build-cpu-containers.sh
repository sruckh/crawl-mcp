#!/bin/bash
# Build script for CPU-only container variants

set -e

echo "🚀 Building CPU-optimized Crawl4AI MCP Server containers..."

# Function to get image size
get_image_size() {
    docker images "$1" --format "table {{.Size}}" | tail -n 1
}

# Build original container (with CUDA)
echo ""
echo "📦 Building original container (may include CUDA)..."
docker build -f Dockerfile -t crawl4ai-mcp:original .
ORIGINAL_SIZE=$(get_image_size "crawl4ai-mcp:original")

# Build CPU-only optimized container
echo ""
echo "⚡ Building CPU-optimized container..."
docker build -f Dockerfile.cpu -t crawl4ai-mcp:cpu .
CPU_SIZE=$(get_image_size "crawl4ai-mcp:cpu")

# Build ultra-lightweight container
echo ""
echo "🪶 Building ultra-lightweight container..."
docker build -f Dockerfile.lightweight -t crawl4ai-mcp:lightweight .
LIGHTWEIGHT_SIZE=$(get_image_size "crawl4ai-mcp:lightweight")

# Display results
echo ""
echo "📊 Build Results:"
echo "===================="
echo "Original (with potential CUDA):  $ORIGINAL_SIZE"
echo "CPU-optimized:                   $CPU_SIZE"
echo "Ultra-lightweight:               $LIGHTWEIGHT_SIZE"
echo ""

# Test basic functionality
echo "🧪 Testing container functionality..."

echo "Testing CPU-optimized container..."
docker run --rm --name test-cpu crawl4ai-mcp:cpu \
    python -c "
from crawl4ai_mcp.server import mcp
print('✅ CPU-optimized container: Basic imports successful')
print('✅ MCP server can be initialized')
"

echo "Testing lightweight container..."
docker run --rm --name test-lightweight crawl4ai-mcp:lightweight \
    python -c "
from crawl4ai_mcp.server import mcp
print('✅ Lightweight container: Basic imports successful')
print('✅ MCP server can be initialized')
"

echo ""
echo "✅ All containers built and tested successfully!"
echo ""
echo "💡 Usage recommendations:"
echo "  - For local development: docker-compose -f docker-compose.cpu.yml up"
echo "  - For minimal footprint: docker run crawl4ai-mcp:lightweight"
echo "  - For RunPod deployment: Use Dockerfile.runpod (optimized for serverless)"