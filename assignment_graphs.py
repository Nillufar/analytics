"""Build the assignment database and save the requested graphs."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
DOWNLOADS = Path.home() / "Downloads"


def find_file(name: str) -> Path:
    for folder in (BASE, DOWNLOADS):
        path = folder / name
        if path.exists():
            return path
    raise FileNotFoundError(f"Could not find {name} in {BASE} or {DOWNLOADS}")


def clean_gvkey(x):
    if pd.isna(x):
        return pd.NA
    text = str(x).strip()
    if text == "" or text.lower() == "nan":
        return pd.NA
    try:
        return str(int(float(text)))
    except ValueError:
        return text


mergers = pd.read_csv(find_file("Mergers.csv"))
fundamentals = pd.read_csv(find_file("Fundamentals.csv"))
announcement_returns = pd.read_csv(find_file("Announcement_Returns.csv"))

print("Mergers shape:", mergers.shape)
print("Fundamentals shape:", fundamentals.shape)
print("Announcement returns shape:", announcement_returns.shape)

print("\nMergers columns:")
print(mergers.columns.tolist())
print("\nFundamentals columns:")
print(fundamentals.columns.tolist())
print("\nAnnouncement returns columns:")
print(announcement_returns.columns.tolist())

print("\nFundamentals data check:")
print(fundamentals.head())
print(fundamentals.tail())
print(fundamentals.shape)
print(fundamentals.columns)
print(fundamentals.dtypes)
print(fundamentals.isna().sum())
print(fundamentals.duplicated().sum())

print("\nMissing values in Mergers:")
print(mergers.isna().sum().sort_values(ascending=False).head(10))
print("\nMissing values in Fundamentals:")
print(fundamentals.isna().sum().sort_values(ascending=False).head(10))
print("\nMissing values in Announcement Returns:")
print(announcement_returns.isna().sum())

print("\nDuplicate merger rows:", mergers.duplicated().sum())
print("\nDuplicate fundamentals rows:", fundamentals.duplicated().sum())
print("\nDuplicate announcement return rows:", announcement_returns.duplicated().sum())

mergers["da"] = pd.to_datetime(mergers["da"], errors="coerce")
fundamentals["datadate"] = pd.to_datetime(fundamentals["datadate"], errors="coerce")
announcement_returns["da"] = pd.to_datetime(announcement_returns["da"], errors="coerce")

mergers["agvkey"] = mergers["agvkey"].map(clean_gvkey).astype("string")
mergers["tgvkey"] = mergers["tgvkey"].map(clean_gvkey).astype("string")
fundamentals["gvkey"] = fundamentals["gvkey"].map(clean_gvkey).astype("string")

mergers["acu"] = mergers["acu"].astype("string").str.strip().str.upper()
announcement_returns["acu"] = (
    announcement_returns["acu"].astype("string").str.strip().str.upper()
)

mergers["announcement_year"] = mergers["da"].dt.year
mergers["previous_calendar_year"] = mergers["announcement_year"] - 1
fundamentals["calendar_year"] = fundamentals["datadate"].dt.year

fundamentals_year = (
    fundamentals.sort_values(["gvkey", "calendar_year", "datadate"])
    .dropna(subset=["gvkey", "calendar_year"])
    .drop_duplicates(subset=["gvkey", "calendar_year"], keep="last")
)

target_fundamentals = fundamentals_year.rename(
    columns={
        "gvkey": "tgvkey",
        "calendar_year": "previous_calendar_year",
        "sale": "target_sales",
        "at": "target_assets",
        "datadate": "target_datadate",
    }
)[
    [
        "tgvkey",
        "previous_calendar_year",
        "target_sales",
        "target_assets",
        "target_datadate",
    ]
]

acquirer_fundamentals = fundamentals_year.rename(
    columns={
        "gvkey": "agvkey",
        "calendar_year": "previous_calendar_year",
        "sale": "acquirer_sales",
        "at": "acquirer_assets",
        "datadate": "acquirer_datadate",
    }
)[
    [
        "agvkey",
        "previous_calendar_year",
        "acquirer_sales",
        "acquirer_assets",
        "acquirer_datadate",
    ]
]

final_data = mergers.merge(
    target_fundamentals,
    on=["tgvkey", "previous_calendar_year"],
    how="left",
)
final_data = final_data.merge(
    acquirer_fundamentals,
    on=["agvkey", "previous_calendar_year"],
    how="left",
)
final_data = final_data.merge(
    announcement_returns[["da", "acu", "A_A_RET"]],
    on=["da", "acu"],
    how="left",
)

final_data["transaction_value_to_sales"] = final_data["val"] / final_data["target_sales"]
final_data["transaction_value_to_assets"] = (
    final_data["val"] / final_data["acquirer_assets"]
)
for col in ("transaction_value_to_sales", "transaction_value_to_assets"):
    final_data[col] = pd.to_numeric(final_data[col], errors="coerce")
    final_data.loc[~np.isfinite(final_data[col]), col] = np.nan
    final_data.loc[final_data[col] <= 0, col] = np.nan

# Keep only deals that can be used in the client charts.
client_data = final_data.copy()
client_data["da"] = pd.to_datetime(client_data["da"])
client_data["announcement_year"] = client_data["da"].dt.year
client_data = client_data.dropna(subset=["master_deal_no", "da"])
client_data = client_data.drop_duplicates(subset=["master_deal_no"], keep="first")

sales_ratio_col = "transaction_value_to_sales"
assets_ratio_col = "transaction_value_to_assets"
return_col = "A_A_RET"

chart_data = client_data.copy()
transactions_by_year = chart_data.groupby("announcement_year").size()

print("Final database shape:", client_data.shape)
print("Chart sample shape:", chart_data.shape)
print("Duplicate transaction IDs:", client_data["master_deal_no"].duplicated().sum())
print(client_data[[sales_ratio_col, assets_ratio_col, return_col]].describe())

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(
    transactions_by_year.index,
    transactions_by_year.values,
    marker="o",
    color="darkblue",
    linewidth=2,
)
ax.set_title("Relevant Historical Transactions by Announcement Year")
ax.set_xlabel("Announcement Year")
ax.set_ylabel("Number of Transactions")
ax.set_xticks(transactions_by_year.index[::2])
fig.tight_layout()
fig.savefig(BASE / "transactions_by_year.png", dpi=300, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(
    chart_data[sales_ratio_col].dropna(),
    bins=20,
    color="steelblue",
    edgecolor="black",
)
ax.axvline(
    2,
    color="darkred",
    linestyle="--",
    linewidth=2,
    label="Client implied ratio = 2.0",
)
ax.set_title("Distribution of Transaction Value to Sales Ratios")
ax.set_xlabel("Transaction Value / Target Sales")
ax.set_ylabel("Number of Transactions")
ax.legend()
fig.tight_layout()
fig.savefig(BASE / "transaction_value_to_sales_histogram.png", dpi=300, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(
    chart_data[assets_ratio_col].dropna(),
    bins=20,
    color="mediumseagreen",
    edgecolor="black",
)
ax.axvline(
    0.2,
    color="darkred",
    linestyle="--",
    linewidth=2,
    label="Client implied ratio = 0.2",
)
ax.set_title("Distribution of Transaction Value to Assets Ratios")
ax.set_xlabel("Transaction Value / Acquirer Total Assets")
ax.set_ylabel("Number of Transactions")
ax.legend()
fig.tight_layout()
fig.savefig(BASE / "transaction_value_to_assets_histogram.png", dpi=300, bbox_inches="tight")
plt.close(fig)

sales_scatter = chart_data.dropna(subset=[sales_ratio_col, return_col])
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    sales_scatter[sales_ratio_col],
    sales_scatter[return_col],
    alpha=0.65,
    color="darkblue",
    edgecolor="white",
    linewidth=0.5,
)
ax.axhline(0, color="black", linewidth=1)
ax.set_title("Transaction Value to Sales Ratio and Acquirer Announcement Returns")
ax.set_xlabel("Transaction Value / Target Sales")
ax.set_ylabel("Acquirer Announcement Return")
fig.tight_layout()
fig.savefig(BASE / "sales_ratio_vs_announcement_return.png", dpi=300, bbox_inches="tight")
plt.close(fig)

assets_scatter = chart_data.dropna(subset=[assets_ratio_col, return_col])
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    assets_scatter[assets_ratio_col],
    assets_scatter[return_col],
    alpha=0.65,
    color="mediumseagreen",
    edgecolor="white",
    linewidth=0.5,
)
ax.axhline(0, color="black", linewidth=1)
ax.set_title("Transaction Value to Assets Ratio and Acquirer Announcement Returns")
ax.set_xlabel("Transaction Value / Acquirer Total Assets")
ax.set_ylabel("Acquirer Announcement Return")
fig.tight_layout()
fig.savefig(BASE / "assets_ratio_vs_announcement_return.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# Winsorized views so extreme Compustat ratios do not hide the mass of deals.
sales_plot = chart_data[sales_ratio_col].clip(upper=chart_data[sales_ratio_col].quantile(0.99))
assets_plot = chart_data[assets_ratio_col].clip(upper=chart_data[assets_ratio_col].quantile(0.99))

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(sales_plot.dropna(), bins=20, color="steelblue", edgecolor="black")
ax.axvline(2, color="darkred", linestyle="--", linewidth=2, label="Client implied ratio = 2.0")
ax.set_title("Transaction Value to Sales Ratios (99th percentile winsorized)")
ax.set_xlabel("Transaction Value / Target Sales")
ax.set_ylabel("Number of Transactions")
ax.legend()
fig.tight_layout()
fig.savefig(BASE / "transaction_value_to_sales_histogram_winsorized.png", dpi=300, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(assets_plot.dropna(), bins=20, color="mediumseagreen", edgecolor="black")
ax.axvline(0.2, color="darkred", linestyle="--", linewidth=2, label="Client implied ratio = 0.2")
ax.set_title("Transaction Value to Assets Ratios (99th percentile winsorized)")
ax.set_xlabel("Transaction Value / Acquirer Total Assets")
ax.set_ylabel("Number of Transactions")
ax.legend()
fig.tight_layout()
fig.savefig(BASE / "transaction_value_to_assets_histogram_winsorized.png", dpi=300, bbox_inches="tight")
plt.close(fig)

scatter_sales = chart_data.dropna(subset=[sales_ratio_col, return_col])
scatter_sales = scatter_sales[
    scatter_sales[sales_ratio_col] <= scatter_sales[sales_ratio_col].quantile(0.99)
]
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    scatter_sales[sales_ratio_col],
    scatter_sales[return_col],
    alpha=0.65,
    color="darkblue",
    edgecolor="white",
    linewidth=0.5,
)
ax.axhline(0, color="black", linewidth=1)
ax.set_title("Sales Ratio vs Announcement Return (99th percentile winsorized)")
ax.set_xlabel("Transaction Value / Target Sales")
ax.set_ylabel("Acquirer Announcement Return")
fig.tight_layout()
fig.savefig(BASE / "sales_ratio_vs_announcement_return_winsorized.png", dpi=300, bbox_inches="tight")
plt.close(fig)

scatter_assets = chart_data.dropna(subset=[assets_ratio_col, return_col])
scatter_assets = scatter_assets[
    scatter_assets[assets_ratio_col] <= scatter_assets[assets_ratio_col].quantile(0.99)
]
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    scatter_assets[assets_ratio_col],
    scatter_assets[return_col],
    alpha=0.65,
    color="mediumseagreen",
    edgecolor="white",
    linewidth=0.5,
)
ax.axhline(0, color="black", linewidth=1)
ax.set_title("Assets Ratio vs Announcement Return (99th percentile winsorized)")
ax.set_xlabel("Transaction Value / Acquirer Total Assets")
ax.set_ylabel("Acquirer Announcement Return")
fig.tight_layout()
fig.savefig(
    BASE / "assets_ratio_vs_announcement_return_winsorized.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close(fig)

summary = {
    "n_deals": int(len(client_data)),
    "n_with_sales_ratio": int(client_data[sales_ratio_col].notna().sum()),
    "n_with_assets_ratio": int(client_data[assets_ratio_col].notna().sum()),
    "n_with_return": int(client_data[return_col].notna().sum()),
    "sales_median": float(client_data[sales_ratio_col].median()),
    "assets_median": float(client_data[assets_ratio_col].median()),
    "return_mean": float(client_data[return_col].mean()),
    "return_median": float(client_data[return_col].median()),
    "share_sales_above_2": float((client_data[sales_ratio_col] > 2).mean()),
    "share_assets_above_02": float((client_data[assets_ratio_col] > 0.2).mean()),
    "year_min": int(transactions_by_year.index.min()),
    "year_max": int(transactions_by_year.index.max()),
}
print("\nSUMMARY")
for key, value in summary.items():
    print(f"{key}: {value}")
print("\nTransactions by year:")
print(transactions_by_year.to_string())
print("\nSaved graphs to", BASE)
