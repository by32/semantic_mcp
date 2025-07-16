#!/usr/bin/env python3
"""
AWS MCP Bridge - STDIO to HTTP API Bridge
Allows LangFlow STDIO MCP Tools to connect to AWS HTTP API
"""

import json
import sys
import os
import time
from typing import Dict, Any
import urllib.request
import urllib.error

class AWSMCPBridge:
    """Bridge between LangFlow STDIO and AWS HTTP API"""
    
    def __init__(self, api_url: str = None):
        # API URL will be set after deployment
        self.api_url = api_url or os.getenv('AWS_MCP_API_URL', 'PLACEHOLDER_API_URL')
        self.session_id = f"session_{int(time.time())}"
        self.request_count = 0
        
        # Log to stderr for debugging
        self.debug = os.getenv('DEBUG', '').lower() in ('1', 'true', 'yes')
        
        if self.debug:
            print(f"DEBUG: AWS MCP Bridge starting with API URL: {self.api_url}", file=sys.stderr)
    
    def log_debug(self, message: str):
        """Log debug message to stderr"""
        if self.debug:
            print(f"DEBUG: {message}", file=sys.stderr)
    
    def make_http_request(self, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to AWS API Gateway"""
        try:
            # Add session tracking
            self.request_count += 1
            request_id = f"{self.session_id}_{self.request_count}"
            
            self.log_debug(f"Request #{self.request_count}: {mcp_request.get('method', 'unknown')}")
            
            # Prepare HTTP request
            data = json.dumps(mcp_request).encode('utf-8')
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'LangFlow-MCP-Bridge/1.0',
                'X-Session-ID': self.session_id,
                'X-Request-ID': request_id
            }
            
            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers=headers,
                method='POST'
            )
            
            # Make request with timeout
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                
                # Parse response
                if response.getcode() == 200:
                    api_response = json.loads(response_data)
                    
                    # Extract MCP response from API Gateway response
                    if isinstance(api_response, dict) and 'body' in api_response:
                        # API Gateway wrapped response
                        body = api_response['body']
                        if isinstance(body, str):
                            return json.loads(body)
                        else:
                            return body
                    else:
                        # Direct response
                        return api_response
                else:
                    # HTTP error
                    return {
                        "jsonrpc": "2.0",
                        "id": mcp_request.get("id"),
                        "error": {
                            "code": -32603,
                            "message": f"HTTP {response.getcode()}: {response_data}"
                        }
                    }
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No error details"
            self.log_debug(f"HTTP Error {e.code}: {error_body}")
            
            return {
                "jsonrpc": "2.0",
                "id": mcp_request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"HTTP {e.code}: {error_body}"
                }
            }
            
        except urllib.error.URLError as e:
            self.log_debug(f"URL Error: {e}")
            
            return {
                "jsonrpc": "2.0",
                "id": mcp_request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Network error: {str(e)}"
                }
            }
            
        except Exception as e:
            self.log_debug(f"Unexpected error: {e}")
            
            return {
                "jsonrpc": "2.0",
                "id": mcp_request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Bridge error: {str(e)}"
                }
            }
    
    def handle_stdio(self):
        """Handle STDIO communication with LangFlow"""
        self.log_debug("Starting STDIO handling...")
        
        try:
            # Process each line from stdin
            for line_num, line in enumerate(sys.stdin, 1):
                line = line.strip()
                if not line:
                    continue
                
                self.log_debug(f"Processing line {line_num}: {line[:100]}...")
                
                try:
                    # Parse MCP request
                    mcp_request = json.loads(line)
                    
                    # Forward to AWS API
                    response = self.make_http_request(mcp_request)
                    
                    # Send response back to LangFlow
                    if response:
                        output = json.dumps(response)
                        print(output)
                        sys.stdout.flush()
                        
                        self.log_debug(f"Response sent: {output[:100]}...")
                        
                except json.JSONDecodeError as e:
                    self.log_debug(f"JSON decode error: {e}")
                    
                    # Send error response
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
                except Exception as e:
                    self.log_debug(f"Line processing error: {e}")
                    
                    # Send error response
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Processing error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            self.log_debug("Bridge interrupted by user")
        except Exception as e:
            self.log_debug(f"STDIO handling error: {e}")
        finally:
            self.log_debug("Bridge shutting down")

def main():
    """Main entry point"""
    # Check if API URL is configured
    bridge = AWSMCPBridge()
    
    if 'PLACEHOLDER_API_URL' in bridge.api_url:
        print(json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": "AWS API URL not configured. Please set AWS_MCP_API_URL environment variable or update the script."
            }
        }))
        sys.exit(1)
    
    # Start the bridge
    bridge.handle_stdio()

if __name__ == "__main__":
    main()