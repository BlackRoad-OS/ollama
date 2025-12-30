---
name: excel-skill
description: Help non-technical users process Excel and CSV data - summarize spreadsheets, find duplicates, filter rows, calculate statistics, and clean up data. Use when the user mentions Excel, spreadsheet, CSV, or asks about their data.
---

# Excel Data Processing Skill

## Purpose

This skill helps users work with Excel (.xlsx) and CSV files without needing technical knowledge. It can summarize data, find problems, answer questions about the data, and perform common cleanup tasks.

## When to use

- User uploads or mentions an Excel or CSV file
- User wants to understand what's in their data
- User asks about duplicates, missing values, or data quality
- User wants to filter, sort, or summarize data
- User asks questions like "how many", "what's the average", "show me the top 10"

## Instructions

### Step 1: Understand the data first

When a user provides a file, ALWAYS start by running a summary to understand what you're working with:

```
uv run scripts/process_data.py "<filepath>" summary
```

This shows:
- Number of rows and columns
- Column names and their data types
- Sample of the data
- Missing value counts

### Step 2: Answer their question

Based on what the user asks, use the appropriate command:

**Get statistics for a column:**
```
uv run scripts/process_data.py "<filepath>" stats "<column_name>"
```
Shows count, average, min, max, and common values.

**Find duplicate rows:**
```
uv run scripts/process_data.py "<filepath>" duplicates
```
Or check duplicates in specific columns:
```
uv run scripts/process_data.py "<filepath>" duplicates "<column_name>"
```

**Filter rows:**
```
uv run scripts/process_data.py "<filepath>" filter "<column>" "<operator>" "<value>"
```
Operators: equals, contains, greater, less, not_equals
Examples:
- `filter "Status" "equals" "Active"`
- `filter "Amount" "greater" "1000"`
- `filter "Name" "contains" "Smith"`

**Sort data:**
```
uv run scripts/process_data.py "<filepath>" sort "<column>" [asc|desc]
```

**Count values in a column:**
```
uv run scripts/process_data.py "<filepath>" count "<column_name>"
```
Shows how many times each value appears.

**Get top/bottom rows:**
```
uv run scripts/process_data.py "<filepath>" top "<column>" <number>
uv run scripts/process_data.py "<filepath>" bottom "<column>" <number>
```

**Find missing values:**
```
uv run scripts/process_data.py "<filepath>" missing
```

**Export filtered/processed data:**
Add `--output "<new_filepath>"` to any command to save results.

## Examples

**User: "What's in this spreadsheet?"**
Run: `uv run scripts/process_data.py "sales.xlsx" summary`

**User: "Are there any duplicate entries?"**
Run: `uv run scripts/process_data.py "sales.xlsx" duplicates`

**User: "How many sales per region?"**
Run: `uv run scripts/process_data.py "sales.xlsx" count "Region"`

**User: "Show me orders over $500"**
Run: `uv run scripts/process_data.py "orders.csv" filter "Amount" "greater" "500"`

**User: "What's the average order value?"**
Run: `uv run scripts/process_data.py "orders.csv" stats "Amount"`

**User: "Find all rows with missing email addresses"**
Run: `uv run scripts/process_data.py "contacts.xlsx" filter "Email" "equals" ""`

**User: "Show me the top 10 customers by revenue"**
Run: `uv run scripts/process_data.py "customers.csv" top "Revenue" 10`

## Tips for helping non-technical users

1. Always explain what you found in plain language
2. If there are issues (duplicates, missing data), explain why it matters
3. Offer to help fix problems you discover
4. When showing numbers, provide context ("this is high/low compared to...")
5. Ask clarifying questions if the column names are ambiguous
