"""Step 3 - Build the self-contained interactive HTML dashboard.

Embeds the cleaned order lines (compact arrays, ~0.5 MB) into src/dashboard_template.html so the
dashboard works offline with no libraries - just open the file in a browser.

Usage:
    python 03_build_dashboard.py <orders_clean_csv> <template_html> <out_html>
"""
import json
import sys
from pathlib import Path

import pandas as pd


def main(orders_csv: str, template: str, out_html: str) -> None:
    df = pd.read_csv(orders_csv, dtype={"Postal Code": str})

    def codes(col):
        cats = sorted(df[col].unique())
        return cats, df[col].map({c: i for i, c in enumerate(cats)})

    region, c_reg = codes("Region")
    category, c_cat = codes("Category")
    segment, c_seg = codes("Segment")
    state, c_st = codes("State")

    sub_pairs = sorted(df[["Sub-Category", "Category"]].drop_duplicates().itertuples(index=False, name=None))
    sub = [[s, category.index(c)] for s, c in sub_pairs]
    c_sub = df["Sub-Category"].map({s: i for i, (s, _) in enumerate(sub_pairs)})

    cust_ids = sorted(df["Customer ID"].unique())
    cust_name = df.drop_duplicates("Customer ID").set_index("Customer ID")["Customer Name"]
    cust_seg = df.drop_duplicates("Customer ID").set_index("Customer ID")["Segment"]
    customer = [cust_name[c] for c in cust_ids]
    cust_seg_idx = [segment.index(cust_seg[c]) for c in cust_ids]
    c_cust = df["Customer ID"].map({c: i for i, c in enumerate(cust_ids)})

    prod_ids = sorted(df["Product ID"].unique())
    prod_name = df.drop_duplicates("Product ID").set_index("Product ID")["Product Name"]
    product = [prod_name[p] for p in prod_ids]
    c_prod = df["Product ID"].map({p: i for i, p in enumerate(prod_ids)})

    order_ids = {o: i for i, o in enumerate(df["Order ID"].unique())}
    c_ord = df["Order ID"].map(order_ids)

    rows = pd.DataFrame({
        "y": df["OrderYear"], "m": df["OrderMonth"], "reg": c_reg, "cat": c_cat, "sub": c_sub, "seg": c_seg,
        "st": c_st, "cu": c_cust, "pr": c_prod, "or": c_ord, "di": df["Discount"],
        "sa": df["Sales"].round(2), "pf": df["Profit"].round(2), "qt": df["Quantity"],
        "rt": (df["Returned"] == "Yes").astype(int),
    })
    data = {
        "years": sorted(int(y) for y in df["OrderYear"].unique()),
        "region": region, "category": category, "segment": segment, "state": state,
        "sub": sub, "customer": customer, "custSeg": cust_seg_idx, "product": product,
        "rows": rows.values.tolist(),
    }
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    html = Path(template).read_text(encoding="utf-8")
    assert "/*__DATA__*/null" in html
    html = html.replace("/*__DATA__*/null", payload)
    Path(out_html).parent.mkdir(parents=True, exist_ok=True)
    Path(out_html).write_text(html, encoding="utf-8")
    print(f"Wrote {out_html}  ({len(html) / 1024:.0f} KB, {len(rows):,} order lines embedded)")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: python 03_build_dashboard.py <orders_clean_csv> <template_html> <out_html>")
    main(*sys.argv[1:])
