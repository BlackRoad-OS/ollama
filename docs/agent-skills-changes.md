# Agent Skills Feature - Implementation Summary

This document summarizes all changes made to implement agent skills in Ollama, enabling `ollama run <agent>` with skill-based capabilities.

## Overview

Agents are models with attached skills. Skills are directories containing a `SKILL.md` file with instructions and optional executable scripts. When an agent runs, skills are loaded and injected into the system prompt, and the model can execute scripts via tool calls.

## Files Changed

### 1. `cmd/skills.go` (NEW FILE)

Core skills implementation:

```go
// Key types
type skillMetadata struct {
    Name        string `yaml:"name"`
    Description string `yaml:"description"`
}

type skillDefinition struct {
    Name        string
    Description string
    Content     string  // SKILL.md body content
    Dir         string  // Absolute path to skill directory
    SkillPath   string  // Absolute path to SKILL.md
}

type skillCatalog struct {
    Skills []skillDefinition
    byName map[string]skillDefinition
}
```

**Key functions:**
- `loadSkills(paths []string)` - Walks skill directories, parses SKILL.md files
- `parseSkillFile(path, skillDir)` - Extracts YAML frontmatter and body content
- `SystemPrompt()` - Generates system prompt with skill instructions
- `Tools()` - Returns `run_skill_script` and `read_skill_file` tools
- `RunToolCall(call)` - Executes tool calls from the model
- `runSkillScript(skillDir, command)` - Executes shell commands in skill directory

**Tools provided to model:**
| Tool | Description |
|------|-------------|
| `run_skill_script` | Execute a script in a skill's directory |
| `read_skill_file` | Read a file from a skill's directory |

**Security note:** `runSkillScript` has documented limitations (no sandboxing, no path validation). See the function's doc comment for details.

---

### 2. `cmd/cmd.go`

**Changes to `runOptions` struct:**
```go
type runOptions struct {
    // ... existing fields ...
    IsAgent   bool
    AgentType string
    Skills    []string
}
```

**Agent detection in `RunHandler`** (~line 497-503):
```go
// Check if this is an agent
isAgent := info.AgentType != "" || len(info.Skills) > 0
if isAgent {
    opts.IsAgent = true
    opts.AgentType = info.AgentType
    opts.Skills = info.Skills
}
```

**Route agents to chat API** (~line 557-562):
```go
// For agents, use chat API even in non-interactive mode to support tools
if opts.IsAgent {
    opts.Messages = append(opts.Messages, api.Message{Role: "user", Content: opts.Prompt})
    _, err := chat(cmd, opts)
    return err
}
```

**Skills loading in `chat` function** (~line 1347-1361):
```go
var skillsCatalog *skillCatalog
if opts.IsAgent && len(opts.Skills) > 0 {
    skillsCatalog, err = loadSkills(opts.Skills)
    // ... error handling ...
    // Print loaded skills
    fmt.Fprintf(os.Stderr, "Loaded skills: %s\n", strings.Join(skillNames, ", "))
}
```

**System prompt injection** (~line 1448-1455):
- Skills system prompt is prepended to messages

**Tool execution** (~line 1497-1533):
- Executes pending tool calls via `skillsCatalog.RunToolCall()`
- Displays script execution and output to terminal

---

### 3. `parser/parser.go`

**New valid commands** in `isValidCommand()`:
```go
case "from", "license", "template", "system", "adapter", "renderer",
     "parser", "parameter", "message", "requires", "skill", "agent_type":
```

**Command handling in `CreateRequest()`**:
```go
case "skill":
    skills = append(skills, c.Args)
case "agent_type":
    req.AgentType = c.Args
```

**Underscore support in command names** (~line 545):
```go
case isAlpha(r), r == '_':
    return stateName, r, nil
```

---

### 4. `api/types.go`

**CreateRequest additions** (~line 560-564):
```go
// Skills is a list of skill directories for the agent
Skills []string `json:"skills,omitempty"`

// AgentType defines the type of agent (e.g., "conversational", "task-based")
AgentType string `json:"agent_type,omitempty"`
```

**ShowResponse additions** (~line 633-637):
```go
// Skills loaded for this agent
Skills []string `json:"skills,omitempty"`

// AgentType for this agent
AgentType string `json:"agent_type,omitempty"`
```

---

### 5. `types/model/config.go`

**ConfigV2 additions**:
```go
type ConfigV2 struct {
    // ... existing fields ...

    // Agent-specific fields
    Skills    []string `json:"skills,omitempty"`
    AgentType string   `json:"agent_type,omitempty"`
}
```

---

### 6. `server/create.go`

**Store agent fields** (~line 65-66):
```go
config.Skills = r.Skills
config.AgentType = r.AgentType
```

---

### 7. `server/routes.go`

**Return agent fields in ShowResponse** (~line 1107):
```go
resp := &api.ShowResponse{
    // ... existing fields ...
    Skills:    m.Config.Skills,
    AgentType: m.Config.AgentType,
}
```

---

### 8. `envconfig/config.go`

**Environment variable support**:
```go
func Skills() []string {
    raw := strings.TrimSpace(Var("OLLAMA_SKILLS"))
    if raw == "" {
        return []string{}
    }
    return strings.Split(raw, ",")
}
```

---

## Agentfile Format

Agentfiles use the same syntax as Modelfiles with additional commands:

```dockerfile
FROM gpt-oss:20b

AGENT_TYPE conversational
SKILL /path/to/skills/directory

SYSTEM You are a helpful assistant.

PARAMETER temperature 0.3
PARAMETER top_p 0.9
```

| Command | Description |
|---------|-------------|
| `SKILL` | Path to a directory containing skill subdirectories |
| `AGENT_TYPE` | Type of agent (e.g., "conversational") |

---

## SKILL.md Format

Each skill is a directory with a `SKILL.md` file:

```
calculator-skill/
├── SKILL.md
└── scripts/
    └── calculate.py
```

**SKILL.md structure:**
```markdown
---
name: calculator-skill
description: A skill for performing calculations.
---

# Calculator Skill

## Instructions

1. Use `run_skill_script` to execute calculations
2. Call: `python3 scripts/calculate.py '<expression>'`

## Examples

For "What is 25 * 4?":
- Call: run_skill_script with skill="calculator-skill" and command="python3 scripts/calculate.py '25 * 4'"
```

**Requirements:**
- `name` must match directory name
- `name` must be lowercase alphanumeric with hyphens only
- `name` max 64 characters
- `description` required, max 1024 characters

---

## Usage

```bash
# Create an agent
ollama create math-agent -f math-agent.Agentfile

# Run the agent
ollama run math-agent "What is 25 * 4?"

# Output:
# Loaded skills: calculator-skill
# Running script in calculator-skill: python3 scripts/calculate.py '25 * 4'
# Output:
# 25 * 4 = 100
```

---

## Flow Diagram

```
1. ollama run math-agent "query"
       │
       ▼
2. RunHandler detects agent (AgentType or Skills present)
       │
       ▼
3. Routes to chat() instead of generate()
       │
       ▼
4. loadSkills() parses SKILL.md files
       │
       ▼
5. SystemPrompt() injects skill instructions
       │
       ▼
6. Tools() provides run_skill_script, read_skill_file
       │
       ▼
7. Model generates response (may include tool calls)
       │
       ▼
8. RunToolCall() executes scripts, returns output
       │
       ▼
9. Display results to user
```

---

## Security Considerations

The `runSkillScript` function has known limitations documented in the code:

- No sandboxing (commands run with user permissions)
- No path validation (model can run any command)
- Shell injection risk (`sh -c` is used)
- No executable allowlist
- No environment isolation

**Potential improvements** (documented as TODOs):
- Restrict to skill directory paths only
- Allowlist executables (python3, node, bash)
- Use sandboxing (Docker, nsjail, seccomp)
- Require explicit script registration in SKILL.md
