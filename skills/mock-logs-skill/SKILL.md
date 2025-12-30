---
name: mock-logs
description: Outputs mock log entries for testing and demonstration purposes
---

# Mock Logs Skill

## Purpose

This skill generates mock log entries for testing, debugging, and demonstration purposes.

## When to use

- User asks to generate sample logs
- User wants to see example log output
- User needs test data for log parsing
- User asks about log formats

## Instructions

1. When the user asks for mock logs, use the `run_skill_script` tool
2. Call: `python3 scripts/generate_logs.py [count] [level]`
   - count: Number of log entries (default: 5)
   - level: Log level filter - info, warn, error, debug, or all (default: all)
3. Return the generated logs to the user

## Examples

For "Generate some sample logs":
- Call: `run_skill_script` with skill="mock-logs" and command="python3 scripts/generate_logs.py 5"

For "Show me 10 error logs":
- Call: `run_skill_script` with skill="mock-logs" and command="python3 scripts/generate_logs.py 10 error"

For "Generate debug logs":
- Call: `run_skill_script` with skill="mock-logs" and command="python3 scripts/generate_logs.py 5 debug"
