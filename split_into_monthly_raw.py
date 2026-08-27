from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

SHEET_NAMES = ("Year 2009-2010", "Year 2010-2011")
FILENAME_PREFIX = "Retail"


def load_combined(input_path: Path) -> pd.DataFrame:
    sheets = pd.read_excel(input_path, sheet_name=list(SHEET_NAMES))
    frames = []
    for sheet_name, frame in sheets.items():
        frame = frame.copy()
        frame["SourceSheet"] = sheet_name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def drop_sheet_overlap(combined: pd.DataFrame) -> pd.DataFrame:
    sheet_counts = combined.groupby("Invoice")["SourceSheet"].nunique()
    overlapping_invoices = sheet_counts[sheet_counts > 1].index
    is_stale_overlap_copy = combined["Invoice"].isin(overlapping_invoices) & (
        combined["SourceSheet"] == "Year 2009-2010"
    )
    print(
        f"Dropped {int(is_stale_overlap_copy.sum()):,} rows that were the Year 2009-2010 copy "
        "of an overlapping invoice."
    )
    kept = combined.loc[~is_stale_overlap_copy].drop(columns="SourceSheet")
    # Customer ID has missing values so pandas reads it as float64; without this it would
    # write as "17850.0" instead of "17850" once it hits CSV (Excel's numeric formatting
    # hid the trailing ".0", CSV has no such formatting layer).
    kept["Customer ID"] = kept["Customer ID"].astype("Int64")
    return kept


def split_by_month(rows: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    month_key = pd.to_datetime(rows["InvoiceDate"]).dt.strftime("%Y-%m")
    for month, month_rows in rows.groupby(month_key):
        out_path = output_dir / f"{FILENAME_PREFIX}_{month}.csv"
        month_rows.to_csv(out_path, index=False)
        print(f"{out_path.name}: {len(month_rows):,} rows")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Split the merged Online Retail II workbook into one monthly file per "
            "InvoiceDate month, resolving the Year 2009-2010 / Year 2010-2011 sheet "
            "overlap first. Output mimics the monthly client exports the production "
            "pipeline will receive, seeding data/raw/ for the self-refreshing report."
        )
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        default=Path("data/online_retail_II.xlsx"),
        help="Path to the merged two-sheet workbook.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory to write monthly CSV files into.",
    )
    args = parser.parse_args()

    combined = load_combined(args.input_path)
    deduped = drop_sheet_overlap(combined)
    split_by_month(deduped, args.output_dir)


if __name__ == "__main__":
    main()
