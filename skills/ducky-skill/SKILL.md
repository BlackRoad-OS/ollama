---
name: ducky
description: Run DuckY CLI tool for processing directories with AI models
---

# DuckY Skill

## Purpose

This skill provides access to the DuckY CLI tool, which processes directories using AI models.

## When to use

- User asks to run ducky on a directory
- User wants to process files with ducky
- User asks about ducky or wants to use ducky features
- User wants to poll a crumb

## Instructions

1. When the user asks to run ducky, use the `run_skill_script` tool
2. Call: `./scripts/run_ducky.sh [args]`
   - `-d <directory>` - Directory to process
   - `-m <model>` - Model to use
   - `-l` - Run locally with Ollama
   - `--poll <crumb>` - Poll a specific crumb
   - `-i <seconds>` - Polling interval

## Examples

For "Run ducky on the current directory":
- Call: `run_skill_script` with skill="ducky" and command="./scripts/run_ducky.sh -d . -l"

For "Run ducky locally on src folder":
- Call: `run_skill_script` with skill="ducky" and command="./scripts/run_ducky.sh -d src -l"

For "Poll the build crumb every 30 seconds":
- Call: `run_skill_script` with skill="ducky" and command="./scripts/run_ducky.sh --poll build -i 30 -l"
