---
name: pdf-skill
description: Help users work with PDF files - extract text, get document info, search content, extract pages, and merge PDFs. Use when the user mentions PDF, document extraction, or wants to read/combine PDF files.
---

# PDF Processing Skill

## Purpose

This skill helps users work with PDF files without needing technical knowledge. It can extract text, search for content, get document information, split and merge PDFs.

## When to use

- User uploads or mentions a PDF file
- User wants to extract text from a document
- User asks "what's in this PDF" or similar
- User wants to search for something in a PDF
- User wants to combine or split PDF files
- User asks about page counts or document info

## Instructions

### Step 1: Understand the document first

When a user provides a PDF, start by getting info about it:

```
uv run scripts/process_pdf.py "<filepath>" info
```

This shows:
- Number of pages
- Document metadata (title, author, etc.)
- File size

### Step 2: Perform the requested operation

Based on what the user asks, use the appropriate command:

**Extract all text:**
```
uv run scripts/process_pdf.py "<filepath>" text
```
Extracts text from all pages.

**Extract text from specific pages:**
```
uv run scripts/process_pdf.py "<filepath>" text --pages 1,2,3
uv run scripts/process_pdf.py "<filepath>" text --pages 1-5
```

**Search for text:**
```
uv run scripts/process_pdf.py "<filepath>" search "<query>"
```
Finds all occurrences and shows surrounding context.

**Extract tables:**
```
uv run scripts/process_pdf.py "<filepath>" tables
```
Attempts to extract tables from the PDF as CSV format.

**Extract specific pages to new PDF:**
```
uv run scripts/process_pdf.py "<filepath>" split --pages 1-3 --output "extracted.pdf"
```

**Merge multiple PDFs:**
```
uv run scripts/process_pdf.py merge "<file1.pdf>" "<file2.pdf>" --output "combined.pdf"
```

**Get word/character count:**
```
uv run scripts/process_pdf.py "<filepath>" count
```

## Examples

**User: "What's in this PDF?"**
Run: `uv run scripts/process_pdf.py "document.pdf" info`
Then: `uv run scripts/process_pdf.py "document.pdf" text --pages 1` (for first page preview)

**User: "Extract the text from this document"**
Run: `uv run scripts/process_pdf.py "document.pdf" text`

**User: "Find all mentions of 'invoice' in this PDF"**
Run: `uv run scripts/process_pdf.py "document.pdf" search "invoice"`

**User: "How many pages is this?"**
Run: `uv run scripts/process_pdf.py "document.pdf" info`

**User: "Get me just pages 5-10"**
Run: `uv run scripts/process_pdf.py "document.pdf" split --pages 5-10 --output "pages_5_10.pdf"`

**User: "Combine these two PDFs"**
Run: `uv run scripts/process_pdf.py merge "doc1.pdf" "doc2.pdf" --output "combined.pdf"`

**User: "Are there any tables in this PDF?"**
Run: `uv run scripts/process_pdf.py "document.pdf" tables`

## Tips for helping non-technical users

1. Always start with `info` to understand what you're working with
2. For long documents, extract just the first page first to preview
3. If text extraction looks garbled, the PDF might be scanned images (OCR needed)
4. Explain what you found in plain language
5. If tables don't extract well, mention that PDF tables can be tricky
