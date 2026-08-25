## Retail report analysis

The analyzer streams both sheets in `data/online_retail_II.xlsx` and writes CSV summaries to `reports/`.

Run it from the project folder:

```powershell
.\.venv\Scripts\python.exe analyze_retail.py
```

Use a different workbook or output folder when needed:

```powershell
.\.venv\Scripts\python.exe analyze_retail.py path\to\retail.xlsx --output-dir reports
```

Generated files include `summary.csv`, `monthly_sales.csv`, `top_products.csv`, `top_countries.csv`, and `invalid_rows.csv`. The last file keeps every row with missing IDs or invalid core values, including its worksheet and Excel row number. Rows with only a missing customer ID are flagged but still included in the sales totals.
