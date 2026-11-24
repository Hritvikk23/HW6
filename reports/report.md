# HW5 report

## 1 Provenance
## 2 Validation: failures on the raw file

## Validation failures on the raw file (Part 2)

| Rule | Failure | Rows | What I did |
|---|---|---|---|
| Range: Garage Yr Blt ≤ 2010 (study period) | Order 2261 has Garage Yr Blt = 2207 | 1 | Corrected to 2007. The house was built in 2006, remodeled in 2007, and sold in 2007, so 2207 is a typo. |
| Allowed values: MS Zoning (data dictionary) | Codes `C (all)` (25), `I (all)` (2), `A (agr)` (2) are not dictionary codes | 29 | Recoded explicitly in `clean.py` to the dictionary codes `C`, `I`, `A`. The allowed set in `validate.py` was not widened. |
| Cross-column: Year Remod/Add ≥ Year Built | Order 851 was remodeled in 2001 but built in 2002 | 1 | Set Year Remod/Add to 2002. The dictionary says the remodel date equals the construction date when there is no remodel. |
| Cross-column: Yr Sold ≥ Year Built | Order 2181 was sold in 2007 but built in 2008 and remodeled in 2009 (Sale Condition = Partial) | 1 | Dropped the row. It is a pre-construction sale, and no single year can be corrected without inventing a value. The cleaned file has 2,929 rows. |

## 3 Sentinels and structural absence
## 4 Keys and duplicates
## 5 Missingness mechanism
## 6 Imputation strategy and defense (at most 150 words)
## 7 Leakage-safe evaluation
## 8 What this data cannot tell you
