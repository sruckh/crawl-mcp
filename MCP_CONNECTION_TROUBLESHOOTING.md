# MCP Server Connection Troubleshooting Guide

## Issue Analysis

The MCP server connection error occurs because the configuration files contain incorrect paths that don't match the current workspace directory.

### Error Details
- **Error**: `Error sending message to file:///undefined: TypeError: fetch failed`
- **Root Cause**: Configuration files point to `/home/user/prj/crawl` but actual workspace is `/mnt/backblaze/crawl-mcp`
- **Impact**: Server fails to initialize due to incorrect working directory and PYTHONPATH

## Solution

### 1. Corrected Configuration Files

I've created corrected configuration files that use the proper workspace directory:

#### Standard Configuration
- **File**: `configs/claude_desktop_config_corrected.json`
- **Key Changes**:
  - `cwd`: Updated from `/home/user/prj/crawl` to `/mnt/backblaze/crawl-mcp`
  - `PYTHONPATH`: Updated from `/home/user/prj/crawl/venv/lib/python3.10/site-packages` to `/mnt/backblaze/crawl-mcp`

#### Pure HTTP Configuration
- **File**: `configs/claude_desktop_config_pure_http_corrected.json`
- **Key Changes**:
  - `cwd`: Updated to `/mnt/backblaze/crawl-mcp`
  - `PYTHONPATH`: Updated to `/mnt/backblaze/crawl-mcp`

#### Script Configuration
- **File**: `configs/claude_desktop_config_script_corrected.json`
- **Key Changes**:
  - `cwd`: Updated to `/mnt/backblaze/crawl-mcp`
  - `PYTHONPATH`: Updated to `/mnt/backblaze/crawl-mcp`

### 2. Dependencies Issue

The server requires several dependencies that may not be installed:
- `fastmcp>=0.1.0`
- `crawl4ai>=0.3.0`
- Other packages listed in `requirements.txt`

### 3. Testing the Configuration

#### Method 1: Direct Python Import Test
```bash
cd /mnt/backblaze/crawl-mcp
python -c "import crawl4ai_mcp.server; print('Server import successful')"
```

#### Method 2: Manual Server Start
```bash
cd /mnt/backblaze/crawl-mcp
python -m crawl4ai_mcp.server --transport stdio
```

#### Method 3: HTTP Transport Test
```bash
cd /mnt/backblaze/crawl-mcp
python -m crawl4ai_mcp.server --transport streamable-http --host 127.0.0.1 --port 8000
```

### 4. Configuration Usage

To use the corrected configurations:

1. **Replace existing config**: Copy the corrected file to your Claude Desktop configuration
   ```bash
   # For standard configuration
   cp configs/claude_desktop_config_corrected.json ~/.config/claude-desktop/config.json
   
   # For pure HTTP configuration
   cp configs/claude_desktop_config_pure_http_corrected.json ~/.config/claude-desktop/config.json
   ```

2. **Update VS Code settings**: If using VS Code MCP extension, update the configuration path

3. **Restart Claude Desktop**: After updating the configuration, restart Claude Desktop to apply changes

### 5. Environment Variables

You can also use environment variables to override configuration:
- `MCP_TRANSPORT`: Set to "stdio", "streamable-http", or "sse"
- `MCP_HOST`: Set the host for HTTP transport (default: 127.0.0.1)
- `MCP_PORT`: Set the port for HTTP transport (default: 8000)

### 6. Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'fastmcp'` | Install dependencies: `pip install -r requirements.txt` |
| `Error: file:///undefined` | Check configuration paths and ensure they point to correct workspace |
| Server exits immediately | Check Python path and ensure all dependencies are installed |
| Connection timeout | Verify server is running and port is accessible |

### 7. Verification Steps

1. **Check workspace directory**:
   ```bash
   pwd  # Should return /mnt/backblaze/crawl-mcp
   ```

2. **Verify configuration**:
   ```bash
   cat configs/claude_desktop_config_corrected.json | grep cwd
   # Should show: "cwd": "/mnt/backblaze/crawl-mcp"
   ```

3. **Test server startup**:
   ```bash
   python -m crawl4ai_mcp.server --help
   ```

4. **Check logs**: Look for any error messages in the MCP client logs