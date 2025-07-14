#!/bin/bash
# Wrapper script to connect LangFlow to containerized MCP server via stdio

# Execute the MCP server inside the running container
docker exec -i semantic_mcp-cube-1 python /cube/conf/semantic_mcp_server.py

# This script:
# 1. Takes stdin from LangFlow
# 2. Passes it to the MCP server running in the container
# 3. Returns stdout back to LangFlow
# 4. Maintains the stdio protocol that MCP expects