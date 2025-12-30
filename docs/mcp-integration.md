# MCP (Model Context Protocol) Integration

This document describes the MCP integration for Ollama agents, enabling agents to use external tools via the Model Context Protocol.

## Overview

MCP allows Ollama agents to communicate with external tool servers over JSON-RPC 2.0 via stdio. This enables agents to access capabilities like web search, file operations, databases, and more through standardized tool interfaces.

## Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Types & Parser | ✅ Complete |
| Phase 2 | Layer Handling | ✅ Complete |
| Phase 3 | Runtime Manager | ✅ Complete |
| Phase 4 | CLI Commands | ✅ Complete |

## Agentfile Syntax

### Simple Command Format
```dockerfile
MCP <name> <command> [args...]
```

Example:
```dockerfile
FROM llama3.2
AGENT TYPE conversational
SYSTEM You are a helpful assistant with MCP tools.
MCP calculator python3 ./mcp-server.py
MCP websearch node ./search-server.js
```

### JSON Format
```dockerfile
MCP {"name": "custom", "command": "uv", "args": ["run", "server.py"], "env": {"API_KEY": "xxx"}}
```

## Architecture

### Type Definitions

**MCPRef** (`types/model/config.go`):
```go
type MCPRef struct {
    Name    string            `json:"name,omitempty"`
    Digest  string            `json:"digest,omitempty"`
    Command string            `json:"command,omitempty"`
    Args    []string          `json:"args,omitempty"`
    Env     map[string]string `json:"env,omitempty"`
    Type    string            `json:"type,omitempty"`  // "stdio"
}
```

### Tool Namespacing

MCP tools are namespaced to avoid conflicts:
- Format: `mcp_{serverName}_{toolName}`
- Example: Server "calculator" with tool "add" → `mcp_calculator_add`

### Runtime Flow

1. Agent starts → MCP servers spawn as subprocesses
2. Initialize via JSON-RPC: `initialize` → `notifications/initialized`
3. Discover tools: `tools/list`
4. During chat, model calls tools → routed via `tools/call`
5. On shutdown, MCP servers are gracefully terminated

## Files

### Created

| File | Purpose |
|------|---------|
| `cmd/mcp.go` | Runtime MCP manager with JSON-RPC protocol |
| `cmd/mcp_cmd.go` | CLI commands for managing MCPs (push, pull, list, etc.) |
| `server/mcp.go` | MCP layer utilities (extraction, creation) |

### Modified

| File | Changes |
|------|---------|
| `types/model/config.go` | Added `MCPRef` type, `MCPs` field to `ConfigV2` |
| `types/model/name.go` | Added `"mcp"` to `ValidKinds` for 5-part name parsing |
| `api/types.go` | Added `MCPRef` alias, `MCPs` to `CreateRequest`/`ShowResponse` |
| `parser/parser.go` | Added `MCP` command parsing with JSON and simple formats |
| `server/create.go` | Added `setMCPLayers()` for MCP config handling |
| `server/routes.go` | Added `MCPs` to show response |
| `cmd/cmd.go` | MCP integration in `chat()` function |
| `cmd/interactive.go` | Added `/mcp` and `/mcps` REPL commands |

## Usage Example

### 1. Create an MCP Server

```python
#!/usr/bin/env python3
# mcp-server.py
import json
import sys

def handle_request(req):
    method = req.get("method", "")
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "example", "version": "1.0"}
        }
    elif method == "tools/list":
        return {
            "tools": [{
                "name": "add",
                "description": "Adds two numbers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            }]
        }
    elif method == "tools/call":
        args = req["params"]["arguments"]
        return {"content": [{"type": "text", "text": f"{args['a'] + args['b']}"}]}
    return {}

for line in sys.stdin:
    req = json.loads(line)
    if "id" in req:
        result = handle_request(req)
        print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": result}), flush=True)
```

### 2. Create an Agent

```dockerfile
# my-agent.Agentfile
FROM gpt-oss:20b
AGENT TYPE conversational
SYSTEM You have access to a calculator. Use the add tool when asked to add numbers.
MCP calculator python3 ./mcp-server.py
```

### 3. Build and Run

```bash
ollama create my-agent -f my-agent.Agentfile
ollama run my-agent "What is 15 + 27?"
```

Output:
```
Loaded MCP servers: calculator (1 tools)
Executing: mcp_calculator_add
Output: 42
The result is 42.
```

## CLI Commands

The `ollama mcp` command provides utilities for managing MCP servers:

### Global Config Commands

Add an MCP server to the global config (`~/.ollama/mcp.json`):
```bash
# Add MCP to global config (available to all agents)
ollama mcp add web-search uv run ./mcp-server.py
ollama mcp add calculator python3 /path/to/calc.py

# List global MCP servers (shows enabled/disabled status)
ollama mcp list-global

# Disable an MCP server (keeps in config but won't be loaded)
ollama mcp disable web-search

# Re-enable a disabled MCP server
ollama mcp enable web-search

# Remove from global config
ollama mcp remove-global web-search
```

### Registry Commands

Package and push MCPs to a registry:
```bash
# Push MCP to registry (creates locally first)
ollama mcp push mcp/websearch:1.0 ./my-mcp-server/

# Pull MCP from registry
ollama mcp pull mcp/websearch:1.0

# List installed MCPs (from registry)
ollama mcp list

# Show MCP details
ollama mcp show mcp/websearch:1.0

# Remove MCP
ollama mcp rm mcp/websearch:1.0
```

## REPL Commands

Inside `ollama run`, you can manage MCP servers dynamically:

```
>>> /mcp                                     # Show all MCP servers (model + global)
>>> /mcp add calc python3 ./calc-server.py   # Add MCP server to global config
>>> /mcp remove calc                         # Remove MCP server from global config
>>> /mcp disable calc                        # Disable an MCP server (keep in config)
>>> /mcp enable calc                         # Re-enable a disabled MCP server
>>> /? mcp                                   # Get help for MCP commands
```

The `/mcp` command shows all available MCP servers (both bundled with the model and from global config). Disabled servers are shown with a `[disabled]` marker. Use `/mcp add` and `/mcp remove` to manage MCPs in `~/.ollama/mcp.json`. Changes take effect on the next message.

## Global Config

MCPs can be configured globally in `~/.ollama/mcp.json`:

```json
{
  "mcpServers": {
    "web-search": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "./mcp-server.py"]
    },
    "calculator": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/calc.py"],
      "disabled": true
    }
  }
}
```

The `disabled` field is optional. When set to `true`, the MCP server will not be loaded when running agents.

## Future Enhancements

1. **Remote Registry Push/Pull**: Full support for pushing/pulling MCPs to/from remote registries
2. **Use go-sdk**: Consider using `github.com/modelcontextprotocol/go-sdk` for protocol handling
3. **Resource Support**: Add MCP resources (not just tools)
4. **Prompt Support**: Add MCP prompts

## Protocol Reference

MCP uses JSON-RPC 2.0 over stdio with these key methods:

| Method | Direction | Purpose |
|--------|-----------|---------|
| `initialize` | Client→Server | Handshake with capabilities |
| `notifications/initialized` | Client→Server | Confirm initialization |
| `tools/list` | Client→Server | Discover available tools |
| `tools/call` | Client→Server | Execute a tool |

See [MCP Specification](https://modelcontextprotocol.io/docs) for full details.
