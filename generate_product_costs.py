"""Generate a synthetic supplier-cost table for the top N stock codes by revenue.

The transactions in Online Retail II are real; no public source publishes supplier
cost, so this file fabricates a plausible cost layer. It deliberately covers only
the top N codes by revenue -- every other stock code legitimately has no cost, and
that gap is what the dashboard's "revenue without cost data" warning reports on.

Descriptions follow the same canonical-name rule as reports/analysis_report.md
(section 7.9), so this file and the Power Query model agree on product names.

Costs are drawn from a fixed seed so re-running produces identical output.
"""

from __future__ import annotations

import argparse
import random
import re
from pathlib import Path

import pandas as pd

# A real product code is 5 digits with an optional short letter suffix (85123A).
# Anything else is postage, bank charges, manual adjustments and friends (7.8).
PRODUCT_CODE = re.compile(r"^\d{5}[A-Za-z]{0,2}$")

# 7.9: if one wording dominates a code this heavily, the others are stray
# operational notes ("found", "wrongly coded") rather than alternate names.
MODAL_SHARE_THRESHOLD = 0.95

SUPPLIERS = (
    "Halden & Rowe",
    "Marchetti Imports",
    "Brightwater Supply",
    "Kestrel Wholesale",
    "Pennine Goods",
)

# Giftware wholesale: cost sits at roughly 40-60% of the selling price.
MIN_COST_RATIO = 0.40
MAX_COST_RATIO = 0.60

SEED = 20091201
VALID_FROM = "2009-12-01"


def load_monthly_files(directories: list[Path]) -> pd.DataFrame:
    files: list[Path] = []
    for directory in directories:
        if directory.is_dir():
            files.extend(sorted(directory.glob("*.csv")))
            files.extend(sorted(directory.glob("*.xlsx")))
    files = [f for f in files if f.name != "product_costs.csv"]
    if not files:
        raise SystemExit(f"No monthly files found in: {', '.join(map(str, directories))}")

    frames = []
    for path in files:
        reader = pd.read_csv if path.suffix.lower() == ".csv" else pd.read_excel
        frames.append(reader(path))
    print(f"Read {len(files)} monthly files.")

    rows = pd.concat(frames, ignore_index=True)
    rows["StockCode"] = rows["StockCode"].astype(str).str.strip()
    rows["InvoiceDate"] = pd.to_datetime(rows["InvoiceDate"])
    return rows.loc[rows["StockCode"].str.match(PRODUCT_CODE)].copy()


def canonical_descriptions(products: pd.DataFrame) -> pd.Series:
    """One name per stock code, following section 7.9's two-branch rule.

    Text is compared as-is (no trimming or case folding) so this matches what
    Power Query will do on the same data.
    """
    named = products.dropna(subset=["Description"]).copy()
    named["Description"] = named["Description"].astype(str)

    counts = (
        named.groupby(["StockCode", "Description"]).size().rename("n").reset_index()
    )
    totals = counts.groupby("StockCode")["n"].sum().rename("total")

    # Ties on n are broken by whichever wording sorts first -- rare, and the two
    # wordings are near-identical by definition when it happens.
    modal = (
        counts.sort_values(["StockCode", "n", "Description"], ascending=[True, False, True])
        .drop_duplicates("StockCode")
        .set_index("StockCode")
        .join(totals)
    )
    modal["share"] = modal["n"] / modal["total"]

    latest = (
        named.sort_values("InvoiceDate")
        .drop_duplicates("StockCode", keep="last")
        .set_index("StockCode")["Description"]
    )

    dominant = modal["share"] >= MODAL_SHARE_THRESHOLD
    chosen = modal["Description"].where(dominant, latest.reindex(modal.index))

    renamed = int((~dominant).sum())
    print(
        f"{len(modal):,} product codes named: "
        f"{len(modal) - renamed:,} by modal wording, {renamed:,} by most recent wording."
    )
    return chosen.rename("description")


def top_products(products: pd.DataFrame, limit: int) -> pd.DataFrame:
    sales = products.loc[(products["Quantity"] > 0) & (products["Price"] > 0)].copy()
    sales["Revenue"] = sales["Quantity"] * sales["Price"]

    # Median price, not mean: prices drift over two years and the odd outlier
    # would put "typical price" somewhere no customer ever paid.
    summary = sales.groupby("StockCode").agg(
        revenue=("Revenue", "sum"),
        typical_price=("Price", "median"),
    )

    summary = summary.join(canonical_descriptions(products))
    return summary.sort_values("revenue", ascending=False).head(limit)


def build_cost_table(products: pd.DataFrame) -> pd.DataFrame:
    rng = random.Random(SEED)
    records = []
    for stock_code, row in products.iterrows():
        ratio = rng.uniform(MIN_COST_RATIO, MAX_COST_RATIO)
        cost = round(float(row["typical_price"]) * ratio, 2)
        records.append(
            {
                "stock_code": stock_code,
                "description": row["description"],
                "cost_per_unit": max(cost, 0.01),
                "supplier": rng.choice(SUPPLIERS),
                "valid_from": VALID_FROM,
            }
        )
    return pd.DataFrame.from_records(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--archive-dir", type=Path, default=Path("archive"))
    parser.add_argument("--output", type=Path, default=Path("data/reference/product_costs.csv"))
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    products = load_monthly_files([args.raw_dir, args.archive_dir])
    top = top_products(products, args.limit)
    costs = build_cost_table(top)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    costs.to_csv(args.output, index=False)

    print(f"Wrote {len(costs)} rows to {args.output}")
    print(f"Top {args.limit} codes cover GBP {top['revenue'].sum():,.0f} of product revenue.")
    print(costs.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
