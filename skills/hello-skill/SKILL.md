---
name: hello-skill
description: Simple test skill for verifying Agent Skills integration in ollama run. Use when the user asks to test skills, sample skills, or wants a quick hello workflow.
---

# Hello Skill

## Purpose

This is a minimal skill to validate that skills load correctly and that tool calls can read additional files.

## When to use

- The user asks to test skills integration.
- The user wants a simple example skill.

## Instructions

1. Reply with a short greeting that mentions the skill name.
2. If you need a template greeting, read `references/GREETING.md` using the `read_skill_file` tool.

## Example

User: "Test the skills feature."
Assistant: "Hello from hello-skill."
