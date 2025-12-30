# ENTRYPOINT Feature for Ollama Agents

## Overview

The ENTRYPOINT command allows agents to specify an external program to run instead of the built-in Ollama chat loop. This makes Ollama a packaging/distribution mechanism for agents with custom runtimes.

## Status: Implemented ✓

## What Was Done

### 1. Types & API

**`types/model/config.go`**
- Added `Entrypoint string` field to `ConfigV2` struct

**`api/types.go`**
- Added `Entrypoint string` to `CreateRequest` (line ~576)
- Added `Entrypoint string` to `ShowResponse` (line ~632)

### 2. Parser

**`parser/parser.go`**
- Added "entrypoint" to `isValidCommand()` switch
- Added case in `CreateRequest()` to set `req.Entrypoint = c.Args`
- Updated `ParseFile()` to allow ENTRYPOINT without FROM (entrypoint-only agents)
- Added entrypoint serialization in `Command.String()`

### 3. Server

**`server/create.go`**
- Added `config.Entrypoint = r.Entrypoint` to store entrypoint in config
- Made FROM optional when ENTRYPOINT is specified:
  ```go
  } else if r.Entrypoint != "" {
      // Entrypoint-only agent: no base model needed
      slog.Debug("create entrypoint-only agent", "entrypoint", r.Entrypoint)
  }
  ```

**`server/routes.go`**
- Added `Entrypoint: m.Config.Entrypoint` to ShowResponse in `GetModelInfo()`

**`server/images.go`**
- Added entrypoint serialization in `Model.String()`:
  ```go
  if m.Config.Entrypoint != "" {
      modelfile.Commands = append(modelfile.Commands, parser.Command{
          Name: "entrypoint",
          Args: m.Config.Entrypoint,
      })
  }
  ```

### 4. CLI

**`cmd/cmd.go`**
- Added `Entrypoint string` to `runOptions` struct
- Updated agent detection to include Entrypoint check
- Added entrypoint check before interactive mode:
  ```go
  if opts.Entrypoint != "" {
      return runEntrypoint(cmd, opts)
  }
  ```
- Implemented `runEntrypoint()` function:
  - Parses entrypoint into command and args
  - Appends user prompt as additional argument if provided
  - Looks up command in PATH
  - Creates subprocess with stdin/stdout/stderr connected
  - Runs and waits for completion
- Updated `showInfo()` to display entrypoint in Agent section
- Updated `showInfo()` to hide Model section for entrypoint-only agents (no blank fields)
- Added `$PROMPT` placeholder support in `runEntrypoint()`:
  - If entrypoint contains `$PROMPT`, it's replaced with the user's prompt
  - If no placeholder, prompt is appended as positional argument (backwards compatible)
  - If no prompt provided, `$PROMPT` is removed from the command

## Usage

### Agentfile
```dockerfile
# Minimal entrypoint agent (no model required)
ENTRYPOINT ducky

# Or with full path
ENTRYPOINT /usr/local/bin/ducky

# Or with arguments
ENTRYPOINT ducky --verbose

# Use $PROMPT placeholder to control where prompt is inserted
ENTRYPOINT ducky -p $PROMPT

# Without placeholder, prompt is appended as positional argument
ENTRYPOINT echo "Hello"  # becomes: echo "Hello" <prompt>

# Can still bundle skills/MCPs with entrypoint agents
SKILL ./my-skill
MCP calculator python3 ./calc.py
ENTRYPOINT my-custom-runtime
```

### CLI
```bash
# Create the agent
ollama create ducky -f ducky.Agentfile

# Run it - starts the entrypoint (e.g., REPL)
ollama run ducky

# With prompt (passed as argument to entrypoint)
ollama run ducky "hello"

# Show agent info
ollama show ducky
#   Agent
#     entrypoint    ducky
```

## Testing Done

1. **Basic entrypoint execution**: ✓
   ```bash
   # Agentfile: ENTRYPOINT echo "Hello from entrypoint"
   ollama run test-entry  # Output: "Hello from entrypoint"
   ```

2. **Prompt passing (positional)**: ✓
   ```bash
   # Agentfile: ENTRYPOINT echo "Args:"
   ollama run echo-test "hello world"  # Output: "Args:" hello world
   ```

3. **Prompt passing ($PROMPT placeholder)**: ✓
   ```bash
   # Agentfile: ENTRYPOINT echo "Prompt was:" $PROMPT "end"
   ollama run echo-placeholder "hello world"  # Output: "Prompt was:" hello world "end"
   ollama run echo-placeholder                # Output: "Prompt was:" "end"
   ```

4. **Show command**: ✓
   ```bash
   ollama show ducky
   #   Agent
   #     entrypoint    ducky
   # (Model section hidden for entrypoint-only agents)
   ```

5. **List command**: ✓
   - Entrypoint-only agents show with small sizes (~200 bytes)

## Left Over / Future Enhancements

### 1. Context Passing via Environment Variables
Pass agent context to entrypoint via env vars:
- `OLLAMA_AGENT_NAME` - Name of the agent
- `OLLAMA_SKILLS_PATH` - Path to bundled skills
- `OLLAMA_MCPS` - JSON of MCP configurations

### ~~2. Arguments Placeholder~~ ✓ DONE
~~Support placeholder syntax for more control:~~
```dockerfile
# Now supported!
ENTRYPOINT ducky -p $PROMPT
```

### 3. Working Directory
Set working directory for entrypoint:
```dockerfile
WORKDIR /app
ENTRYPOINT ./run.sh
```

### 4. Interactive Mode Detection
Different behavior for REPL vs single-shot:
- Detect if stdin is a TTY
- Pass different flags based on mode

### 5. Signal Handling
Improved signal forwarding to subprocess:
- Forward SIGINT, SIGTERM gracefully
- Handle cleanup on parent exit

### 6. Entrypoint with Model
Allow both model and entrypoint:
```dockerfile
FROM llama3.2
ENTRYPOINT my-custom-ui
```
The entrypoint could then use the model via Ollama API.

### 7. Pull/Push for Entrypoint Agents
- Currently entrypoint agents can be created locally
- Need to test/verify push/pull to registry works correctly
- May need to handle entrypoint binaries (or just reference system commands)

### 8. Error Handling
- Better error messages when entrypoint command not found
- Validation of entrypoint during create (optional, warn if not found)

## Design Decisions

1. **Subprocess mode (not exec)**: Ollama stays as parent process to handle signals and cleanup

2. **No context passing initially**: Keep it simple, entrypoint handles its own config

3. **Skills/MCPs allowed**: Enables packaging assets with the agent even if entrypoint manages execution

4. **FROM optional**: Entrypoint agents don't need a model, just the runtime

5. **Prompt as argument**: User prompt is appended as argument to entrypoint command (simplest approach)
