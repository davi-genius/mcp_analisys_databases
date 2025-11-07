import argparse
import logging
import os
import sys
import json
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from starlette.responses import Response, JSONResponse, FileResponse
from starlette.requests import Request
from mcp.server.fastmcp import FastMCP

from config import configure_logging, server_lifespan, session_handler
from tools.mcp_tools import register_all_tools
from prompts.prompts import MODELS, get_model_list, get_model_by_id, get_model_curl_command

# Configure logging
logger = configure_logging()

# Initialize MCP server
mcp = FastMCP(
    "PostgreSQL Performance Analyzer", 
    instructions="""
    This MCP server helps you optimize PostgreSQL database performance by:
    - Identifying slow-running queries
    - Analyzing query execution plans
    - Recommending indexes
    - Suggesting query rewrites
    - Analyzing database structure
    
    IMPORTANT: This is a READ-ONLY tool. All operations are performed in read-only mode
    for security reasons. No database modifications will be made.
    
    You must provide an AWS Secrets Manager secret name containing your database credentials
    when using any of the tools.
    """,
    stateless_http=True, 
    json_response=False,
    lifespan=server_lifespan
)

# Add a health check route directly to the MCP server
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """
    Simple health check endpoint for ALB Target Group.
    Always returns 200 OK to indicate the service is running.
    """
    return Response(
        content="healthy",
        status_code=200,
        media_type="text/plain"
    )

# Add a session status endpoint
@mcp.custom_route("/sessions", methods=["GET"])
async def session_status(request):
    """
    Show active sessions for debugging purposes
    """
    active_sessions = len(session_handler.sessions)
    session_ids = list(session_handler.sessions.keys())
    
    content = f"Active sessions: {active_sessions}\n"
    content += f"Session IDs: {', '.join(session_ids)}\n"
    
    return Response(
        content=content,
        status_code=200,
        media_type="text/plain"
    )

# Add prompts list endpoint
@mcp.custom_route("/prompts", methods=["GET"])
async def list_prompts(request):
    """
    Lista todos os prompts disponíveis
    """
    return Response(
        content=get_model_list(),
        status_code=200,
        media_type="text/plain"
    )

# Add prompts JSON endpoint
@mcp.custom_route("/api/prompts", methods=["GET"])
async def list_prompts_json(request):
    """
    Lista todos os prompts em formato JSON
    """
    return JSONResponse({"prompts": MODELS})

# Add specific prompt endpoint
@mcp.custom_route("/api/prompts/{prompt_id}", methods=["GET"])
async def get_prompt(request):
    """
    Retorna detalhes de um prompt específico
    """
    prompt_id = request.path_params.get("prompt_id")
    model = get_model_by_id(prompt_id)
    
    if not model:
        return JSONResponse({"error": "Prompt não encontrado"}, status_code=404)
    
    return JSONResponse(model)

# Add prompt command generator
@mcp.custom_route("/api/prompts/{prompt_id}/command", methods=["GET"])
async def get_prompt_command(request):
    """
    Gera comando curl para executar o prompt
    """
    prompt_id = request.path_params.get("prompt_id")
    model = get_model_by_id(prompt_id)
    
    if not model:
        return JSONResponse({"error": "Prompt não encontrado"}, status_code=404)
    
    # Pegar parâmetros de conexão da query string ou usar defaults
    host = request.query_params.get("host", "localhost")
    port = int(request.query_params.get("port", "5432"))
    dbname = request.query_params.get("dbname", "petclinic")
    username = request.query_params.get("username", "petclinic")
    password = request.query_params.get("password", "petclinic")
    
    command_data = get_model_curl_command(
        prompt_id, host, port, dbname, username, password
    )
    
    return JSONResponse(command_data)

# Register all tools with the MCP server
register_all_tools(mcp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PostgreSQL Performance Analyzer Remote MCP Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--session-timeout', type=int, default=1800,
                        help='Session timeout in seconds (default: 1800)')
    parser.add_argument('--request-timeout', type=int, default=300,
                        help='Request timeout in seconds (default: 300)')
    parser.add_argument('--log-level', type=str, default='INFO',
                        help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--json-response', action='store_true', default=False,
                        help='Enable JSON responses instead of SSE streams')
    
    args = parser.parse_args()
    
    # Configure the MCP server settings
    mcp.settings.port = args.port
    mcp.settings.host = args.host
    
    # Update session handler settings
    session_handler.session_timeout = args.session_timeout
    
    # Configure server to handle multiple concurrent connections
    # Set a high value for max concurrent requests
    os.environ["MCP_MAX_CONCURRENT_REQUESTS"] = "100"  # Allow many concurrent requests
    os.environ["MCP_REQUEST_TIMEOUT_SECONDS"] = str(args.request_timeout)
    
    logger.info(f"Starting PostgreSQL Performance Analyzer Remote MCP server on {args.host}:{args.port}")
    logger.info(f"Health check endpoint available at http://{args.host}:{args.port}/health")
    logger.info(f"Session status endpoint available at http://{args.host}:{args.port}/sessions")
    logger.info(f"Session timeout: {args.session_timeout} seconds")
    logger.info(f"Request timeout: {args.request_timeout} seconds")
    
    try:
        mcp.run(transport='streamable-http')
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        # If the server crashes, try to restart it
        import time
        time.sleep(5)  # Wait 5 seconds before restarting
        logger.info("Attempting to restart server...")
        mcp.run(transport='streamable-http')