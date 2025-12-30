#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pandas",
#     "openpyxl",
# ]
# ///
"""
Excel/CSV Data Processing Script for non-technical users.
Handles common data operations: summary, statistics, filtering, duplicates, etc.

Usage: uv run scripts/process_data.py <filepath> <command> [args...] [--output <output_path>]
"""

import sys
import argparse
import pandas as pd
from pathlib import Path


def load_file(filepath):
    """Load Excel or CSV file into a DataFrame."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    suffix = path.suffix.lower()
    try:
        if suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
        elif suffix == '.csv':
            df = pd.read_csv(filepath)
        else:
            # Try CSV as default
            df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def save_output(df, output_path):
    """Save DataFrame to file."""
    path = Path(output_path)
    suffix = path.suffix.lower()
    try:
        if suffix in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
        else:
            df.to_csv(output_path, index=False)
        print(f"\nSaved {len(df)} rows to: {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")


def cmd_summary(df, args):
    """Show overview of the data."""
    print("=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\n" + "-" * 40)
    print("COLUMNS:")
    print("-" * 40)
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()

        type_label = "text" if dtype == 'object' else ("number" if dtype in ['int64', 'float64'] else str(dtype))
        null_info = f" ({null_count} missing)" if null_count > 0 else ""
        print(f"  - {col}: {type_label}{null_info}")

    print("\n" + "-" * 40)
    print("SAMPLE DATA (first 5 rows):")
    print("-" * 40)
    print(df.head().to_string())

    return df


def cmd_stats(df, args):
    """Show statistics for a column."""
    if not args.column:
        print("Error: Please specify a column name")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    col = args.column
    if col not in df.columns:
        print(f"Error: Column '{col}' not found")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    print(f"\nSTATISTICS FOR: {col}")
    print("=" * 40)

    series = df[col]
    print(f"Total values: {len(series):,}")
    print(f"Non-empty: {series.notna().sum():,}")
    print(f"Empty/missing: {series.isna().sum():,}")
    print(f"Unique values: {series.nunique():,}")

    if pd.api.types.is_numeric_dtype(series):
        print(f"\nNumeric Statistics:")
        print(f"  Sum: {series.sum():,.2f}")
        print(f"  Average: {series.mean():,.2f}")
        print(f"  Median: {series.median():,.2f}")
        print(f"  Min: {series.min():,.2f}")
        print(f"  Max: {series.max():,.2f}")
        print(f"  Std Dev: {series.std():,.2f}")
    else:
        print(f"\nMost common values:")
        for val, count in series.value_counts().head(10).items():
            pct = count / len(series) * 100
            print(f"  {val}: {count:,} ({pct:.1f}%)")

    return df


def cmd_duplicates(df, args):
    """Find duplicate rows."""
    col = args.column

    if col:
        if col not in df.columns:
            print(f"Error: Column '{col}' not found")
            print(f"Available columns: {', '.join(df.columns)}")
            sys.exit(1)
        dups = df[df.duplicated(subset=[col], keep=False)]
        print(f"\nDUPLICATES IN COLUMN: {col}")
    else:
        dups = df[df.duplicated(keep=False)]
        print(f"\nDUPLICATE ROWS (all columns)")

    print("=" * 40)

    if len(dups) == 0:
        print("No duplicates found!")
    else:
        print(f"Found {len(dups):,} duplicate rows")
        print("\nDuplicate entries:")
        print(dups.to_string())

    return dups


def cmd_filter(df, args):
    """Filter rows based on condition."""
    if not args.column or not args.operator or args.value is None:
        print("Error: Filter requires column, operator, and value")
        print("Usage: filter <column> <operator> <value>")
        print("Operators: equals, not_equals, contains, greater, less")
        sys.exit(1)

    col = args.column
    op = args.operator.lower()
    val = args.value

    if col not in df.columns:
        print(f"Error: Column '{col}' not found")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    original_count = len(df)

    if op == 'equals':
        if val == '':
            result = df[df[col].isna() | (df[col] == '')]
        else:
            # Try numeric comparison if possible
            try:
                result = df[df[col] == float(val)]
            except:
                result = df[df[col].astype(str).str.lower() == val.lower()]
    elif op == 'not_equals':
        try:
            result = df[df[col] != float(val)]
        except:
            result = df[df[col].astype(str).str.lower() != val.lower()]
    elif op == 'contains':
        result = df[df[col].astype(str).str.lower().str.contains(val.lower(), na=False)]
    elif op == 'greater':
        try:
            result = df[pd.to_numeric(df[col], errors='coerce') > float(val)]
        except:
            print(f"Error: Cannot compare '{col}' as numbers")
            sys.exit(1)
    elif op == 'less':
        try:
            result = df[pd.to_numeric(df[col], errors='coerce') < float(val)]
        except:
            print(f"Error: Cannot compare '{col}' as numbers")
            sys.exit(1)
    else:
        print(f"Error: Unknown operator '{op}'")
        print("Valid operators: equals, not_equals, contains, greater, less")
        sys.exit(1)

    print(f"\nFILTER: {col} {op} '{val}'")
    print("=" * 40)
    print(f"Found {len(result):,} matching rows (out of {original_count:,})")

    if len(result) > 0:
        print("\nResults:")
        if len(result) > 50:
            print(result.head(50).to_string())
            print(f"\n... and {len(result) - 50} more rows")
        else:
            print(result.to_string())

    return result


def cmd_sort(df, args):
    """Sort data by column."""
    if not args.column:
        print("Error: Please specify a column to sort by")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    col = args.column
    if col not in df.columns:
        print(f"Error: Column '{col}' not found")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    ascending = args.order != 'desc'
    result = df.sort_values(by=col, ascending=ascending)

    order_label = "ascending" if ascending else "descending"
    print(f"\nSORTED BY: {col} ({order_label})")
    print("=" * 40)

    if len(result) > 50:
        print(result.head(50).to_string())
        print(f"\n... and {len(result) - 50} more rows")
    else:
        print(result.to_string())

    return result


def cmd_count(df, args):
    """Count values in a column."""
    if not args.column:
        print("Error: Please specify a column to count")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    col = args.column
    if col not in df.columns:
        print(f"Error: Column '{col}' not found")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    counts = df[col].value_counts()

    print(f"\nVALUE COUNTS FOR: {col}")
    print("=" * 40)
    print(f"Total unique values: {len(counts):,}")
    print()

    for val, count in counts.items():
        pct = count / len(df) * 100
        print(f"  {val}: {count:,} ({pct:.1f}%)")

    # Return as DataFrame for potential export
    return counts.reset_index().rename(columns={'index': col, col: 'count'})


def cmd_top(df, args):
    """Get top N rows by column value."""
    if not args.column:
        print("Error: Please specify a column")
        sys.exit(1)

    col = args.column
    # Number can be in args.operator position due to positional parsing
    n = int(args.number) if args.number else (int(args.operator) if args.operator and args.operator.isdigit() else 10)

    if col not in df.columns:
        print(f"Error: Column '{col}' not found")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    result = df.nlargest(n, col)

    print(f"\nTOP {n} BY: {col}")
    print("=" * 40)
    print(result.to_string())

    return result


def cmd_bottom(df, args):
    """Get bottom N rows by column value."""
    if not args.column:
        print("Error: Please specify a column")
        sys.exit(1)

    col = args.column
    # Number can be in args.operator position due to positional parsing
    n = int(args.number) if args.number else (int(args.operator) if args.operator and args.operator.isdigit() else 10)

    if col not in df.columns:
        print(f"Error: Column '{col}' not found")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    result = df.nsmallest(n, col)

    print(f"\nBOTTOM {n} BY: {col}")
    print("=" * 40)
    print(result.to_string())

    return result


def cmd_missing(df, args):
    """Find rows with missing values."""
    print("\nMISSING VALUE ANALYSIS")
    print("=" * 40)

    # Summary by column
    print("\nMissing values per column:")
    for col in df.columns:
        missing = df[col].isna().sum()
        if missing > 0:
            pct = missing / len(df) * 100
            print(f"  {col}: {missing:,} ({pct:.1f}%)")

    total_missing = df.isna().sum().sum()
    if total_missing == 0:
        print("  No missing values found!")
        return df

    # Rows with any missing values
    rows_with_missing = df[df.isna().any(axis=1)]
    print(f"\nRows with missing values: {len(rows_with_missing):,}")

    if len(rows_with_missing) > 0 and len(rows_with_missing) <= 50:
        print("\nRows with missing data:")
        print(rows_with_missing.to_string())
    elif len(rows_with_missing) > 50:
        print("\nFirst 50 rows with missing data:")
        print(rows_with_missing.head(50).to_string())
        print(f"\n... and {len(rows_with_missing) - 50} more rows")

    return rows_with_missing


def main():
    parser = argparse.ArgumentParser(description='Process Excel/CSV data')
    parser.add_argument('filepath', help='Path to Excel or CSV file')
    parser.add_argument('command', choices=['summary', 'stats', 'duplicates', 'filter', 'sort', 'count', 'top', 'bottom', 'missing'],
                        help='Command to run')
    parser.add_argument('column', nargs='?', help='Column name (for stats, filter, sort, count, top, bottom, duplicates)')
    parser.add_argument('operator', nargs='?', help='Operator for filter (equals, contains, greater, less, not_equals)')
    parser.add_argument('value', nargs='?', help='Value for filter')
    parser.add_argument('number', nargs='?', help='Number for top/bottom')
    parser.add_argument('--order', choices=['asc', 'desc'], default='asc', help='Sort order')
    parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    # Load the file
    df = load_file(args.filepath)

    # Run the command
    commands = {
        'summary': cmd_summary,
        'stats': cmd_stats,
        'duplicates': cmd_duplicates,
        'filter': cmd_filter,
        'sort': cmd_sort,
        'count': cmd_count,
        'top': cmd_top,
        'bottom': cmd_bottom,
        'missing': cmd_missing,
    }

    result = commands[args.command](df, args)

    # Save output if requested
    if args.output and isinstance(result, pd.DataFrame):
        save_output(result, args.output)


if __name__ == "__main__":
    main()
