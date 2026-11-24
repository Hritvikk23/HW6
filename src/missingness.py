"""Part 5: evidence about the missingness mechanism (notebook §4.1 pattern)."""
import sys
import pandas as pd


def compare_groups(df: pd.DataFrame, col: str, observed_cols: list[str]) -> pd.DataFrame:
    """Compare rows with and without `col` on observed columns. Return a summary table."""
    missing = df[col].isna()
    rows = []
    for obs in observed_cols:
        if pd.api.types.is_numeric_dtype(df[obs]):
            rows.append({
                "column": obs,
                "statistic": "median",
                "has value": df.loc[~missing, obs].median(),
                "missing": df.loc[missing, obs].median(),
            })
        else:
            has_share = df.loc[~missing, obs].value_counts(normalize=True)
            miss_share = df.loc[missing, obs].value_counts(normalize=True)
            for cat in sorted(set(has_share.index) | set(miss_share.index)):
                rows.append({
                    "column": obs,
                    "statistic": f"share {cat}",
                    "has value": round(has_share.get(cat, 0.0), 3),
                    "missing": round(miss_share.get(cat, 0.0), 3),
                })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])
    observed = ["Lot Area", "SalePrice", "Year Built", "Gr Liv Area", "Lot Config", "Neighborhood"]

    for col in ["Lot Frontage", "Mas Vnr Area"]:
        n = df[col].isna().sum()
        print(f"\n=== {col}: {n} of {len(df)} missing ({n / len(df):.1%}) ===")
        table = compare_groups(df, col, observed)
        print(table.to_string(index=False))
        slug = col.lower().replace(" ", "_")
        table.to_csv(f"reports/results/missingness_{slug}.csv", index=False)
