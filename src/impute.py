"""Part 6: at least two strategies for Lot Frontage, and their costs (notebook §5 pattern)."""
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # for headless servers


def cost_table(before: pd.Series, after: pd.Series, other: pd.Series) -> pd.Series:
    """std before/after, correlation with `other` before/after."""
    return pd.Series({
        "std before": before.std(),
        "std after": after.std(),
        "corr with Lot Area before": before.corr(other),
        "corr with Lot Area after": after.corr(other),
    })

if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])
    before = df["Lot Frontage"]
    missing = before.isna()

    # Strategy 1: simple fill with the overall median
    median_fill = before.fillna(before.median())

    # Strategy 2: median within the same Neighborhood, median if a neighborhood has no observed Lot Frontage at all
    group_median = df.groupby("Neighborhood")["Lot Frontage"].transform("median")
    group_fill = before.fillna(group_median).fillna(before.median())

    strategies = {"median": median_fill, "neighborhood_median": group_fill}

    costs = pd.DataFrame({name: cost_table(before, after, df["Lot Area"])
                          for name, after in strategies.items()})
    print(costs.round(3).to_string())
    costs.to_csv("reports/results/imputation_costs.csv")

    # One histogram per strategy
    for name, after in strategies.items():
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist([after[~missing], after[missing]], bins=50, stacked=True,
                label=["observed", f"imputed ({missing.sum()} rows)"])
        ax.set_xlabel("Lot Frontage (ft)")
        ax.set_ylabel("Houses")
        ax.set_title(f"Lot Frontage after {name.replace('_', ' ')} fill")
        ax.legend()
        fig.tight_layout()
        fig.savefig(f"reports/figures/lot_frontage_{name}.png", dpi=120)
        plt.close(fig)
        print(f"saved reports/figures/lot_frontage_{name}.png")
