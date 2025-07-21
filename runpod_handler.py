"""
RunPod Serverless Handler for Crawl4AI MCP Server
Provides serverless web crawling capabilities via RunPod platform
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List, Optional

# Import runpod with error handling for local development
try:
    import runpod
    RUNPOD_AVAILABLE = True
except ImportError:
    # runpod is not available in local development
    RUNPOD_AVAILABLE = False
    print("Warning: runpod module not found. This is expected for local development.")

# Import our MCP server components
from crawl4ai_mcp.server import (
    crawl_url,
    deep_crawl_site,
    intelligent_extract,
    extract_entities,
    extract_structured_data,
    process_file,
    extract_youtube_transcript,
    search_google,
    search_and_crawl,
    batch_crawl,
    crawl_url_with_fallback
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_async_safe(coro):
    """
    Safely run an async coroutine in both sync and async contexts.
    This handles the case where an event loop is already running.
    """
    try:
        # Check if there's already a running event loop
        try:
            loop = asyncio.get_running_loop()
            # If we have a running loop, use it
            return loop.run_until_complete(coro)
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(coro)
    except Exception as e:
        # Fallback for any other issues
        logger.error(f"Error in run_async_safe: {e}")
        raise

async def handle_crawl_request(operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle different crawling operations based on the operation type
    """
    try:
        # Map operations to their corresponding functions
        operations = {
            'crawl_url': crawl_url,
            'deep_crawl_site': deep_crawl_site,
            'intelligent_extract': intelligent_extract,
            'extract_entities': extract_entities,
            'extract_structured_data': extract_structured_data,
            'process_file': process_file,
            'extract_youtube_transcript': extract_youtube_transcript,
            'search_google': search_google,
            'search_and_crawl': search_and_crawl,
            'batch_crawl': batch_crawl,
            'crawl_url_with_fallback': crawl_url_with_fallback
        }
        
        if operation not in operations:
            return {
                'error': f'Unknown operation: {operation}',
                'available_operations': list(operations.keys())
            }
        
        # Execute the operation
        logger.info(f"Executing operation: {operation} with params: {params}")
        result = await operations[operation](**params)
        
        return {
            'operation': operation,
            'success': True,
            'result': result
        }
        
    except Exception as e:
        logger.error(f"Error executing {operation}: {str(e)}")
        return {
            'operation': operation,
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    RunPod serverless handler function
    
    Expected input format:
    {
        "input": {
            "operation": "crawl_url",
            "params": {
                "url": "https://example.com",
                "generate_markdown": true
            }
        }
    }
    """
    logger.info("RunPod Crawl4AI Handler started")
    
    try:
        # Extract input data
        input_data = event.get('input', {})
        operation = input_data.get('operation', 'crawl_url')
        params = input_data.get('params', {})
        
        # Validate required parameters
        if not params:
            return {
                'error': 'No parameters provided',
                'example': {
                    'operation': 'crawl_url',
                    'params': {
                        'url': 'https://example.com',
                        'generate_markdown': True
                    }
                }
            }
        
        # Handle batch operations
        if operation == 'batch_operations':
            results = []
            batch_operations = input_data.get('operations', [])
            
            for batch_op in batch_operations:
                batch_operation = batch_op.get('operation')
                batch_params = batch_op.get('params', {})
                result = run_async_safe(handle_crawl_request(batch_operation, batch_params))
                results.append(result)
            
            return {
                'success': True,
                'batch_results': results,
                'total_operations': len(results)
            }
        
        # Handle single operation
        result = run_async_safe(handle_crawl_request(operation, params))
        return result
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

# Example usage patterns for different operations
EXAMPLE_INPUTS = {
    'crawl_url': {
        'operation': 'crawl_url',
        'params': {
            'url': 'https://example.com',
            'generate_markdown': True,
            'wait_for_js': False,
            'timeout': 30
        }
    },
    'deep_crawl_site': {
        'operation': 'deep_crawl_site',
        'params': {
            'url': 'https://docs.example.com',
            'max_depth': 2,
            'max_pages': 10,
            'crawl_strategy': 'bfs'
        }
    },
    'extract_youtube_transcript': {
        'operation': 'extract_youtube_transcript',
        'params': {
            'url': 'https://www.youtube.com/watch?v=VIDEO_ID',
            'languages': ['en'],
            'include_timestamps': True
        }
    },
    'process_file': {
        'operation': 'process_file',
        'params': {
            'url': 'https://example.com/document.pdf',
            'max_size_mb': 50,
            'include_metadata': True
        }
    },
    'search_and_crawl': {
        'operation': 'search_and_crawl',
        'params': {
            'search_query': 'python machine learning tutorial',
            'num_search_results': 5,
            'crawl_top_results': 3
        }
    },
    'batch_operations': {
        'operation': 'batch_operations',
        'operations': [
            {
                'operation': 'crawl_url',
                'params': {'url': 'https://example1.com', 'generate_markdown': True}
            },
            {
                'operation': 'crawl_url', 
                'params': {'url': 'https://example2.com', 'generate_markdown': True}
            }
        ]
    }
}

# Start the serverless function when the script is run
if __name__ == '__main__':
    if not RUNPOD_AVAILABLE:
        logger.error("Cannot start RunPod serverless worker: runpod module not available")
        logger.error("This script is designed to run on RunPod serverless infrastructure")
        logger.error("For local testing, use: python -c \"import runpod_handler; print(runpod_handler.EXAMPLE_INPUTS)\"")
        sys.exit(1)
    
    logger.info("Starting RunPod Crawl4AI Serverless Worker...")
    logger.info("Available operations:")
    for op in EXAMPLE_INPUTS.keys():
        logger.info(f"  - {op}")
    
    runpod.serverless.start({'handler': handler})