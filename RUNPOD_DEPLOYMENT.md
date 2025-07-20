# RunPod Serverless Deployment Guide

Deploy the Crawl4AI MCP Server as a serverless worker on RunPod's cloud platform.

## 🎯 Overview

This project is **CPU-only** and doesn't require GPU acceleration. However, RunPod provides excellent serverless infrastructure for scaling web crawling workloads.

### Why RunPod for Web Crawling?
- **Serverless scaling**: Pay only for actual usage
- **Fast cold starts**: Workers spin up quickly for burst traffic
- **Cost-effective**: No idle server costs
- **Global availability**: Distributed infrastructure

## 🚀 Quick Deployment

### Option A: Use Pre-built Image (Recommended)

**Automated builds available!** GitHub Actions automatically builds and pushes images to Docker Hub.

```
Image: docker.io/gemneye/crawl4ai-runpod-serverless:latest
Platform: AMD64/X86_64 only
Auto-updated: On every commit to main branch
```

### Option B: Build Manually

```bash
# Build the RunPod-specific image
docker build -f Dockerfile.runpod -t your-username/crawl4ai-runpod:latest .

# Test locally first
docker run --rm -it your-username/crawl4ai-runpod:latest

# Push to Docker Hub
docker push your-username/crawl4ai-runpod:latest
```

> **Note**: See [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md) for automated build pipeline details.

### Step 2: Deploy on RunPod Console

1. Go to [RunPod Serverless Console](https://console.runpod.io/serverless)
2. Click **New Endpoint**
3. Select **Custom Source** → **Docker Image**
4. Enter the pre-built image: `docker.io/gemneye/crawl4ai-runpod-serverless:latest`
5. **Important**: Select **CPU-only** workers (no GPU needed)
6. Configure:
   - **Name**: `crawl4ai-mcp-server`
   - **Worker Configuration**: CPU instances (cheaper)
   - **Auto-scaling**: Enable for burst handling
   - **Max Workers**: Set based on expected load
   - **Platform**: AMD64/X86_64 (automatically selected)

### Step 3: Test Your Deployment

Use the RunPod console's test interface:

```json
{
    "input": {
        "operation": "crawl_url",
        "params": {
            "url": "https://example.com",
            "generate_markdown": true
        }
    }
}
```

## 🛠️ Available Operations

### Single URL Crawling
```json
{
    "input": {
        "operation": "crawl_url",
        "params": {
            "url": "https://example.com",
            "generate_markdown": true,
            "wait_for_js": false,
            "timeout": 30
        }
    }
}
```

### Deep Site Crawling
```json
{
    "input": {
        "operation": "deep_crawl_site",
        "params": {
            "url": "https://docs.example.com",
            "max_depth": 2,
            "max_pages": 10,
            "crawl_strategy": "bfs"
        }
    }
}
```

### YouTube Transcript Extraction
```json
{
    "input": {
        "operation": "extract_youtube_transcript",
        "params": {
            "url": "https://www.youtube.com/watch?v=VIDEO_ID",
            "languages": ["en"],
            "include_timestamps": true
        }
    }
}
```

### File Processing (PDF, Office, etc.)
```json
{
    "input": {
        "operation": "process_file",
        "params": {
            "url": "https://example.com/document.pdf",
            "max_size_mb": 50,
            "include_metadata": true
        }
    }
}
```

### Google Search + Crawl
```json
{
    "input": {
        "operation": "search_and_crawl",
        "params": {
            "search_query": "python machine learning tutorial",
            "num_search_results": 5,
            "crawl_top_results": 3
        }
    }
}
```

### Batch Operations
```json
{
    "input": {
        "operation": "batch_operations",
        "operations": [
            {
                "operation": "crawl_url",
                "params": {"url": "https://example1.com", "generate_markdown": true}
            },
            {
                "operation": "crawl_url",
                "params": {"url": "https://example2.com", "generate_markdown": true}
            }
        ]
    }
}
```

## 🔧 Local Testing

Test your handler locally before deploying:

```bash
# Test with the provided test input
python runpod_handler.py

# Or create custom test input
echo '{
    "input": {
        "operation": "crawl_url",
        "params": {
            "url": "https://httpbin.org/html",
            "generate_markdown": true
        }
    }
}' > custom_test.json

python runpod_handler.py
```

## 📊 API Usage Examples

### Using cURL
```bash
# Replace YOUR_ENDPOINT_ID with your actual endpoint ID
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "operation": "crawl_url",
      "params": {
        "url": "https://example.com",
        "generate_markdown": true
      }
    }
  }'
```

### Using Python SDK
```python
import runpod

# Set your API key
runpod.api_key = "your-api-key"

# Run a crawl operation
result = runpod.run(
    endpoint_id="your-endpoint-id",
    job_input={
        "operation": "crawl_url",
        "params": {
            "url": "https://example.com",
            "generate_markdown": True
        }
    }
)

print(result)
```

### Using JavaScript/Node.js
```javascript
const response = await fetch('https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    input: {
      operation: 'crawl_url',
      params: {
        url: 'https://example.com',
        generate_markdown: true
      }
    }
  })
});

const result = await response.json();
console.log(result);
```

## 💰 Cost Optimization

### CPU-Only Configuration
- **Advantage**: Significantly cheaper than GPU instances
- **Performance**: Adequate for web crawling workloads
- **Recommendation**: Use 4-8 vCPU instances for good performance

### Auto-Scaling Settings
```yaml
min_workers: 0          # Scale to zero when idle
max_workers: 10         # Adjust based on expected load
scale_up_threshold: 5   # Queue depth trigger
scale_down_delay: 30s   # Wait before scaling down
```

### Request Patterns
- **Burst usage**: Perfect for RunPod's model
- **Background processing**: Cost-effective serverless execution
- **Batch processing**: Process multiple URLs in single request

## 🔒 Security and Configuration

### Environment Variables
Set these in RunPod console if needed:

```bash
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
FASTMCP_LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=100
```

### Request Limits
- **File size**: 100MB default (configurable)
- **Timeout**: 30-60 seconds per operation
- **Concurrent pages**: Limited for stability

### Error Handling
The handler includes comprehensive error handling:
- Invalid operations return error with available operations
- Timeouts are caught and reported
- Validation errors include example formats

## 📈 Monitoring and Debugging

### Logs
View logs in RunPod console:
- Worker startup logs
- Operation execution logs
- Error tracking and debugging

### Metrics
Monitor in RunPod dashboard:
- Request count and success rate
- Execution time distribution
- Worker utilization
- Cost tracking

### Common Issues
1. **Cold start delays**: First request may take 30-60 seconds
2. **Memory limits**: Increase if processing large files
3. **Timeout errors**: Adjust timeout for complex sites

## 🚀 Advanced Usage

### Custom Operations
Extend the handler by adding new operations:

```python
# In runpod_handler.py
operations = {
    'crawl_url': crawl_url,
    'your_custom_operation': your_custom_function,
    # ... other operations
}
```

### Integration with Other Services
- **Webhooks**: Trigger crawling from external events
- **Scheduled crawling**: Use RunPod cron functionality
- **Data pipelines**: Chain with other RunPod workers

This setup provides a scalable, cost-effective way to deploy the Crawl4AI MCP Server for serverless web crawling workloads.