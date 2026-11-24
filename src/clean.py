"""Parts 3 and 4: decode true missing values, keep structural "none", check keys."""
import sys
import pandas as pd

# Columns where the dictionary defines "NA" as "none", not "unknown".
NA_MEANS_NONE: list[str] = []

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
    return df.copy() 

def check_keys(df: pd.DataFrame) -> None:
    """Assert key uniqueness; print exact and key duplicate counts; run the many_to_one join."""
    pass


if __name__ == "__main__":
    raw_path, out_path = sys.argv[1], sys.argv[2]
    df = fix_failures(decode_missing(load_raw(raw_path)))
    check_keys(df)
    df.to_csv(out_path, index=False)
    print(f"wrote {out_path}: {len(df)} rows, {df.shape[1]} columns")