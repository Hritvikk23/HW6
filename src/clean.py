"""Parts 3 and 4: decode true missing values, keep structural "none", check keys."""
import sys
import pandas as pd
import numpy as np

# Columns where the dictionary defines "NA" as "none", not "unknown".
NA_MEANS_NONE: list[str] = [
    "Alley",                                     # NA = No alley access
    "Bsmt Qual", "Bsmt Cond", "Bsmt Exposure",   # NA = No Basement
    "BsmtFin Type 1", "BsmtFin Type 2",          # NA = No Basement
    "Fireplace Qu",                              # NA = No Fireplace
    "Garage Type", "Garage Finish",              # NA = No Garage
    "Garage Qual", "Garage Cond",                # NA = No Garage
    "Pool QC",                                   # NA = No Pool
    "Fence",                                     # NA = No Fence
    "Misc Feature",                              # NA = None
]

MS_ZONING_FIXES = {"C (all)": "C", "I (all)": "I", "A (agr)": "A"}

def load_raw(path: str) -> pd.DataFrame:
    """Load with keep_default_na=False so that "NA" and "None" survive as strings."""
    return pd.read_csv(path, sep="\t", keep_default_na=False, na_values=[""])

def fix_value(df, order, col, old, new):
    """Change one cell, identified by Order, after checking its current value."""
    mask = df["Order"] == order
    if mask.sum() != 1:
        raise ValueError(f"Order {order}: expected 1 row, found {mask.sum()}")
    current = df.loc[mask, col].iloc[0]
    if current != old:
        raise ValueError(f"Order {order}, {col}: expected {old}, found {current}")
    df.loc[mask, col] = new
    print(f"fixed  Order {order}: {col} {old} -> {new}")

def fix_failures(df: pd.DataFrame) -> pd.DataFrame:
    """Part 2: fix every validation failure found on the raw file. Return a new DataFrame."""
    df = df.copy()

    # Garage Yr Blt 2207 is a typo: built 2006, remodeled 2007, sold 2007.
    fix_value(df, 2261, "Garage Yr Blt", 2207, 2007)

    # Remodel recorded before construction; dictionary: remodel date equals
    # construction date when there is no remodel.
    fix_value(df, 851, "Year Remod/Add", 2001, 2002)

    # MS Zoning codes that differ from the dictionary, recoded explicitly.
    for old, new in MS_ZONING_FIXES.items():
        n = (df["MS Zoning"] == old).sum()
        df.loc[df["MS Zoning"] == old, "MS Zoning"] = new
        print(f"recode MS Zoning '{old}' -> '{new}': {n} rows")

    # Pre-construction sale (Sale Condition = Partial): sold 2007 but built 2008
    # and remodeled 2009. No single year can be corrected, so drop the row.
    mask = df["Order"] == 2181
    if mask.sum() != 1:
        raise ValueError(f"Order 2181: expected 1 row, found {mask.sum()}")
    df = df[~mask]
    print("dropped Order 2181: Yr Sold 2007 before Year Built 2008 (Partial sale)")
    return df


def decode_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Turn only true missing values into NaN. Return a new DataFrame."""
    df = df.copy()
    #"NA" is not a dictionary code, so it means unknown
    for col in df.columns:
        if col not in NA_MEANS_NONE and not pd.api.types.is_numeric_dtype(df[col]):
            mask = df[col] == "NA"
            if mask.any():
                df.loc[mask, col] = np.nan
                print(f"decode {col}: {mask.sum()} 'NA' -> missing")

    # If another column shows the feature exists, the "NA" is genuinely unknown.
    has_feature = {
        "garage": (df["Garage Type"] != "NA") | (df["Garage Area"] > 0),
        "basement": df["Total Bsmt SF"] > 0,
        "fireplace": df["Fireplaces"] > 0,
        "pool": df["Pool Area"] > 0,
    }
    columns = {
        "garage": ["Garage Type", "Garage Finish", "Garage Qual", "Garage Cond"],
        "basement": ["Bsmt Qual", "Bsmt Cond", "Bsmt Exposure", "BsmtFin Type 1", "BsmtFin Type 2"],
        "fireplace": ["Fireplace Qu"],
        "pool": ["Pool QC"],
    }
    for feature, cols in columns.items():
        for col in cols:
            mask = has_feature[feature] & (df[col] == "NA")
            if mask.any():
                df.loc[mask, col] = np.nan
                print(f"decode {col}: {mask.sum()} 'NA' but a {feature} exists -> missing")
    return df


def check_keys(df: pd.DataFrame) -> None:
    """Assert key uniqueness; print exact and key duplicate counts; run the many_to_one join."""
    for key in ["Order", "PID"]:
        dupes = df.duplicated(subset=key).sum()
        print(f"key {key}: {df[key].nunique()} unique in {len(df)} rows, {dupes} duplicates")
    print(f"exact duplicate rows: {df.duplicated().sum()}")
    assert df["PID"].is_unique, "PID is not unique"

    # Lookup table
    lookup = pd.DataFrame({
        "Neighborhood": [
            "Blmngtn", "Blueste", "BrDale", "BrkSide", "ClearCr", "CollgCr", "Crawfor",
            "Edwards", "Gilbert", "Greens", "GrnHill", "IDOTRR", "Landmrk", "MeadowV",
            "Mitchel", "Names", "NoRidge", "NPkVill", "NridgHt", "NWAmes", "OldTown",
            "SWISU", "Sawyer", "SawyerW", "Somerst", "StoneBr", "Timber", "Veenker",
        ],
        "Neighborhood Name": [
            "Bloomington Heights", "Bluestem", "Briardale", "Brookside", "Clear Creek",
            "College Creek", "Crawford", "Edwards", "Gilbert", "Greens", "Green Hills",
            "Iowa DOT and Rail Road", "Landmark", "Meadow Village", "Mitchell",
            "North Ames", "Northridge", "Northpark Villa", "Northridge Heights",
            "Northwest Ames", "Old Town", "South & West of Iowa State University",
            "Sawyer", "Sawyer West", "Somerset", "Stone Brook", "Timberland", "Veenker",
        ],
    })
    before = len(df)
    merged = df.merge(lookup, on="Neighborhood", how="left", validate="many_to_one")
    print(f"neighborhood join: {before} rows before, {len(merged)} rows after")
    assert len(merged) == before, "join changed the row count"

    # This reports codes the dictionary doesn't have instead of silently mapping them.
    unmatched = merged.loc[merged["Neighborhood Name"].isna(), "Neighborhood"].value_counts()
    if len(unmatched):
        print(f"codes not in the dictionary lookup: {unmatched.to_dict()}")


if __name__ == "__main__":
    raw_path, out_path = sys.argv[1], sys.argv[2]
    df = fix_failures(decode_missing(load_raw(raw_path)))
    check_keys(df)
    df.to_csv(out_path, index=False)
    print(f"wrote {out_path}: {len(df)} rows, {df.shape[1]} columns")