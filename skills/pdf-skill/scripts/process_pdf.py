#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypdf",
#     "pdfplumber",
# ]
# ///
"""
PDF Processing Script for non-technical users.
Handles common PDF operations: info, text extraction, search, split, merge.

Usage: uv run scripts/process_pdf.py <filepath> <command> [args...] [--output <output_path>]
"""

import sys
import argparse
import re
from pathlib import Path


def load_pdf_pypdf(filepath):
    """Load PDF using pypdf."""
    from pypdf import PdfReader
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    try:
        return PdfReader(filepath)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        sys.exit(1)


def load_pdf_plumber(filepath):
    """Load PDF using pdfplumber (better for text/tables)."""
    import pdfplumber
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    try:
        return pdfplumber.open(filepath)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        sys.exit(1)


def parse_page_range(pages_str, max_pages):
    """Parse page range string like '1,2,3' or '1-5' or '1,3-5,7'."""
    if not pages_str:
        return list(range(1, max_pages + 1))

    pages = set()
    parts = pages_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))

    # Filter to valid range and sort
    valid_pages = sorted([p for p in pages if 1 <= p <= max_pages])
    return valid_pages


def cmd_info(args):
    """Show PDF information."""
    reader = load_pdf_pypdf(args.filepath)

    print("=" * 60)
    print("PDF INFORMATION")
    print("=" * 60)

    print(f"\nFile: {args.filepath}")
    print(f"Pages: {len(reader.pages)}")

    # File size
    path = Path(args.filepath)
    size_bytes = path.stat().st_size
    if size_bytes < 1024:
        size_str = f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    print(f"Size: {size_str}")

    # Metadata
    meta = reader.metadata
    if meta:
        print("\n" + "-" * 40)
        print("METADATA:")
        print("-" * 40)
        if meta.title:
            print(f"  Title: {meta.title}")
        if meta.author:
            print(f"  Author: {meta.author}")
        if meta.subject:
            print(f"  Subject: {meta.subject}")
        if meta.creator:
            print(f"  Creator: {meta.creator}")
        if meta.creation_date:
            print(f"  Created: {meta.creation_date}")
        if meta.modification_date:
            print(f"  Modified: {meta.modification_date}")


def cmd_text(args):
    """Extract text from PDF."""
    pdf = load_pdf_plumber(args.filepath)

    pages = parse_page_range(args.pages, len(pdf.pages))

    print("=" * 60)
    if args.pages:
        print(f"TEXT EXTRACTION (pages {args.pages})")
    else:
        print("TEXT EXTRACTION (all pages)")
    print("=" * 60)

    for page_num in pages:
        page = pdf.pages[page_num - 1]  # 0-indexed
        text = page.extract_text() or ""

        print(f"\n--- Page {page_num} ---\n")
        if text.strip():
            print(text)
        else:
            print("(No text found on this page - may be an image or scan)")

    pdf.close()


def cmd_search(args):
    """Search for text in PDF."""
    if not args.query:
        print("Error: Please provide a search query")
        sys.exit(1)

    pdf = load_pdf_plumber(args.filepath)
    query = args.query.lower()

    print("=" * 60)
    print(f"SEARCH RESULTS: '{args.query}'")
    print("=" * 60)

    total_matches = 0

    for i, page in enumerate(pdf.pages):
        page_num = i + 1
        text = page.extract_text() or ""

        # Find matches with context
        text_lower = text.lower()
        if query in text_lower:
            # Count occurrences
            count = text_lower.count(query)
            total_matches += count

            print(f"\n--- Page {page_num} ({count} match{'es' if count > 1 else ''}) ---")

            # Show context around each match
            lines = text.split('\n')
            for j, line in enumerate(lines):
                if query in line.lower():
                    # Highlight the match (uppercase)
                    highlighted = re.sub(
                        f'({re.escape(args.query)})',
                        r'>>>\1<<<',
                        line,
                        flags=re.IGNORECASE
                    )
                    print(f"  {highlighted}")

    print(f"\n{'=' * 40}")
    if total_matches == 0:
        print(f"No matches found for '{args.query}'")
    else:
        print(f"Total: {total_matches} match{'es' if total_matches > 1 else ''} found")

    pdf.close()


def cmd_tables(args):
    """Extract tables from PDF."""
    pdf = load_pdf_plumber(args.filepath)

    print("=" * 60)
    print("TABLE EXTRACTION")
    print("=" * 60)

    table_count = 0

    for i, page in enumerate(pdf.pages):
        page_num = i + 1
        tables = page.extract_tables()

        if tables:
            for j, table in enumerate(tables):
                table_count += 1
                print(f"\n--- Table {table_count} (Page {page_num}) ---\n")

                # Print as CSV-like format
                for row in table:
                    # Clean up None values
                    cleaned = [str(cell).strip() if cell else "" for cell in row]
                    print(",".join(cleaned))

    if table_count == 0:
        print("\nNo tables found in this PDF.")
        print("Note: Table extraction works best with clearly structured tables.")
    else:
        print(f"\n{'=' * 40}")
        print(f"Total: {table_count} table{'s' if table_count > 1 else ''} found")

    pdf.close()


def cmd_count(args):
    """Count words and characters in PDF."""
    pdf = load_pdf_plumber(args.filepath)

    total_chars = 0
    total_words = 0
    page_stats = []

    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        chars = len(text)
        words = len(text.split())
        total_chars += chars
        total_words += words
        page_stats.append((i + 1, words, chars))

    print("=" * 60)
    print("DOCUMENT STATISTICS")
    print("=" * 60)

    print(f"\nTotal pages: {len(pdf.pages)}")
    print(f"Total words: {total_words:,}")
    print(f"Total characters: {total_chars:,}")

    if len(pdf.pages) > 1:
        print(f"\nAverage words per page: {total_words // len(pdf.pages):,}")

        print("\n" + "-" * 40)
        print("PER-PAGE BREAKDOWN:")
        print("-" * 40)
        for page_num, words, chars in page_stats:
            print(f"  Page {page_num}: {words:,} words, {chars:,} chars")

    pdf.close()


def cmd_split(args):
    """Extract specific pages to a new PDF."""
    from pypdf import PdfReader, PdfWriter

    if not args.output:
        print("Error: Please specify output file with --output")
        sys.exit(1)

    reader = load_pdf_pypdf(args.filepath)
    pages = parse_page_range(args.pages, len(reader.pages))

    if not pages:
        print("Error: No valid pages specified")
        sys.exit(1)

    writer = PdfWriter()

    for page_num in pages:
        writer.add_page(reader.pages[page_num - 1])

    with open(args.output, 'wb') as f:
        writer.write(f)

    print(f"Extracted {len(pages)} page(s) to: {args.output}")
    print(f"Pages included: {', '.join(map(str, pages))}")


def cmd_merge(args):
    """Merge multiple PDFs into one."""
    from pypdf import PdfReader, PdfWriter

    if not args.output:
        print("Error: Please specify output file with --output")
        sys.exit(1)

    # Collect all input files
    files = [args.filepath]
    if args.query:
        files.append(args.query)
    if args.pages:
        files.append(args.pages)
    # Check for additional files in remaining args

    # Validate all files exist
    for f in files:
        if not Path(f).exists():
            print(f"Error: File not found: {f}")
            sys.exit(1)

    writer = PdfWriter()
    total_pages = 0

    for filepath in files:
        reader = PdfReader(filepath)
        for page in reader.pages:
            writer.add_page(page)
            total_pages += 1
        print(f"  Added: {filepath} ({len(reader.pages)} pages)")

    with open(args.output, 'wb') as f:
        writer.write(f)

    print(f"\nMerged {len(files)} files ({total_pages} total pages) to: {args.output}")


def main():
    parser = argparse.ArgumentParser(description='Process PDF files')
    parser.add_argument('filepath', help='Path to PDF file (or "merge" command)')
    parser.add_argument('command', nargs='?', default='info',
                        help='Command: info, text, search, tables, count, split, merge')
    parser.add_argument('query', nargs='?', help='Search query or second file for merge')
    parser.add_argument('--pages', '-p', help='Page range (e.g., "1-3" or "1,2,5")')
    parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    # Handle merge as special case (first arg is "merge")
    if args.filepath == 'merge':
        if not args.command:
            print("Error: merge requires at least 2 PDF files")
            print("Usage: process_pdf.py merge file1.pdf file2.pdf --output combined.pdf")
            sys.exit(1)
        # Shift args for merge
        args.filepath = args.command
        args.command = 'merge'

    # Run the command
    commands = {
        'info': cmd_info,
        'text': cmd_text,
        'search': cmd_search,
        'tables': cmd_tables,
        'count': cmd_count,
        'split': cmd_split,
        'merge': cmd_merge,
    }

    if args.command not in commands:
        print(f"Error: Unknown command '{args.command}'")
        print(f"Available commands: {', '.join(commands.keys())}")
        sys.exit(1)

    commands[args.command](args)


if __name__ == "__main__":
    main()
