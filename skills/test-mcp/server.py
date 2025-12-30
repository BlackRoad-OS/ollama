#!/usr/bin/env python3
"""
A simple test MCP server that exposes an echo tool.
"""

import json
import sys

def handle_request(req):
    method = req.get("method", "")

    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "test-mcp", "version": "1.0.0"}
        }
    elif method == "notifications/initialized":
        # Notification, no response needed
        return None
    elif method == "tools/list":
        return {
            "tools": [
                {
                    "name": "echo",
                    "description": "Echoes back the input text",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to echo"
                            }
                        },
                        "required": ["text"]
                    }
                },
                {
                    "name": "add",
                    "description": "Adds two numbers together",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "a": {
                                "type": "number",
                                "description": "First number"
                            },
                            "b": {
                                "type": "number",
                                "description": "Second number"
                            }
                        },
                        "required": ["a", "b"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name", "")
        args = params.get("arguments", {})

        if tool_name == "echo":
            text = args.get("text", "")
            return {
                "content": [{"type": "text", "text": f"Echo: {text}"}]
            }
        elif tool_name == "add":
            a = args.get("a", 0)
            b = args.get("b", 0)
            result = a + b
            return {
                "content": [{"type": "text", "text": f"Result: {a} + {b} = {result}"}]
            }
        else:
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                "isError": True
            }
    else:
        return {}

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line.strip())
            result = handle_request(req)

            # Only send response if there's an ID (not a notification)
            if "id" in req and result is not None:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req["id"],
                    "result": result
                }
                print(json.dumps(resp), flush=True)
        except json.JSONDecodeError:
            pass
        except Exception as e:
            if "id" in req:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(resp), flush=True)

if __name__ == "__main__":
    main()
