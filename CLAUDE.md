# Project instructions

This is a retail analytics pipeline: monthly client CSVs land in `data/raw/`, get cleaned and
combined in Power BI's Power Query, and feed a self-refreshing report.

## Power BI build work

When the task is building or modifying the Power Query / model layer of the Power BI file under
`reports/`, follow `power_bi_build_instructions.md` and `power_query_cleaning_guide.md` exactly —
they hold the agreed process and ground rules for that work (in short: never decide alone on
anything the guide doesn't settle, test each step's result before calling it done, report anything
that looks off rather than pushing past it). Read both before touching the model.

These rules apply specifically to the Power BI build; use ordinary judgment for everything else
in the repo (the Python scripts, the guide's own content, general repo housekeeping).
