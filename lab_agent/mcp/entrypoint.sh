#!/bin/bash
# Compass MCP Agent Entry Point
# This runs inside the container

if [ "$1" == "agent" ]; then
    # Start the interactive prompt
    python /app/mcp-prompt.py
else
    # Start the MCP server
    python src/main.py --host 0.0.0.0 --port 8000
fi
