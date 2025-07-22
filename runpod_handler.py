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

# Import MCP server module to access the underlying functions
import crawl4ai_mcp.server as mcp_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_async_safe(coro):
    """
    Safely run an async coroutine in RunPod serverless environment.
    Handles both cases: running event loop and no event loop.
    """
    try:
        # Check if there's already a running event loop
        try:
            loop = asyncio.get_running_loop()
            # There's a running loop - we need to schedule the coroutine
            logger.info("Running event loop detected, scheduling coroutine as task")
            
            # Create a concurrent.futures.Future to get the result
            import concurrent.futures
            import threading
            
            # Create a future to hold the result
            future = concurrent.futures.Future()
            
            def run_in_thread():
                """Run the coroutine in a separate thread with its own event loop"""
                try:
                    # Create a new event loop for this thread
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    
                    try:
                        # Run the coroutine
                        result = new_loop.run_until_complete(coro)
                        future.set_result(result)
                    finally:
                        new_loop.close()
                        
                except Exception as e:
                    future.set_exception(e)
            
            # Run in a separate thread to avoid loop conflicts
            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()
            
            # Get the result (this will raise any exception that occurred)
            return future.result()
            
        except RuntimeError:
            # No running loop - safe to create and use our own
            logger.info("No running event loop, creating new one")
            
            # Create a fresh event loop
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            
            try:
                # Run the coroutine in the new loop
                return new_loop.run_until_complete(coro)
            finally:
                # Clean up the loop when done
                new_loop.close()
                
    except Exception as e:
        logger.error(f"Error in run_async_safe: {e}")
        logger.error(f"Coroutine type: {type(coro)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise

async def handle_crawl_request(operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle different crawling operations by calling the underlying MCP functions properly
    """
    try:
        logger.info(f"Executing operation: {operation} with params: {params}")
        
        # Import the request/response classes we need
        from crawl4ai_mcp.server import (
            CrawlRequest, FileProcessRequest, 
            GoogleSearchRequest, GoogleBatchSearchRequest
        )
        
        # Handle different operations with proper parameter construction
        if operation == 'crawl_url':
            request = CrawlRequest(**params)
            
            # Diagnostic logging to understand the function type
            crawl_func = mcp_server.crawl_url
            logger.info(f"Function type: {type(crawl_func)}")
            logger.info(f"Function callable: {callable(crawl_func)}")
            logger.info(f"Function dir: {[attr for attr in dir(crawl_func) if not attr.startswith('_')]}")
            
            # Check if it's a FastMCP FunctionTool that needs special handling
            if hasattr(crawl_func, 'func'):
                logger.info("Function has .func attribute, using it")
                result = await crawl_func.func(request)
            elif hasattr(crawl_func, '__call__'):
                logger.info("Function is callable, calling directly")
                result = await crawl_func(request)
            else:
                logger.error(f"Function is not callable and has no .func attribute: {type(crawl_func)}")
                raise TypeError(f"'{type(crawl_func).__name__}' object is not callable")
                
        elif operation == 'crawl_url_with_fallback':
            request = CrawlRequest(**params)
            crawl_func = mcp_server.crawl_url_with_fallback
            if hasattr(crawl_func, 'func'):
                result = await crawl_func.func(request)
            else:
                result = await crawl_func(request)
                
        elif operation == 'process_file':
            request = FileProcessRequest(**params)
            process_func = mcp_server.process_file
            if hasattr(process_func, 'func'):
                result = await process_func.func(request)
            else:
                result = await process_func(request)
                
        elif operation == 'search_google':
            request = GoogleSearchRequest(**params)
            search_func = mcp_server.search_google
            if hasattr(search_func, 'func'):
                result = await search_func.func(request)
            else:
                result = await search_func(request)
                
        elif operation == 'batch_search_google':
            request = GoogleBatchSearchRequest(**params)
            batch_func = mcp_server.batch_search_google
            if hasattr(batch_func, 'func'):
                result = await batch_func.func(request)
            else:
                result = await batch_func(request)
                
        elif operation == 'extract_structured_data':
            # This one uses StructuredExtractionRequest
            from crawl4ai_mcp.server import StructuredExtractionRequest
            request = StructuredExtractionRequest(**params)
            extract_func = mcp_server.extract_structured_data
            if hasattr(extract_func, 'func'):
                result = await extract_func.func(request)
            else:
                result = await extract_func(request)
                
        # For operations that take simple parameters, call with fallback
        elif operation == 'deep_crawl_site':
            deep_func = mcp_server.deep_crawl_site
            if hasattr(deep_func, 'func'):
                result = await deep_func.func(**params)
            else:
                result = await deep_func(**params)
                
        elif operation == 'intelligent_extract':
            intel_func = mcp_server.intelligent_extract
            if hasattr(intel_func, 'func'):
                result = await intel_func.func(**params)
            else:
                result = await intel_func(**params)
                
        elif operation == 'extract_entities':
            entities_func = mcp_server.extract_entities
            if hasattr(entities_func, 'func'):
                result = await entities_func.func(**params)
            else:
                result = await entities_func(**params)
                
        elif operation == 'extract_youtube_transcript':
            youtube_func = mcp_server.extract_youtube_transcript
            if hasattr(youtube_func, 'func'):
                result = await youtube_func.func(params)
            else:
                result = await youtube_func(params)
                
        elif operation == 'batch_extract_youtube_transcripts':
            batch_youtube_func = mcp_server.batch_extract_youtube_transcripts
            if hasattr(batch_youtube_func, 'func'):
                result = await batch_youtube_func.func(params)
            else:
                result = await batch_youtube_func(params)
                
        elif operation == 'batch_crawl':
            batch_func = mcp_server.batch_crawl
            if hasattr(batch_func, 'func'):
                result = await batch_func.func(**params)
            else:
                result = await batch_func(**params)
                
        elif operation == 'search_and_crawl':
            search_crawl_func = mcp_server.search_and_crawl
            if hasattr(search_crawl_func, 'func'):
                result = await search_crawl_func.func(**params)
            else:
                result = await search_crawl_func(**params)
                
        else:
            return {
                'error': f'Unknown operation: {operation}',
                'available_operations': [
                    'crawl_url', 'crawl_url_with_fallback', 'deep_crawl_site',
                    'intelligent_extract', 'extract_entities', 'extract_structured_data',
                    'process_file', 'extract_youtube_transcript', 'batch_extract_youtube_transcripts',
                    'search_google', 'batch_search_google', 'search_and_crawl', 'batch_crawl'
                ]
            }
        
        return {
            'operation': operation,
            'success': True,
            'result': result
        }
        
    except Exception as e:
        logger.error(f"Error executing {operation}: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Parameters received: {params}")
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