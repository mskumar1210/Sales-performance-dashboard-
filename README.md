# Sales Performance Dashboard - Superstore

End-to-end sales analytics: cleaning a messy multi-table file, SQL KPIs, an interactive dashboard (HTML, works offline), and a Power BI build kit (DAX + guide).

**Tools:** Python (pandas), SQL (SQLite, portable), interactive HTML/JS dashboard, Power BI (DAX measures + build guide)

## Business problem
A retailer sold $2.30M over 2015-2018 at a 12.5% margin. Leadership wants one dashboard that shows how sales and profit are trending, which regions and products make or lose money, and what discounting is doing to profit.

## Dataset
Superstore sample sales data: 9,994 order lines, 5,009 orders, 793 customers, 4 regions, 17 sub-categories, Jan 2015 - Dec 2018. It is a public sample dataset (also available on Kaggle); the copy here came from a public GitHub repository. The file is in `data/superstore_raw.csv`.

## Data cleaning (`src/01_clean_data.py`)
The raw CSV is **three tables stacked in one file** (10,800 rows):
| Part | Rows | What was done |
|---|---|---|
| Orders | 9,994 | Parsed dates and numbers; validated unique Row IDs, no nulls, ship date >= order date, sales > 0, discount in [0, 1] |
| Regional managers | 4 | Split out into `regional_managers.csv` and joined by region |
| Returns | 800 | **504 exact duplicates removed** -> 296 unique returned orders; all matched to orders; joined as a `Returned` flag |

Also: restored leading zeros in postal codes (stored as numbers) and filled 11 blank postal codes (all Burlington, VT) with 05401. Added derived fields: year, quarter, month, ship days, profit margin, discount band, loss flag. Built a date dimension for BI tools. Totals reconcile: **$2,297,200.86 sales, $286,397.02 profit**.

## SQL analysis (`sql/analysis_queries.sql`)
14 queries: headline KPIs, YoY growth with `LAG()`, monthly trend, region/manager performance, sub-category profit, discount bands, loss-making products and states, segment value, top customers with `RANK()`, ship mode, return rate, quarterly seasonality. Results are exported to `outputs/sql_results/`.

## Key findings
| # | Finding | Evidence |
|---|---|---|
| 1 | **Discounts above 20% destroy profit** | 21-40% discount: -15.3% margin (90% of lines lose money); over 40%: -77.4% margin (100% of lines lose). Together they lost **$135K**, about a third of the profit earned on all other orders |
| 2 | **Central region lags** | 7.9% margin vs 14.9% in West; average discount 24% vs 11%. Texas (-$25.7K) and Illinois (-$12.6K) are the biggest Central losses |
| 3 | **Three sub-categories lose money** | Tables -$17.7K, Bookcases -$3.5K, Supplies -$1.2K; Tables earn +$13K on lines with up to 20% discount but lose $30.7K on heavier discounts |
| 4 | **Machines are high revenue, low profit** | $189K sales at a 1.8% margin; 3D printers are the worst products (-$8.9K for one model) |
| 5 | **Growth is strong but seasonal** | Sales +29.5% in 2017 and +20.4% in 2018 after -2.8% in 2016; Q4 = 38% of annual sales; November 2018 peaked at $118K |
| 6 | **Returns** | 5.9% of orders returned (296 of 5,009); Technology highest at 8.0% |

## Recommendations
1. Introduce a discount cap (e.g. 20%) or manager approval above it; review Binders, Tables and Machines first.
2. Audit Central region pricing and discount practice, starting with Texas and Illinois.
3. Reprice or rationalise Tables, Bookcases and Supplies; stop discounting them heavily.
4. Plan inventory and staffing for the Q4 peak; investigate the weak Q1.
5. Look into why Technology orders are returned more often.

## Dashboard (`dashboard/sales_dashboard.html`)
Open the file in any browser (no internet or install needed). Features: Year / Region / Category / Segment slicers, 6 KPI cards with year-over-year deltas, monthly trend by year (Sales/Profit toggle), profit by region, segment and sub-category, margin by discount level, top customers and least profitable products, hover tooltips, a "view data as table" option under each chart, dark mode and a mobile layout. Numbers were cross-checked against pandas for several filter combinations.

Previews: `dashboard/dashboard_preview.png`, `dashboard_preview_dark.png`, `dashboard_preview_filtered_2018_west.png`.

## Power BI kit (`powerbi/`)
`dax_measures.dax` (KPIs, time intelligence, target vs actual, discount and return measures) and `build_guide.md` (load, model, page-by-page visuals, interview points). I could not create a `.pbix` file here, so build it in Power BI Desktop with the guide; the DAX was written against the exact column names in `orders_clean.csv` but has not been run in Power BI.

## Project structure
```
p2_sales/
├── data/        superstore_raw.csv, orders_clean.csv, returns_clean.csv, regional_managers.csv, dim_date.csv
├── sql/         analysis_queries.sql
├── src/         01_clean_data.py, 02_run_sql.py, 03_build_dashboard.py, dashboard_template.html
├── dashboard/   sales_dashboard.html + preview images
├── powerbi/     dax_measures.dax, build_guide.md
├── outputs/     sales.db, sql_results/*.csv
└── requirements.txt
```

## How to run
```bash
pip install -r requirements.txt
python src/01_clean_data.py data/superstore_raw.csv data
python src/02_run_sql.py data/orders_clean.csv sql/analysis_queries.sql outputs
python src/03_build_dashboard.py data/orders_clean.csv src/dashboard_template.html dashboard/sales_dashboard.html
```

## Resume bullets
- Cleaned a 10,800-row raw file containing three stacked tables (orders, returns, regional managers) with Python; removed 504 duplicate records and reconciled totals to $2.30M sales and $286K profit.
- Built an interactive sales dashboard (KPI cards, YoY growth, region, product, discount and returns views with slicers) on 9,994 order lines using SQL, Python and JavaScript, plus a Power BI DAX measure set.
- Found that discounts above 20% generated a $135K loss and that the Central region earned a 7.9% margin vs 14.9% in West; recommended a discount cap and regional pricing review.

## Limitations
Sample data with no cost or target fields; the DAX target measure uses an assumed growth rate. Describe this as a personal / portfolio project.
