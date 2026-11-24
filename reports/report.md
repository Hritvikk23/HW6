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

```
Output
FAIL data/raw/AmesHousing.txt
range: Garage Yr Blt outside [-inf, 2010]: 1 rows
allowed: MS Zoning has codes not in the dictionary: 29 rows
cross: Year remod/add before year Built: 1 rows
cross: Year sold before year built: 1 rows
```



## 3 Sentinels and structural absence
| Column | "NA" count | Dictionary meaning | Numeric check | Decision |
|---|---|---|---|---|
| Alley | 2,732 | No alley access | none available | Keep as category |
| Bsmt Qual, Bsmt Cond, Bsmt Exposure, BsmtFin Type 1, BsmtFin Type 2 | 79 each | No basement | Total Bsmt SF = 0 in 79 houses | Keep |
| Fireplace Qu | 1,422 | No fireplace | Fireplaces = 0 in 1,422 | Keep |
| Garage Type, Garage Finish | 157 each | No garage | Garage Area = 0 in 157 | Keep |
| Garage Qual, Garage Cond | 158 each | No garage | Only 157 houses don't have a agarage | 157 kept; 1 house has a garage but "NA" quality and condition, so that value is genuinely unknown|
| Pool QC | 2,917 | No pool | Pool Area = 0 in 2,917 | Keep |
| Fence | 2,358 | No fence | none available | Keep |
| Misc Feature | 2,824 | None | Misc Val = 0 in 2,827 | Keep |


### Other strings the default load turned into NaN
Mas Vnr type. The dictionary defines it as "no masonry veneer"

| Column | Zeros | Sentinel or true zero? |
|---|---|---|
| Total Bsmt SF | 79 | True zero. It matches the 79 houses with no basement, a house without a basement has 0 sq ft of basement |
| Garage Area, Garage Cars | 157 each | True zero, it matches the 157 houses with no garage. 0 sq ft and 0 car capacity  |
| Fireplaces | 1,422 | True zero, it matches the 1,422 houses with no fireplace, the count is really 0. |
| Pool Area | 2,917 | True zero, it matches the 2,917 houses with no pool |
| Mas Vnr Area | 1,748 | True zero. No veneer means 0 sq ft of veneer |
| Wood Deck SF, Open Porch SF, Enclosed Porch, 3Ssn Porch, Screen Porch | various | True zero. The feature is absent, so its area is 0. |
| 2nd Flr SF, Low Qual Fin SF | 1,678; 2,890 | True zero, a one-story house has 0 sq ft of second floor|
| BsmtFin SF 1, BsmtFin SF 2, Bsmt Unf SF | 930; 2,578; 244 | True zero. a basement can have 0 sq ft of a given finish type|
| Misc Val | 2,827 | True zero, no miscellaneous feature means $0 of value|
| Full Bath, Bedroom AbvGr, Kitchen AbvGr | 12; 8; 3 | True zero. The dictionary counts these above grade only, so a house with all of them below grade correctly shows 0 |

## 4 Keys and duplicates
- I chose PID as a key because it's unique and no property appears twice. 
- Order is a observation number. It differs on every row so it hides the copies too
- PID idenitifes a property and order idenitfies a row like sale record
```
Output 
exact duplicate rows: 0
Order duplicates: 0
PID duplicates: 0
duplicate rows ignoring Order and PID: 0
```

## 5 Missingness mechanism
- I compared houses with and without a value on four observed columns Lot area, sale price, year built and Gr liv area. I also compared them on tow categorical colunns Neighbourhood and Lot config. 
- For each column I split the houses into two groups, where the column has a value and where it is missing and then compared the groups on four numeric and two categorical columns.
```
Output

=== Lot Frontage: 490 of 2929 missing (16.7%) ===
      column     statistic  has value    missing
    Lot Area        median   9247.000  10397.500
   SalePrice        median 157500.000 173000.000
  Year Built        median   1972.000   1976.500
 Gr Liv Area        median   1433.000   1488.000
  Lot Config  share Corner      0.167      0.212
  Lot Config share CulDSac      0.038      0.180
  Lot Config     share FR2      0.027      0.041
  Lot Config     share FR3      0.004      0.008
  Lot Config  share Inside      0.765      0.559
Neighborhood share Blmngtn      0.008      0.016
Neighborhood share Blueste      0.004      0.000
Neighborhood  share BrDale      0.012      0.000
Neighborhood share BrkSide      0.039      0.027
Neighborhood share ClearCr      0.008      0.049
Neighborhood share CollgCr      0.090      0.096
Neighborhood share Crawfor      0.034      0.041
Neighborhood share Edwards      0.073      0.033
Neighborhood share Gilbert      0.046      0.110
Neighborhood  share Greens      0.003      0.002
Neighborhood share GrnHill      0.000      0.004
Neighborhood  share IDOTRR      0.036      0.012
Neighborhood share Landmrk      0.000      0.002
Neighborhood share MeadowV      0.014      0.008
Neighborhood share Mitchel      0.037      0.049
Neighborhood   share NAmes      0.154      0.139
Neighborhood share NPkVill      0.009      0.004
Neighborhood  share NWAmes      0.035      0.094
Neighborhood share NoRidge      0.022      0.035
Neighborhood share NridgHt      0.067      0.006
Neighborhood share OldTown      0.094      0.020
Neighborhood   share SWISU      0.018      0.008
Neighborhood  share Sawyer      0.040      0.108
Neighborhood share SawyerW      0.043      0.039
Neighborhood share Somerst      0.066      0.041
Neighborhood share StoneBr      0.019      0.010
Neighborhood  share Timber      0.023      0.031
Neighborhood share Veenker      0.007      0.016

=== Mas Vnr Area: 23 of 2929 missing (0.8%) ===
      column     statistic  has value    missing
    Lot Area        median   9429.000   9965.000
   SalePrice        median 160000.000 207500.000
  Year Built        median   1973.000   2006.000
 Gr Liv Area        median   1440.000   1564.000
  Lot Config  share Corner      0.174      0.217
  Lot Config share CulDSac      0.061      0.087
  Lot Config     share FR2      0.029      0.043
  Lot Config     share FR3      0.005      0.000
  Lot Config  share Inside      0.731      0.652
Neighborhood share Blmngtn      0.010      0.000
Neighborhood share Blueste      0.003      0.000
Neighborhood  share BrDale      0.010      0.000
Neighborhood share BrkSide      0.037      0.000
Neighborhood share ClearCr      0.015      0.000
Neighborhood share CollgCr      0.091      0.087
Neighborhood share Crawfor      0.035      0.043
Neighborhood share Edwards      0.066      0.043
Neighborhood share Gilbert      0.055      0.217
Neighborhood  share Greens      0.003      0.000
Neighborhood share GrnHill      0.001      0.000
Neighborhood  share IDOTRR      0.032      0.000
Neighborhood share Landmrk      0.000      0.000
Neighborhood share MeadowV      0.013      0.000
Neighborhood share Mitchel      0.039      0.000
Neighborhood   share NAmes      0.152      0.000
Neighborhood share NPkVill      0.008      0.000
Neighborhood  share NWAmes      0.045      0.000
Neighborhood share NoRidge      0.024      0.000
Neighborhood share NridgHt      0.056      0.087
Neighborhood share OldTown      0.082      0.000
Neighborhood   share SWISU      0.017      0.000
Neighborhood  share Sawyer      0.052      0.000
Neighborhood share SawyerW      0.043      0.043
Neighborhood share Somerst      0.059      0.435
Neighborhood share StoneBr      0.018      0.000
Neighborhood  share Timber      0.024      0.043
Neighborhood share Veenker      0.008      0.000
```

- For Lot Frontage, MAR applies and I reject MCAR. If it were missing completely at random, houses with and without a value would look alike, but they do not. Cul-de-sac lots make up 18.0% of houses missing Lot Frontage but only 3.8% of houses with a value. 
- For Mas Vns Area, it is MAR as well because the pattern is explained by observed columns "Year built". It is not MCAR because if the 23 blanks were completely at random the houses would like a typical ames house but they don't. The median of year built is 2006 for the missing houses and 1973 for the rest of them, which means they are brand new. 43.5% of it is in neighbouhood somerst and in gilbert (21.7%), which are the areas with a lot of new construction. 
- The data cannot check if the missingness depends on the values themselves, it can reject MCAR but cannot differentiate MNAR vs MAR.
- If Los Frontage was MNAR that would mean the missingness depends on frontage. A real world process that would cause it could be if it was left blank because it was too small. 

## 6 Imputation strategy and defense (at most 150 words)
- I chose the neighborhood-median fill. In Part 5, MCAR was rejected for Lot Frontage because houses missing it are concentrated in neighborhoods such as Gilbert, ClearCr, NWAmes and Sawyer, and on cul-de-sac lots, so they are not a random sample of houses. A single overall median assumes they are typical, which is the MCAR assumption, and that contradicts the evidence. Under MAR, missingness depends on observed columns, so filling within Neighborhood, one of those columns, uses information related to why the values are missing. The costs support this choice: it keeps more of the spread (std 21.7 vs 21.3) and more of the link with Lot Area (0.387 vs 0.361). Its limit is that it ignores lot configuration, and if the data were MNAR, neither fill would be unbiased.

- I chose the neighborhood-meadin fill. In part5 MCAR is rejected for Lot frontage because houses missing are concentrated in neighborhoods such as Gilbert, ClearCr, NWAmes, Swayer and on cul-de-sac lots, so they are not random sample of houses. A single median assumes they are typical which is what MCAR assumes and that contradicts the evidence. Under MAR, the missingness depends on observed columns, so filling with neighborhood which is one of the columns, uses that information related why the values are missing. The costs supports the choice. It keeps more of the spread and more of the link with Lot Area. (std after 21.3(median) vs 21.7(neighborhood)) and (corr after 0.361(Median) vs 0.387(neighborhood))

```
Output
                           median  neighborhood_median
std before                 23.340               23.340
std after                  21.302               21.695
corr with Lot Area before   0.489                0.489
corr with Lot Area after    0.361                0.387
saved reports/figures/lot_frontage_median.png
saved reports/figures/lot_frontage_neighborhood_median.png
```

## 7 Leakage-safe evaluation
## 8 What this data cannot tell you
