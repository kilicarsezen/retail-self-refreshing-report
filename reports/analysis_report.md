# Online Retail II — Data Analysis Report

**Source data:** `data/online_retail_II.xlsx` (2 sheets: "Year 2009-2010", "Year 2010-2011")
**Pipeline:** `explore_retail.ipynb`
**Report date:** 2026-08-26

## 1. Overview

The workbook's two yearly sheets were combined into a single dataset covering **December 2009 through December 2011**. The raw file contains 1,067,371 rows across the two sheets; 22,523 of those are a duplicate export of the same 9-day window (§7.0) and are removed before any analysis, leaving **1,044,848 rows**.

| Metric | Value |
|---|---|
| Rows loaded (raw) | 1,067,371 |
| Rows after removing the sheet-overlap duplication (§7.0) | 1,044,848 |
| Columns | 9 (Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, Country, source_sheet) |
| Schema validation | Passed — no missing or unexpected columns |
| Date range | 2009-12-01 07:45 → 2011-12-09 12:50 |

A `Revenue` column (`Quantity × Price`) and seven boolean flags were derived to separate real customer transactions from operational/bookkeeping noise and to surface data-quality issues: `is_cancelled` (§7.1), `is_stock_adjustment` (§7.2), `is_stock_writein` and `is_free_item` (§7.4), `is_bad_debt_adjustment` (§7.5), `is_duplicate_line` (§7.7), and `is_non_product_code` (§7.8). §7.6 cross-tabulates the transaction-type flags against `Quantity`/`Price` sign for a full picture of the dataset's shape.

## 2. Data Quality

### Missing values

| Column | Missing | % of rows |
|---|---|---|
| Customer ID | 235,287 | 22.5% |
| Description | 4,275 | 0.4% |
| All other columns | 0 | 0% |

No rows had missing `Invoice`, `StockCode`, `Price`, `Quantity`, or `InvoiceDate` — so the "invalid core data" check found **0 flagged rows**. Missing `Customer ID` is common in this dataset (guest/unregistered checkouts) and rows are still included in sales totals.

### Questionable numeric values

| Issue | Column | Count | % of non-null |
|---|---|---|---|
| Negative quantity | Quantity | 22,557 | 2.16% |
| Zero quantity | Quantity | 0 | 0.00% |
| Negative price | Price | 5 | 0.00% |
| Zero price | Price | 6,024 | 0.58% |
| Negative revenue | Revenue | 19,169 | 1.83% |
| Zero revenue | Revenue | 6,024 | 0.58% |

Negative quantities split into two distinct populations:

- **19,164 rows** are cancellations (invoices prefixed with "C") — e.g. invoice `C489449` and `C489459` show full-line reversals with matching negative revenue.
- **3,393 rows** are negative but **not** cancellations. See §7.2 for the finding and decision — these turned out to be internal stock write-offs (damaged/lost/miscounted stock), not customer activity.

The remaining 6,024 zero-price rows split three ways (see §7.4): the 3,393 negative-quantity `is_stock_adjustment` rows above, plus 2,561 positive-quantity **stock write-ins** (`is_stock_writein`) and 70 positive-quantity **free items** (`is_free_item`) — 3,393 + 2,561 + 70 = 6,024, exactly.

The 5 negative-price rows (and 1 further positive-price sibling not caught by this simple count) are financial **bad debt write-offs**, not sales — see §7.5.

### Column extremes

| Column | Min | Max |
|---|---|---|
| Quantity | -80,995 | 80,995 |
| Price | -£53,594.36 | £38,970.00 |
| Revenue | -£168,469.60 | £168,469.60 |
| Customer ID | 12346.0 | 18287.0 |
| Country | Australia | West Indies |

The symmetric min/max on Quantity and Revenue suggests a single large order was later fully cancelled (both appear as the `PAPER CRAFT , LITTLE BIRDIE` line in the top-products table below, netting out at exactly the same magnitude).

## 3. Sales Summary

| Metric | Value |
|---|---|
| Gross revenue (sales rows only) | £20,522,679.86 |
| Cancellation revenue (money returned) | −£1,465,303.66 |
| Bad debt revenue (financial write-offs) | −£147,614.08 |
| **Net revenue** | **£19,057,376.20** |
| Orders (unique invoices, sales rows only) | 40,082 |
| Customers (unique) | 5,942 |
| Cancelled rows | 19,165 |
| Stock adjustment rows | 3,393 |
| Stock write-in rows | 2,561 |
| Free item rows | 70 |
| Bad debt rows | 6 |
| Duplicate-flagged rows | 22,813 |
| Non-product-code rows | 5,993 |
| Flagged/invalid rows | 0 |

**Net revenue is the headline figure** (gross sales plus cancellation returns; bad debt is reported separately, since it isn't a sales transaction — see §7.5). Gross revenue on its own overstates actual revenue by ~7.1%, since it doesn't account for the ~£1.47M returned to customers via cancellations. Order and customer counts are based on sales rows, with one exception: `is_free_item` rows are kept in (§7.4), since a £0 item given to a real customer is still a real order. Duplicate-flagged and non-product-code rows are visibility flags (§7.7, §7.8), not exclusions — the rows they mark are already counted correctly (or not) via the flags above; the flag just tells you which ones to look at.

## 4. Monthly Revenue Trend

Net of cancellations (see §7.3) and bad debt write-offs (§7.5) — cancellations are counted in the month the return happened, not the month of the original purchase, since the two can't be reliably linked; likewise for bad debt.

| Month | Net Revenue (£) |
|---|---|
| 2009-12 | 799,847 |
| 2010-01 | 624,033 |
| 2010-02 | 533,091 |
| 2010-03 | 765,849 |
| 2010-04 | 644,175 |
| 2010-05 | 615,323 |
| 2010-06 | 679,787 |
| 2010-07 | 619,268 |
| 2010-08 | 656,776 |
| 2010-09 | 853,650 |
| 2010-10 | 1,084,094 |
| 2010-11 | 1,422,655 |
| 2010-12 | 748,957 |
| 2011-01 | 560,000 |
| 2011-02 | 498,063 |
| 2011-03 | 683,267 |
| 2011-04 | 493,207 |
| 2011-05 | 723,334 |
| 2011-06 | 691,123 |
| 2011-07 | 681,300 |
| 2011-08 | 693,743 |
| 2011-09 | 1,019,688 |
| 2011-10 | 1,070,705 |
| 2011-11 | 1,461,756 |
| 2011-12 | 433,686 *(partial month — data ends Dec 9)* |

Four months (2010-04, 2010-07, 2010-10, 2011-08) each include a one-off bad debt write-off (§7.5), which is excluded here as it isn't sales activity.

**Pattern:** Revenue peaks sharply every **November** (holiday stock-up before Christmas), in both 2010 (£1.42M) and 2011 (£1.46M), then drops off after the holiday season — December 2010 falls to £749K and January figures each year are lower still. This is a clear seasonal retail pattern.

## 5. Top 20 Products by Revenue

Net of cancellations (see §7.3) — each product's total includes any cancellation rows for that same `Description`.

| Rank | Product | Net Revenue (£) |
|---|---|---|
| 1 | REGENCY CAKESTAND 3 TIER | 314,513 |
| 2 | DOTCOM POSTAGE | 309,844 |
| 3 | WHITE HANGING HEART T-LIGHT HOLDER | 251,944 |
| 4 | PARTY BUNTING | 147,157 |
| 5 | JUMBO BAG RED RETROSPOT | 146,241 |
| 6 | ASSORTED COLOUR BIRD ORNAMENT | 128,907 |
| 7 | PAPER CHAIN KIT 50'S CHRISTMAS | 116,422 |
| 8 | POSTAGE | 110,430 |
| 9 | CHILLI LIGHTS | 80,237 |
| 10 | ROTATING SILVER ANGELS T-LIGHT HLDR | 71,031 |
| 11 | JUMBO BAG STRAWBERRY | 68,596 |
| 12 | RABBIT NIGHT LIGHT | 66,757 |
| 13 | BLACK RECORD COVER FRAME | 65,141 |
| 14 | JUMBO STORAGE BAG SUKI | 60,854 |
| 15 | VINTAGE UNION JACK BUNTING | 59,861 |
| 16 | EDWARDIAN PARASOL NATURAL | 59,329 |
| 17 | JUMBO BAG BAROQUE BLACK WHITE | 58,741 |
| 18 | HOT WATER BOTTLE TEA AND SYMPATHY | 58,541 |
| 19 | PAPER CHAIN KIT VINTAGE CHRISTMAS | 57,514 |
| 20 | CHOCOLATE HOT WATER BOTTLE | 57,408 |

Note: "DOTCOM POSTAGE" and "POSTAGE" are shipping line items rather than physical products, together accounting for **~£420K** of the top-20 total. The genuine best-selling product is the **REGENCY CAKESTAND 3 TIER**, followed by home-decor and gift items (t-light holders, bunting, storage jars) — consistent with a gift/homeware retailer.

Two lines that look large on a gross basis are absent from this net view: **"Manual"** adjustment entries and **PAPER CRAFT , LITTLE BIRDIE** — this is the line flagged in §2 "Column extremes": the single order with `Quantity` = ±80,995 was fully cancelled, so its net contribution is ~£0 and it doesn't rank in a net-revenue view.

## 6. Top 20 Countries by Revenue

Net of cancellations (§7.3) and bad debt (§7.5); shares are of **net revenue** (£19,057,376).

| Rank | Country | Net Revenue (£) | Share of total |
|---|---|---|---|
| 1 | United Kingdom | 16,186,222 | 84.9% |
| 2 | EIRE | 610,244 | 3.2% |
| 3 | Netherlands | 548,332 | 2.9% |
| 4 | Germany | 412,518 | 2.2% |
| 5 | France | 321,929 | 1.7% |
| 6 | Australia | 166,512 | 0.9% |
| 7 | Switzerland | 99,425 | 0.5% |
| 8 | Spain | 91,065 | 0.5% |
| 9 | Sweden | 87,809 | 0.5% |
| 10 | Denmark | 64,460 | 0.3% |
| 11 | Belgium | 63,228 | 0.3% |
| 12 | Portugal | 51,472 | 0.3% |
| 13 | Channel Islands | 41,090 | 0.2% |
| 14 | Japan | 39,662 | 0.2% |
| 15 | Norway | 35,456 | 0.2% |
| 16 | Italy | 30,269 | 0.2% |
| 17 | Finland | 29,514 | 0.2% |
| 18 | Cyprus | 24,163 | 0.1% |
| 19 | Austria | 23,178 | 0.1% |
| 20 | Greece | 18,995 | 0.1% |

The business is heavily **UK-concentrated (~85% of net revenue)**, with the next four markets (Ireland, Netherlands, Germany, France) as distant secondary markets in Western Europe.

## 7. Data Handling Decisions

This section documents how known data-quality issues are handled going forward, and why.

### 7.0 Sheet-overlap duplication

- **What:** the source workbook's two sheets aren't cleanly split by calendar year. `Year 2009-2010` runs through 2010-12-09, overlapping the first 9 days of `Year 2010-2011` (which starts 2010-12-01). **1,088 invoices (45,046 rows)** fall in that overlapping window and are recorded identically in both sheets.
- **Finding:** for those 1,088 invoices, the revenue recorded in the `Year 2009-2010` sheet is **exactly** the same as the revenue recorded in the `Year 2010-2011` sheet for the same invoices. Concatenating both sheets as-is means that 9-day window's revenue is counted twice throughout the entire analysis.
- **Decision:** drop the `Year 2009-2010` sheet's copy of those 1,088 invoices before any other processing, keeping the `Year 2010-2011` copy. This removes 22,523 rows and is applied first, ahead of every other flag or metric in this report — every figure elsewhere in this document already reflects this correction.

### 7.1 Cancellations (`is_cancelled`)

- **What:** Invoices prefixed with "C" (19,165 rows) represent cancelled orders — negative quantity, negative revenue.
- **Finding:** Despite the "C + same digits" naming convention, cancellation invoices do **not** reference an existing order invoice elsewhere in the data. Stripping the "C" from all 8,292 distinct cancellation invoice numbers matches **zero** original invoices — cancellations are recorded as fully independent invoices, not as a linked mutation of one specific original order.
- **Decision:** Keep the dataset at line-item (transaction) grain — one row per invoice line, `is_cancelled` flag as-is. Do **not** attempt to roll cancellations up into a single row per order (e.g. `is_cancelled` / `cancellation_qty` / `cancellation_date` columns merged onto the original order's row), since there is no reliable key linking a cancellation back to a specific original order. Partial vs. full returns cannot be distinguished with certainty from this data and are not classified.
- **Known oddity:** one cancelled invoice (`C496350`, a "Manual" adjustment line) has a *positive* quantity — the one exception to "cancellations are negative." Not corrected; noted here for awareness.
- **Effect on totals:** cancelled rows are excluded from `sales_rows` and from revenue/order/customer counts.

### 7.2 Stock adjustments (`is_stock_adjustment`)

- **What:** 3,393 rows have negative `Quantity` but are **not** cancellations (no "C" prefix).
- **Finding:** Every one of these rows has `Price = 0.00` and a missing `Customer ID`; none share an invoice with a normal (positive-quantity) sale row; and where a `Description` exists (~22% of the time) it reads as a warehouse note rather than a product name — `damages`, `missing`, `lost`, `lost?`, `thrown away`, `check`, `smashed`, `crushed`, `unsaleable, destroyed.`, `given away`, `invcd as 84879?`. These are internal inventory write-offs/corrections, not customer transactions.
- **Decision:** Flag these rows with `is_stock_adjustment` (`Quantity < 0` and not `is_cancelled`) and exclude them from `sales_rows` alongside cancellations, so they never contribute to revenue, order, or customer counts. Excluding them is what makes the "orders" figure represent actual customer orders — all 3,393 of these invoices contain no purchase at all, just an inventory correction.
- **Next step:** a small subset (31 rows) use non-standard stock codes (`DCGS*`, `GIFT`, etc.) instead of normal 5-digit product codes — flagged for a follow-up analysis, not yet resolved.

### 7.3 Revenue is reported net of cancellations

- **Reasoning:** cancellations aren't linked to a specific original order (§7.1), so a cancellation can't be matched against, and subtracted from, one particular prior sale. Simply leaving cancellation rows out of the revenue calculation isn't the same as netting them out, though — the original purchase's full amount would still be counted, while the money actually returned to the customer would go unaccounted for. Revenue has to include the cancellation amounts as a deduction to reflect what the business actually keeps.
- **Decision:** **net revenue** = sum of `Revenue` across sales rows **and** cancellation rows (stock adjustments and write-ins excluded, since they're not customer transactions). This is the headline "Total revenue" figure and drives the monthly/product/country breakdowns in §4–§6. Gross revenue is shown alongside it, since the gap between the two is itself a useful signal of return-heavy periods, products, or markets — currently **£1,465,304, or 7.1% of gross**.
- **Orders and customers:** these counts use sales rows only — a cancellation invoice isn't a placed order, so it isn't counted as one, even though its revenue is netted into the total.

### 7.4 Stock write-ins vs. free items (`is_stock_writein`, `is_free_item`)

- **What:** 2,631 rows have `Price = 0.00` and *positive* `Quantity`, are not cancellations, and are not `is_stock_adjustment` (which only covers negative quantity). This is the mirror image of §7.2's write-offs.
- **Finding:** this bucket splits cleanly by whether `Customer ID` is present:
  - **2,561 rows — no `Customer ID`.** Same profile as the existing stock-adjustment write-offs: no price, no customer, and where a note exists it's operational (`check`, `found`, `adjustment`, `amazon`, `?`) rather than a product description. This is stock being corrected/added back into inventory, not sold — the mirror image of a write-off, so call it a **write-in**.
  - **70 rows — has `Customer ID`.** A real customer received a real product (`6 RIBBONS EMPIRE`, `DOOR MAT FAIRY CAKE`, `CHRISTMAS PUDDING TRINKET POT`, …) at £0, alongside a handful of placeholder codes (`Manual`, `TEST001`, `PADS`). This is a genuine transaction — a **free item** given within a real order — not internal bookkeeping.
- **Decision:** two separate flags, since the two groups mean different things and should be handled differently rather than folded into one:
  - `is_stock_writein` — same treatment as `is_stock_adjustment`: excluded from `sales_rows`, `revenue_rows`, and order/customer counts, but reported as its own line rather than folded into the stock-adjustment count.
  - `is_free_item` — **kept inside** `sales_rows`/`revenue_rows`/order counts, since it's a real order for a real customer (just worth £0). Flagged only for visibility (e.g. "how many orders included a free item").
- **Note:** some write-in rows share an invoice with normal priced rows (e.g. a large real order with a couple of `£0` filler/packaging lines mixed in, or an invoice that's entirely `£0` lines except one lump-sum "Manual" line carrying the invoice's real value). This doesn't cause any double-counting: excluding a `£0` line never changes revenue, and the invoice still counts as an order via its other, non-excluded rows.

### 7.5 Bad debt adjustments (`is_bad_debt_adjustment`)

- **What:** a distinct 6-row category identified by `Invoice` prefixed **"A"** (not "C"), `StockCode == "B"`, `Description == "Adjust bad debt"`, `Quantity = 1`, no `Customer ID`. Five carry large negative prices (−£53,594.36 to −£11,062.06); one is a positive +£11,062.06 partial reversal. Net impact: **−£147,614.08**.
- **Finding:** this is a financial write-off — an amount the business has recorded as uncollectable and removed from its books — not a stock movement and not a customer cancellation, so it doesn't fit either of those existing categories.
- **Decision:** flag with `is_bad_debt_adjustment` (`Invoice` starts with "A") and exclude from `sales_rows`, `revenue_rows`, and order/customer counts — reported as **its own category** in §3, distinct from cancellations and stock adjustments, since it represents a different kind of event (a financial write-off, not a returned or corrected order).

### 7.6 Full data taxonomy

Every row is assigned to exactly one category by checking the rules below **in order** — a row gets the first category whose rule it matches, so e.g. a cancelled invoice is always `cancelled` even if it also happens to have `Price = 0`. Anything that matches none of the first five rules falls through to `normal_sale`.

| Priority | Category | Rule | Reference | Counted as a sale? |
|---|---|---|---|---|
| 1 | `cancelled` | `Invoice` starts with "C" | §7.1 | No — excluded from `sales_rows`, but its revenue is netted back in for **net revenue** (§7.3) |
| 2 | `bad_debt_adjustment` | `Invoice` starts with "A" | §7.5 | No — excluded entirely (not netted anywhere) |
| 3 | `stock_adjustment` | `Quantity < 0` (and not already `cancelled`/`bad_debt_adjustment`) | §7.2 | No — excluded entirely |
| 4 | `stock_writein` | `Price = 0` and `Quantity > 0` and `Customer ID` is missing | §7.4 | No — excluded entirely |
| 5 | `free_item` | `Price = 0` and `Quantity > 0` and `Customer ID` is present | §7.4 | **Yes** — kept in `sales_rows`/`revenue_rows`, it's a real order at £0 |
| 6 *(fallback)* | `normal_sale` | Everything left over — in practice, `Quantity > 0` and `Price > 0` | — | **Yes** |

Every row in the dataset falls into exactly one of the categories below (counts sum to exactly 1,044,848, the full row count post-deduplication — §7.0). `Quantity` is never exactly zero anywhere in the data, so quantity sign only ever takes negative/positive.

| Category | Qty sign | Price sign | Count |
|---|---|---|---|
| `normal_sale` | positive | positive | 1,019,653 |
| `cancelled` | negative | positive | 19,164 |
| `cancelled` | positive | positive | 1 *(known oddity, `C496350` — see §7.1)* |
| `stock_adjustment` | negative | zero | 3,393 |
| `stock_writein` | positive | zero | 2,561 |
| `free_item` | positive | zero | 70 |
| `bad_debt_adjustment` | positive | negative | 5 |
| `bad_debt_adjustment` | positive | positive | 1 |

Reading this top to bottom: the overwhelming majority of the dataset (97.6%) is `normal_sale`; every other category is some flavor of "not a straightforward paid purchase" — a cancellation, an inventory correction (in either direction), a free gift, or a financial write-off — and each now has its own flag and its own documented treatment above. Two further flags overlay this taxonomy without changing it — `is_duplicate_line` (§7.7) and `is_non_product_code` (§7.8) can each apply to a row regardless of which category it falls into above.

### 7.7 Duplicate line-item flag (`is_duplicate_line`)

- **What:** after removing the sheet-overlap duplication (§7.0), **22,813 rows** are still exact duplicates of another row — same Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, and Country. That's **11,001 distinct duplicate-content groups** across **4,387 invoices**; most groups repeat exactly twice, though a handful repeat up to 20 times.
- **Finding — who:** this isn't uniform — it concentrates heavily among a small number of customers. The top few accounts (Customer IDs 12748, 17841, 16549, 16782, and others) account for a large share of all duplicate rows, each with hundreds of duplicate lines. Only 116 of the 22,813 duplicate rows are cancellations; the rest are ordinary sales. Those accounts also sit at the 90th–99.9th percentile of *all* customers by both total revenue and total order count — they're genuine high-volume outliers, not just noisy accounts. The pattern reads as **wholesale/bulk buyers whose orders are logged as repeated single-unit lines** (the same product entered as several separate quantity-1 lines, e.g. two units of one item on the same order producing two `Quantity = 1` rows instead of one `Quantity = 2` row) rather than one line at a higher quantity — a data-entry convention, not an obvious error. If every group were collapsed down to one copy, £53,678 of revenue (spread over 11,676 "extra" rows) would disappear.
- **Finding — when:** duplicates appear in **every single month** of the dataset (25 of 25 months, December 2009 through December 2011 — never a gap), which argues against a short-lived system bug that would show up in a narrow window and then stop. The rate isn't flat, though: it roughly **doubles in November each year** (3.52% of that month's rows in 2010, 3.12% in 2011, versus a dataset-wide average of 2.18%) — the same month flagged in §4 as the seasonal order-volume peak. More orders (and more bulk orders) in November means more opportunities for this pattern to occur, which is consistent with an order-volume-driven cause rather than a bug tied to a specific date or deployment window.
- **Decision:** flag with `is_duplicate_line`, but **do not drop or collapse** these rows — both the customer-concentration and the month-by-month evidence point to legitimate repeat-entry tied to order volume, not a one-off system error, and collapsing them would remove real revenue. The flag exists so these rows can be reviewed or excluded deliberately if closer inspection of a specific customer or invoice calls for it.

### 7.8 Non-product stock code flag (`is_non_product_code`)

- **What:** standard product codes are 5 digits with an optional short letter suffix (e.g. `85123A`). **5,976 rows across 61 distinct codes** don't match that pattern (excluding `TEST001`/`TEST002`, now removed from the dataset — see below) — bookkeeping and operational entries riding in the same `StockCode` column as real products (`StockCode` itself is stored as a mix of numbers and text in the source file, which is why this needs an explicit check rather than being visible at a glance).
- **Finding:** these 63 codes are not one thing — some are legitimate revenue (postage, carriage, gift vouchers, a handful of products sold under alternate codes), while others are financial entries that shouldn't be treated as merchandise sales at all. `category` (§7.6) already tells us, row by row, which of the six categories each one currently falls into — `normal_sale` and `free_item` are the two that count as a sale; everything else is excluded from revenue by whichever flag matches it. Breaking each code down by category shows exactly which mechanism is doing the excluding:

  | StockCode | What it is | Raw `Description` text | `normal_sale` | `free_item` | `cancelled` | `stock_writein` | `stock_adjustment` | `bad_debt_adjustment` |
  |---|---|---|---|---|---|---|---|---|
  | `POST` | Postage | `POSTAGE` | 1,851 / £125,682 | — | 228 / −£15,252 | 7 / £0 | — | — |
  | `DOT` | Dotcom postage | `DOTCOM POSTAGE` | 1,415 / £309,854 | — | 3 / −£10 | 7 / £0 | — | — |
  | `M` / `m` | "Manual" adjustment entries | `Manual` | 861 / £339,630 | 7 / £0 | 535 / −£422,566 | — | — | — |
  | `C2` | Carriage | `CARRIAGE` | 267 / £13,426 | — | 7 / −£290 | 3 / £0 | — | — |
  | `D` | Discount | `Discount` | 5 / £398 | — | 168 / −£13,278 | — | — | — |
  | `BANK CHARGES` | Bank fees | `Bank Charges` | 34 / £519 | — | 66 / −£36,001 | — | — | — |
  | `S` | Samples | `SAMPLES` | 3 / £137 | — | 99 / −£6,138 | — | — | — |
  | `ADJUST` / `ADJUST2` | Named manual adjustments | `Adjustment by <name> on <date>` (free text, one per adjustment) | 39 / £9,629 | — | 31 / −£2,063 | — | — | — |
  | `AMAZONFEE` | Amazon marketplace fees | `AMAZON FEE` | 3 / £20,468 | — | 33 / −£241,988 | — | — | — |
  | `CRUK` | Charity commission | `CRUK Commission` | — | — | 16 / −£7,933 | — | — | — |
  | `B` | Bad debt (§7.5) | `Adjust bad debt` | — | — | — | — | — | 6 / −£147,614 |
  | *(48 further codes)* | Gift vouchers, alt-coded products | genuine product-style text (e.g. gift voucher amounts, real item names) | 221 / £2,942 | 1 / £0 | 2 / −£106 | 27 / £0 | 31 / £0 | — |

  `TEST001`/`TEST002` (17 rows, literal `This is a test product.` QA entries spread across `normal_sale`, `free_item`, `cancelled`, and `stock_writein`) have been **removed from the dataset entirely** (§6b) rather than left in this table, since they aren't real transactions of any kind.

  Each cell is *rows / revenue* for that code within that category. A few patterns stand out:
  - **`CRUK` and `B` are entirely one category each** — `CRUK` is 100% `cancelled`, `B` is 100% `bad_debt_adjustment` (by design, §7.5).
  - **`M`/`m`, `BANK CHARGES`, `D`, `S`, `AMAZONFEE`, and `CRUK` are dominated by `cancelled`** — meaning most of what removes these rows from gross revenue today is a **reversal invoice** (the same mechanism built for customer order cancellations), not a purpose-built flag for what they actually are. `AMAZONFEE` is the largest example: a real marketplace fee split between a small `normal_sale` slice (+£20,468, inflating gross revenue as if it were a product sale) and a much larger `cancelled` slice (−£241,988) that only lands in net revenue because cancellation revenue is netted in by design (§7.3) — not because it's recognized as a fee.
  - **`POST`/`DOT`/`C2` are almost entirely `normal_sale`**, with only a small `cancelled` trickle — consistent with genuine shipping revenue, not something that needs pulling out.
- **Decision:** flag with `is_non_product_code` for visibility — **no rows are excluded or reclassified yet, except `TEST001`/`TEST002`, which have been dropped outright (§6b)** since they were literal QA rows scattered across four categories with no legitimate transaction meaning in any of them. The remaining decision point: `POST`/`DOT`/`C2`/gift vouchers/alt-coded products look like genuine revenue and are probably fine to leave inside `normal_sale`. `AMAZONFEE`, `BANK CHARGES`, and `CRUK` look like they'd warrant their own "financial fee" treatment (similar to how `is_bad_debt_adjustment` was carved out in §7.5). Not yet implemented pending a decision on scope.

### 7.9 Multiple descriptions per product code (`has_variant_description`)

- **What:** restricted to genuine product codes only (`is_non_product_code == False`) — non-product codes like `ADJUST`/`M` are expected to carry many different free-text notes by design (§7.8), so including them here would just be noise about bookkeeping, not about products. **1,224 of 4,907 product codes (25%) have more than one distinct raw `Description` text.**
- **Finding:** the 1,224 codes split into two clearly different situations, based on what share of a code's rows use its single most common wording (its "modal share"):
  - **686 codes — one dominant name (≥95% of rows) plus a handful of stray one-off notes.** E.g. `20713`: 1,372 rows say `JUMBO BAG OWLS`, and single rows each say things like `missing`, `found`, `wrongly coded-23343`, `wrongly marked 23343` — operational annotations that ended up in the Description field, not alternate product names.
  - **538 codes — meaningfully split between two or more full wordings (modal share < 95%), with no single dominant text.** This looks like the product was renamed/reworded partway through the two-year window rather than a data-entry error. Examples: `21243` (`PINK  POLKADOT PLATE` / `PINK  SPOTTY PLATE`), `21955` (`DOORMAT UNION JACK GUNS AND ROSES` / `DOOR MAT UNION JACK GUNS AND ROSES` / `UNION JACK GUNS & ROSES  DOORMAT`), `84997A`/`B`/`C`/`D` (the children's cutlery sets, each renamed from a "3 PIECE POLKADOT/RETROSPOT" wording to a "CHILDRENS CUTLERY" wording).
- **Decision:** resolve each of the 1,224 codes to a single canonical `Description`, using a different rule per group since they represent different situations, then overwrite `Description` in place (raw per-row text is not kept separately) — flagged for traceability with `has_variant_description` (True for the 538 renamed/reworded codes):
  - **Stray-note codes:** use the **most frequent (modal) wording** — it already is the product's real name; the one-off notes are discarded.
  - **Renamed/reworded codes:** use whichever wording was **in use most recently** (latest `InvoiceDate`), since there's no single "correct" text and the most recent one reflects current catalog naming.
  - **78,365 rows** end up relabelled. This directly cleans up downstream aggregations that group by `Description` — e.g. §5's top-products ranking, which previously fragmented revenue for the same product across each of its wordings.

### 7.10 Non-country flag (`is_non_country`)

- **What:** of 43 distinct `Country` values, four aren't actual countries: `Unspecified` (756 rows), `Channel Islands` (1,664 rows, a dependency, not a country), `European Community` (61 rows, a multi-country bloc), `West Indies` (54 rows, a multi-country region) — **2,535 rows (0.24%)** in total. (`EIRE` and `RSA` are real countries — the Irish and Afrikaans-derived names for Ireland and South Africa — so they're left as-is.)
- **Finding:** these aren't errors so much as values that don't reduce to a single nation — there's no clean one-country mapping for a political bloc or an island chain, and £53,000 combined in real revenue (`Channel Islands` £41,454, `Unspecified` £9,687, `European Community` £1,292, `West Indies` £536) sits behind them.
- **Decision:** flag with `is_non_country` for visibility — **no rows are dropped or remapped.** They remain in the dataset and in the Top Countries ranking (§6) under their own label, since forcing them into a single-country bucket would misrepresent the data and the revenue itself is genuine.

### 7.11 Partial final month (`Retail_2011-12`)

- **What:** the source data stops at **2011-12-09**, so December 2011 holds only 9 days
  (£638,811 gross) against November's £1,509,496 — roughly 42% of a normal December.
- **Decision:** **exclude** — the December 2011 monthly export is not written to `raw/`.
  A partial month plotted next to full ones reads as a collapse in trade rather than a
  gap in the data, and no caption on a chart reliably prevents that misreading. The
  dataset therefore runs December 2009 through November 2011, 24 complete months.

## 8. Key Takeaways

1. **The two source sheets overlap by 9 days**: 1,088 invoices (22,523 rows) were recorded identically in both sheets, double-counting a whole window of revenue until removed (§7.0). Every figure in this report already reflects that correction.
2. **Data is largely clean otherwise**: no missing IDs, dates, or prices; the only meaningful gap is `Customer ID` (22.5% missing — guest orders).
3. **Revenue is reported net of cancellations, not just excluding them**: cancellations aren't linked to a specific original order (§7.1), so revenue must include their negative amounts as a deduction (§7.3) — the gap between gross and net is ~7.1% (£1.47M), a useful indicator of return activity in its own right.
4. **Five distinct categories sit outside a straightforward paid purchase**: cancellations, stock write-offs, stock write-ins, free items, and bad debt adjustments (§7.1–§7.5), each meaning something different and handled accordingly. §7.6 lays out the full picture in one table.
5. **Not everything with `Quantity < 0` or `Price = 0` is a customer transaction**: 3,393 stock write-offs and 2,561 stock write-ins are warehouse inventory corrections with no customer attached, excluded entirely from orders and revenue (§7.2, §7.4). The 70 free-item rows *do* have a real customer and are kept in (§7.4).
6. **Bad debt write-offs are a small but material category**: 6 "Adjust bad debt" rows, net −£147,614.08, reflect amounts written off as uncollectable rather than sales activity, and are reported separately from both cancellations and stock adjustments (§7.5).
7. **22,813 rows are duplicate line items, concentrated among a handful of wholesale customers**: this looks like a data-entry convention (repeat single-unit lines) rather than an error, so they're flagged (`is_duplicate_line`) but not removed — dropping them would erase £53,678 of real revenue (§7.7).
8. **A "financial fee" category is hiding inside ordinary sales**: `AMAZONFEE`, `BANK CHARGES`, and `CRUK` commission together account for over a quarter-million pounds that isn't merchandise revenue, only some of which is currently excluded — and only because it happens to be recorded as a cancellation, not because it's recognized as a fee (§7.8). This is flagged as a decision point, not yet resolved.
9. **Strong seasonality**: net revenue nearly doubles in November each year ahead of the holiday season, then falls sharply afterward.
10. **Revenue concentration**: a handful of home/gift products and shipping-related line items dominate top-line revenue; the UK alone drives ~85% of net revenue.
11. **Some non-product "sales" rows** (POSTAGE, DOTCOM POSTAGE) inflate the raw top-products ranking and should be excluded from a true best-seller analysis if needed; "Manual" adjustment entries look large on a gross basis but net to near zero once their associated cancellations are counted.
12. **A quarter of product codes had more than one Description on file**: 1,224 of 4,907 codes, split between stray operational notes (686 codes, resolved to the most-frequent wording) and genuine renames/rewordings over time (538 codes, resolved to the most recent wording) — 78,365 rows relabelled with a single canonical name each, which is what §5's top-products ranking is now based on (§7.9).
13. **Four `Country` values aren't real countries**: `Unspecified`, `Channel Islands`, `European Community`, and `West Indies` (2,535 rows, £53,000 combined revenue) don't reduce to a single nation, so they're flagged (`is_non_country`) and kept in Top Countries under their own label rather than dropped or remapped (§7.10).
