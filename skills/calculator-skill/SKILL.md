---
name: calculator-skill
description: A skill for performing mathematical calculations using a Python script. Use when the user asks to calculate, compute, or do math operations.
---

# Calculator Skill

## Purpose

This skill performs mathematical calculations using a bundled Python script for accuracy.

## When to use

- The user asks to calculate something
- The user wants to do math (add, subtract, multiply, divide)
- The user asks about percentages or conversions
- Any arithmetic or mathematical operation is needed

## Instructions

1. When the user asks for a calculation, use the `run_skill_script` tool to execute the calculation script.
2. Call the script like this: `python3 scripts/calculate.py "<expression>"`
3. Return the result from the script output to the user.

## Examples

For "What is 25 * 4?":
- Call: `run_skill_script` with skill="calculator-skill" and command="python3 scripts/calculate.py '25 * 4'"
- Output: "25 * 4 = 100"

For "Calculate 15% of 200":
- Call: `run_skill_script` with skill="calculator-skill" and command="python3 scripts/calculate.py '15/100 * 200'"
- Output: "15/100 * 200 = 30.0"

For "Add 123 and 456":
- Call: `run_skill_script` with skill="calculator-skill" and command="python3 scripts/calculate.py '123 + 456'"
- Output: "123 + 456 = 579"
