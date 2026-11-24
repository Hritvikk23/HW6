"""Part 2: validation as code. Raise once, listing every failure (notebook §1)."""
import sys
import pandas as pd
import math


class ValidationError(Exception):
    pass


# Each rule needs a source. Put it in the comment.
NUMERIC = {
    "Order", "Lot Frontage", "Lot Area", "Year Built", "Year Remod/Add",
    "Mas Vnr Area", "BsmtFin SF 1", "BsmtFin SF 2", "Bsmt Unf SF", "Total Bsmt SF",
    "1st Flr SF", "2nd Flr SF", "Low Qual Fin SF", "Gr Liv Area",
    "Bsmt Full Bath", "Bsmt Half Bath", "Full Bath", "Half Bath",
    "Bedroom AbvGr", "Kitchen AbvGr", "TotRms AbvGrd", "Fireplaces",
    "Garage Yr Blt", "Garage Cars", "Garage Area", "Wood Deck SF",
    "Open Porch SF", "Enclosed Porch", "3Ssn Porch", "Screen Porch",
    "Pool Area", "Misc Val", "Mo Sold", "Yr Sold", "SalePrice",
    "PID",           # Nominal, but a numeric parcel ID
    "MS SubClass",   # Nominal, but the dictionary's codes are numbers (020, 030, ...)
    "Overall Qual",  # Ordinal, but the dictionary's scale is 1-10
    "Overall Cond",  # Ordinal, but the dictionary's scale is 1-10
}
TEXT = {
    "MS Zoning", "Street", "Alley", "Lot Shape", "Land Contour", "Utilities",
    "Lot Config", "Land Slope", "Neighborhood", "Condition 1", "Condition 2",
    "Bldg Type", "House Style", "Roof Style", "Roof Matl", "Exterior 1st",
    "Exterior 2nd", "Mas Vnr Type", "Exter Qual", "Exter Cond", "Foundation",
    "Bsmt Qual", "Bsmt Cond", "Bsmt Exposure", "BsmtFin Type 1", "BsmtFin Type 2",
    "Heating", "Heating QC", "Central Air", "Electrical", "Kitchen Qual",
    "Functional", "Fireplace Qu", "Garage Type", "Garage Finish", "Garage Qual",
    "Garage Cond", "Paved Drive", "Pool QC", "Fence", "Misc Feature",
    "Sale Type", "Sale Condition",
}
RANGES = {
    # "Year Built": (1870, 2010),   # source: ...
    "Yr Sold": (2006, 2010),             # source: study period, sales 2006-2010 (De Cock, 2011)
    "Year Built": (-math.inf, 2010),     # source: study period, cannot be built after the last sale year
    "Year Remod/Add": (-math.inf, 2010), # source: study period, cannot be remodeled after the last sale year
    "Garage Yr Blt": (-math.inf, 2010),  # source: study period, garage cannot be built after the last sale year
    "Mo Sold": (1, 12),                  # source: physical limit, months of the year
    "Overall Qual": (1, 10),             # source: data dictionary, Overall Qual is rated 1-10
    "Overall Cond": (1, 10),             # source: data dictionary, Overall Cond is rated 1-10
    "Lot Area": (0, math.inf), 
}
ALLOWED = {
    # "Street": {"Grvl", "Pave"},   # source: data dictionary, Street(Nominal)
    "Street": {"Grvl", "Pave"}, # source: data dictionary, Street(Nominal)
    "Alley": {"Grvl", "Pave", "NA"}, # source: data dictionary, Alley(Nominal)
    "MS Zoning": {"A", "C", "FV", "I", "RH", "RL", "RP", "RM"},  # source: data dictionary, MS Zoning(Nominal)
    "Central Air": {"N", "Y"}, #source: data dictionary, Central Air(Nominal)
}


def check_schema(df: pd.DataFrame) -> list[str]:
    """Return a list of schema failures: missing or extra columns, wrong dtype families."""
    errors = []
    expected = NUMERIC | TEXT
    missing = sorted(expected - set(df.columns))
    extra = sorted(set(df.columns) - expected)
    if missing:
        errors.append(f"schema: missing columns {missing}")
    if extra:
        errors.append(f"schema: unexpected columns {extra}")

    for col in sorted(NUMERIC & set(df.columns)):
        if not pd.api.types.is_numeric_dtype(df[col]):
            as_num = pd.to_numeric(df[col], errors="coerce")
            bad = df[col][as_num.isna() & df[col].notna()]
            errors.append(
                f"schema: {col} should be numeric but is {df[col].dtype}; "
                f"{len(bad)} non-numeric values"
            )
    for col in sorted(TEXT & set(df.columns)):
        if pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"schema: {col} should be text but is {df[col].dtype}")
    return errors


def check_ranges(df: pd.DataFrame) -> list[str]:
    """Return one message per column with values outside its range. NaN is not judged here."""
    errors = []
    for col, (lo, hi) in RANGES.items():
        if col not in df.columns:
            continue  # check_schema already reports it
        vals = pd.to_numeric(df[col], errors="coerce")
        bad = vals[vals.notna() & ~vals.between(lo, hi)]
        if len(bad):
            errors.append(f"range: {col} outside [{lo}, {hi}]: {len(bad)} rows")
    return errors


def check_allowed(df: pd.DataFrame) -> list[str]:
    """Return one message per categorical column with values not in the dictionary."""
    errors = []
    for col, allowed in ALLOWED.items():
        if col not in df.columns:
            continue
        vals = df[col].dropna().astype(str)
        bad = vals[~vals.isin(allowed)]
        if len(bad):
            errors.append(f"allowed: {col} has codes not in the dictionary: {len(bad)} rows")
    return errors


def check_cross_column(df: pd.DataFrame) -> list[str]:
    """Return failures of rules that involve two or more columns."""
    errors = []
    num = lambda c: pd.to_numeric(df[c], errors="coerce")

    # a house that cannot be remodeled before it was built
    if {"Year Built", "Year Remod/Add"} <= set(df.columns):
        n = (num("Year Remod/Add") < num("Year Built")).sum()
        if n:
            errors.append(f"cross: Year remod/add before year Built: {n} rows")

    # a house that cannot be sold before it was built
    if {"Year Built", "Yr Sold"} <= set(df.columns):
        n = (num("Yr Sold") < num("Year Built")).sum()
        if n:
            errors.append(f"cross: Year sold before year built: {n} rows")
    return errors


def validate(df: pd.DataFrame) -> pd.DataFrame:
    errors = check_schema(df) + check_ranges(df) + check_allowed(df) + check_cross_column(df)
    if errors:
        raise ValidationError("\n".join(errors))
    return df


if __name__ == "__main__":
    path = sys.argv[1]
    raw = "--raw" in sys.argv
    df = pd.read_csv(path, sep="\t" if raw else ",", keep_default_na=False, na_values=[""])
    try:
        validate(df)
        print(f"PASS {path}")
    except ValidationError as e:
        print(f"FAIL {path}\n{e}")
        sys.exit(1)
