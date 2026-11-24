# HW5: Ames Housing quality audit

## How to run

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all
```

## Provenance (Part 1)

| Item | Value |
| --- | --- |
| Source URL | https://jse.amstat.org/v19n3/decock/AmesHousing.txt|
| Downloaded on | 2026-11-23|
| Citation | De Cock, D. (2011). Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project. Journal of Statistics Education, 19(3). |
| Data dictionary | https://jse.amstat.org/v19n3/decock/DataDocumentation.txt |
| Terms of use | JSE data sets may be used freely for teaching if cited (name, author, date accessed); publication requires the author's consent.|
| Rows, columns on arrival |(2930, 82) |

## Features used in Part 7

List the 8 to 15 numeric columns in `NUMERIC_FEATURES`, and why.

## AI assistance

Tool, what it was used for, which files.
Tool: Claude

| What it was used for | Files |
|---|---|

| Help with the validation functions and rules | validate.py |
| Help with the Part 2 fixes, missing-value decoding, key checks and neighborhood join | src/clean.py |
| Help with the missingness comparison and imputation strategies | missingness.py, impute.py` |
| Help with the Part 7 variants and the custom Pipeline transformer | evaluate.py|
| Explaining outputs and turning my answers into Markdown | report.md |


