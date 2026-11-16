"""Step 2 - Load orders_clean.csv into SQLite and run every query in sql/analysis_queries.sql.

Usage:
    python 02_run_sql.py <orders_clean_csv> <queries_sql> <out_dir>

Creates <out_dir>/sales.db and one CSV per query in <out_dir>/sql_results/.
"""
import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd


def main(orders_csv: str, queries_sql: str, out_dir: str) -> None:
    out = Path(out_dir)
    (out / "sql_results").mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(orders_csv, dtype={"Postal Code": str})
    con = sqlite3.connect(out / "sales.db")
    df.to_sql("orders", con, if_exists="replace", index=False)

    text = Path(queries_sql).read_text()
    blocks = re.split(r"^-- name:\s*(\S+)\s*$", text, flags=re.M)
    for name, body in zip(blocks[1::2], blocks[2::2]):
        res = pd.read_sql_query(body, con)
        res.to_csv(out / "sql_results" / f"{name}.csv", index=False)
        print(f"\n=== {name} ===")
        print(res.to_string(index=False))
    con.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: python 02_run_sql.py <orders_clean_csv> <queries_sql> <out_dir>")
    main(*sys.argv[1:])
