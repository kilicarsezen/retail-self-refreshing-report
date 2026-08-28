# Retail self-refreshing report

A small end-to-end retail analytics pipeline built on the [Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) dataset: messy transaction-level exports → documented cleaning decisions → a star-schema Power BI model → a two-page report that's designed to refresh itself as new monthly data lands, not be rebuilt every time.

It's a portfolio piece, so the point isn't just the finished report — it's the trail showing how it got there: real data-quality findings, real decisions (and the reasoning behind them), and a build log of what actually happened putting it together, mistakes included.

## The pipeline, in order

```
data/online_retail_II.xlsx           the historical source: two overlapping yearly sheets
        │
        ▼
explore_retail.ipynb                 exploration: find every data-quality issue, decide
        │                            what to do about it, document why (→ analysis_report.md)
        ▼
power_query_cleaning_guide.md        those decisions turned into a production spec:
        │                            exact Power Query steps, ready to build
        ▼
split_into_monthly_raw.py            seeds data/raw/ with one CSV per month, mimicking
        │                            the client's real monthly export shape
        ▼
generate_product_costs.py            fabricates a synthetic supplier-cost layer (no real
        │                            cost data exists for this dataset) for margin analysis
        ▼
reports/RetailDemo.pbip              the Power BI model + report: star schema, DAX
                                      measures, two report pages, built to refresh on
                                      its own when a new monthly CSV lands in data/raw/
```

Each stage hands the next one something concrete — not just data, but a *decision*. The notebook doesn't clean anything; it figures out what "clean" should mean and why, and writes that down. The guide doesn't analyze anything; it turns those decisions into exact steps someone (or something) can build without re-litigating them. Nothing downstream re-derives a decision an upstream stage already made.

## What's in each file

| Path | What it is |
|---|---|
| `explore_retail.ipynb` | The exploration notebook — source of truth for every cleaning decision. Re-run it end to end whenever the source data changes; it regenerates the figures behind `reports/analysis_report.md`. Never touches production data. |
| `reports/analysis_report.md` | The written findings: every data-quality issue found, the decision made about it, and why. Hand-written from the notebook's output, not auto-generated — see its own §9 for how its 25-month scope relates to the report's 22-month demo window. |
| `power_query_cleaning_guide.md` | The production spec — each `analysis_report.md` decision (§7.x) turned into the exact Power Query M steps to build it. §0–§11 still match the live model; §12/§13 describe the original single-table design before it became a star schema (see the note at the top of that file). |
| `power_bi_build_instructions.md` | A running build log of the actual Power BI construction — an AI-assisted session-by-session record of what was built, what broke, and how it got fixed. Kept as-is, warts and all, rather than cleaned up after the fact. |
| `split_into_monthly_raw.py` | Seeds `data/raw/` with monthly CSVs from the historical xlsx, resolving the sheet overlap once so Power Query never has to know the two-sheet workbook exists. Run once to set up the demo. |
| `generate_product_costs.py` | Fabricates a plausible supplier-cost table (no real cost data is published for this dataset) so the model can compute COGS and margin. Deliberately covers only a subset of product codes by default — the gap is what a "revenue without cost data" measure in the model reports on. |
| `analyze_retail.py` | **Superseded.** The very first exploratory pass, before any of the current findings were known. Kept for history; `explore_retail.ipynb` replaced it entirely. |
| `reports/RetailDemo.pbip`, `reports/RetailDemo.Report/`, `reports/RetailDemo.SemanticModel/` | The actual Power BI project, saved in the git-friendly [PBIP format](https://learn.microsoft.com/power-bi/developer/projects/projects-overview) — diffable JSON/TMDL, not a binary blob. This is the deliverable: a star schema (`fact_sales` + `dim_product`/`dim_customer`/`dim_date`/`dim_country`/`dim_product_cost`), ~25 DAX measures, and a two-page report (a "Monday morning" summary page scoped to the latest complete month, and a drillthrough detail page). Open `RetailDemo.pbip` in Power BI Desktop to view or edit it. |
| `data/`, `archive/` | Local-only (gitignored) — the source workbook, the seeded monthly CSVs, and two months (`2011-10`, `2011-11`) deliberately held back to test that a new monthly upload flows through a refresh correctly. |
| `CLAUDE.md` | Project instructions for AI-assisted work on this repo. |

## Why a "self-refreshing" report

The whole design is built around one constraint: **a new monthly CSV should be able to land in `data/raw/` and the report should update correctly without anyone re-opening the model.** That shows up in a few concrete ways:

- Every cleaning rule in `power_query_cleaning_guide.md` operates on the data's own shape (e.g. "invoices prefixed C are cancellations"), never on hardcoded dates or row counts.
- The report's "latest month" scoping, its 13-week trend window, and its "reporting period" label are all computed from `MAX(date in the data)` — not typed in — so they're still correct after the next refresh.
- `2011-10` and `2011-11` are held back in `archive/` specifically so that scenario — "a new month arrives" — can actually be tested, not just assumed to work.

## Reproducing it locally

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
# Place the source workbook at data/online_retail_II.xlsx (not included in this repo)
.venv\Scripts\python split_into_monthly_raw.py
.venv\Scripts\python generate_product_costs.py
.venv\Scripts\jupyter nbconvert --to notebook --execute --inplace explore_retail.ipynb
```

Then open `reports/RetailDemo.pbip` in Power BI Desktop to view or refresh the model.
