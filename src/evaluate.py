"""Part 7: variants A, B, C with the given model (notebook §6.1 to §6.3)."""
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline


NUMERIC_FEATURES: list[str] = [
    "Lot Frontage", "Lot Area", "Overall Qual", "Overall Cond",
    "Year Built", "Year Remod/Add", "Gr Liv Area", "1st Flr SF",
    "Full Bath", "Bedroom AbvGr", "TotRms AbvGrd", "Fireplaces",
]   # 8 to 15 columns, including "Lot Frontage"


CV = KFold(n_splits=5, shuffle=True, random_state=5110)


def rmse(estimator, X: pd.DataFrame, y: pd.Series) -> float:
    return -cross_val_score(estimator, X, y, cv=CV, scoring="neg_root_mean_squared_error").mean()

class NeighborhoodMedianImputer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.medians_ = X.groupby("Neighborhood")["Lot Frontage"].median()
        self.overall_ = X["Lot Frontage"].median()
        return self

    def transform(self, X):
        X = X.copy()
        fill = X["Neighborhood"].map(self.medians_).fillna(self.overall_)
        X["Lot Frontage"] = X["Lot Frontage"].fillna(fill)
        return X.drop(columns="Neighborhood")  

if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    y = np.log(df["SalePrice"])

    # Variant A 
    quintile = pd.qcut(df["SalePrice"], 5, labels=False)
    X_a = df[NUMERIC_FEATURES].copy()
    X_a["Lot Frontage"] = X_a["Lot Frontage"].fillna(
        df.groupby(quintile)["Lot Frontage"].transform("median"))

    # Variant B 
    X_b = df[NUMERIC_FEATURES].copy()
    neighborhood_median = df.groupby("Neighborhood")["Lot Frontage"].transform("median")
    X_b["Lot Frontage"] = (X_b["Lot Frontage"].fillna(neighborhood_median)
                           .fillna(df["Lot Frontage"].median()))

    # Variant C
    X_c = df[NUMERIC_FEATURES + ["Neighborhood"]]
    pipe = Pipeline([("fill", NeighborhoodMedianImputer()), ("model", LinearRegression())])

    results = pd.Series({
        "A: SalePrice-quintile median, full table": rmse(LinearRegression(), X_a, y),
        "B: neighborhood median, full table": rmse(LinearRegression(), X_b, y),
        "C: neighborhood median, in Pipeline": rmse(pipe, X_c, y),
    }, name="RMSE (log SalePrice)")

    print(results.round(5).to_string())
    print(f"\nB - C difference: {results.iloc[1] - results.iloc[2]:.6f}")
    results.to_csv("reports/results/evaluation.csv")
