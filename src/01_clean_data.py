"""Step 1 - Split and clean the Superstore file.

The raw CSV has three tables stacked in one file:
  * Orders              - rows whose "Row ID" is a number            (9,994 rows)
  * Regional managers   - rows between the "Person" and "Returned" header rows (4 people)
  * Returns             - rows where "Row ID" == "Yes" (Order ID is the returned order; has duplicates)

Usage:
    python 01_clean_data.py <raw_csv> <out_dir>
"""
import sys
from pathlib import Path

import pandas as pd


def main(raw_csv: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(raw_csv, dtype=str)
    print(f"Raw file: {raw.shape[0]:,} rows x {raw.shape[1]} cols")

    # ---- 1. Split the stacked tables -------------------------------------
    is_order = raw["Row ID"].str.fullmatch(r"\d+").fillna(False)
    orders = raw[is_order].copy()

    i_person = raw.index[raw["Row ID"] == "Person"][0]
    i_returned = raw.index[raw["Row ID"] == "Returned"][0]
    managers = raw.loc[i_person + 1:i_returned - 1, ["Row ID", "Order ID"]].copy()
    managers.columns = ["RegionalManager", "Region"]

    returns_raw = raw[raw["Row ID"] == "Yes"][["Order ID"]].copy()
    print(f"Orders: {len(orders):,} | Managers: {len(managers)} | Return rows: {len(returns_raw)}")

    # ---- 2. Clean returns (800 rows -> unique returned orders) ------------
    returns = returns_raw.drop_duplicates().reset_index(drop=True)
    returns["Returned"] = "Yes"
    print(f"Returns: removed {len(returns_raw) - len(returns)} duplicate rows -> {len(returns)} unique returned orders")
    missing = ~returns["Order ID"].isin(orders["Order ID"])
    print("Returned orders not found in Orders:", int(missing.sum()))

    # ---- 3. Clean orders --------------------------------------------------
    num = ["Sales", "Quantity", "Discount", "Profit"]
    for c in num:
        orders[c] = pd.to_numeric(orders[c], errors="raise")
    orders["Row ID"] = orders["Row ID"].astype(int)
    orders["Quantity"] = orders["Quantity"].astype(int)
    orders["Order Date"] = pd.to_datetime(orders["Order Date"], format="%m/%d/%Y")
    orders["Ship Date"] = pd.to_datetime(orders["Ship Date"], format="%m/%d/%Y")

    # Postal code: stored as number, so leading zeros were lost; 11 Burlington (Vermont) rows are blank.
    pc = pd.to_numeric(orders["Postal Code"], errors="coerce")
    n_blank = int(pc.isna().sum())
    orders["Postal Code"] = pc.round().astype("Int64").astype(str).str.zfill(5)
    blank_mask = pc.isna()
    assert (orders.loc[blank_mask, "City"] == "Burlington").all() and (orders.loc[blank_mask, "State"] == "Vermont").all()
    orders.loc[blank_mask, "Postal Code"] = "05401"  # Burlington, VT
    print(f"Postal Code: filled {n_blank} blank values (all Burlington, VT) with 05401; restored leading zeros")

    # Validation checks
    assert orders["Row ID"].is_unique
    assert orders.isna().sum().sum() == 0
    assert (orders["Ship Date"] >= orders["Order Date"]).all()
    assert (orders["Sales"] > 0).all()
    assert orders["Discount"].between(0, 1).all()
    n_lines_dup = int(orders.duplicated(["Order ID", "Product ID"]).sum())
    print(f"Validation passed. (Note: {n_lines_dup} repeated Order ID + Product ID lines have distinct Row IDs, kept as separate order lines.)")

    # ---- 4. Enrich --------------------------------------------------------
    orders = orders.merge(returns, on="Order ID", how="left")
    orders["Returned"] = orders["Returned"].fillna("No")
    orders = orders.merge(managers, on="Region", how="left")

    orders["OrderYear"] = orders["Order Date"].dt.year
    orders["OrderQuarter"] = "Q" + orders["Order Date"].dt.quarter.astype(str)
    orders["OrderMonth"] = orders["Order Date"].dt.month
    orders["YearMonth"] = orders["Order Date"].dt.strftime("%Y-%m")
    orders["ShipDays"] = (orders["Ship Date"] - orders["Order Date"]).dt.days
    orders["ProfitMargin"] = (orders["Profit"] / orders["Sales"]).round(4)
    orders["DiscountBand"] = pd.cut(
        orders["Discount"], bins=[-0.001, 0.0, 0.2, 0.4, 1.0],
        labels=["No discount", "1-20%", "21-40%", "Over 40%"]).astype(str)
    orders["IsLoss"] = (orders["Profit"] < 0).astype(int)

    # ---- 5. Date dimension for Power BI / Tableau -------------------------
    d = pd.DataFrame({"Date": pd.date_range("2015-01-01", "2018-12-31")})
    d["Year"] = d["Date"].dt.year
    d["Quarter"] = "Q" + d["Date"].dt.quarter.astype(str)
    d["MonthNumber"] = d["Date"].dt.month
    d["MonthName"] = d["Date"].dt.strftime("%b")
    d["YearMonth"] = d["Date"].dt.strftime("%Y-%m")
    d["Weekday"] = d["Date"].dt.strftime("%a")

    # ---- 6. Save ----------------------------------------------------------
    for c in ["Order Date", "Ship Date"]:
        orders[c] = orders[c].dt.strftime("%Y-%m-%d")
    d["Date"] = d["Date"].dt.strftime("%Y-%m-%d")
    orders.to_csv(out / "orders_clean.csv", index=False)
    returns.to_csv(out / "returns_clean.csv", index=False)
    managers.to_csv(out / "regional_managers.csv", index=False)
    d.to_csv(out / "dim_date.csv", index=False)
    print(f"\nSaved to {out}: orders_clean.csv {orders.shape}, returns_clean.csv, regional_managers.csv, dim_date.csv")
    print(f"Check totals -> Sales {orders['Sales'].sum():,.2f} | Profit {orders['Profit'].sum():,.2f} | "
          f"Orders {orders['Order ID'].nunique():,} | Customers {orders['Customer ID'].nunique():,}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python 01_clean_data.py <raw_csv> <out_dir>")
    main(sys.argv[1], sys.argv[2])
