#!/bin/bash
# LangFlow MCP Wrapper Script
# This script allows LangFlow to connect to the containerized MCP server via stdio

exec docker exec -i semantic_mcp-mcp-server-1 python /app/semantic_mcp_server.py