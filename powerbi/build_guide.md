# Build the dashboard in Power BI (about 60-90 minutes)

A ready-made interactive version is in `../dashboard/sales_dashboard.html` (open it in any browser). Use this guide to recreate it in Power BI Desktop (or Tableau) so you can show a `.pbix` in interviews.

## 1. Load the data
Home > Get data > Text/CSV, load from `../data/`:
- `orders_clean.csv` -> rename the query to **Orders** (set `Order Date` and `Ship Date` to Date type; `Postal Code` to Text)
- `dim_date.csv` -> rename to **Date** (set `Date` to Date type), then Table tools > **Mark as date table**
- `regional_managers.csv` (optional) -> **Managers**

## 2. Model
- Relationship: `Orders[Order Date]` (many) -> `Date[Date]` (one), single direction.
- Optional: `Orders[Region]` (many) -> `Managers[Region]` (one). (Manager is already a column in Orders, so this is not required.)
- Add the measures from `dax_measures.dax` (Modeling > New measure). Put them in a table called `_Measures` for tidiness.
- Create the `Growth Target` what-if parameter (Modeling > New parameter, 0 to 30%, step 5%, default 10%).

## 3. Pages and visuals

**Page 1 - Executive overview**
| Visual | Fields |
|---|---|
| 6 KPI cards | Total Sales, Total Profit, Profit Margin %, Orders, Avg Order Value, Return Rate % (add `Sales YoY %` as the card's reference label) |
| Line chart | Axis `Date[MonthName]` (sort by `MonthNumber`), Legend `Date[Year]`, Values `Total Sales` |
| Bar chart | Axis `Orders[Region]`, Values `Total Profit`, tooltip `Profit Margin %` |
| Slicers | `Date[Year]`, `Orders[Region]`, `Orders[Category]`, `Orders[Segment]` |

**Page 2 - Product and discount analysis**
| Visual | Fields |
|---|---|
| Bar chart (sorted) | Axis `Sub-Category`, Values `Total Profit`; Format > Colors > fx > Field value > `Profit Bar Colour` |
| Column chart | Axis `Orders[DiscountBand]`, Values `Profit Margin %` (sort axis: No discount, 1-20%, 21-40%, Over 40%) |
| Matrix | Rows `Sub-Category`, Columns `DiscountBand`, Values `Total Profit` + conditional formatting (red for negatives) |
| Table | `Product Name`, `Total Sales`, `Total Profit`; Top N filter = bottom 10 by `Total Profit` |

**Page 3 - Customers, regions and returns**
| Visual | Fields |
|---|---|
| Filled map | Location `State`, Colour saturation `Total Profit` (diverging: red-grey-blue, centre at 0) |
| Table | `Customer Name`, `Segment`, `Orders`, `Total Sales`, `Total Profit`; Top N = top 10 by profit |
| Column chart | Axis `Category`, Values `Return Rate %` |

## 4. Finishing touches
- One consistent palette: blue `#2A78D6` for positive/primary, orange `#EB6834` as the comparison colour, red `#E34948` only for losses.
- Titles that say what the chart shows ("Heavy discounts turn sales into losses"), not just field names.
- View > Page view > fit to page; add a title bar and a one-line "How to read" text box.
- Export a PDF or screenshots for your portfolio; publish to Power BI Service if you have an account and share the link.

## 5. Interview talking points
1. **Data prep:** the raw file had three tables stacked together (orders, managers, returns) and 504 duplicate return rows; I split, de-duplicated and validated totals ($2.30M sales, $286K profit).
2. **Headline insight:** discounts above 20% lose money (-$135K on 14% of order lines), so a discount cap or approval rule protects profit.
3. **Regional insight:** Central has a 7.9% margin vs 14.9% in West, mostly explained by 24% vs 11% average discounts.
4. **Why DAX time intelligence:** `SAMEPERIODLASTYEAR` and `TOTALYTD` need a proper date table.
5. **Limitation:** no cost or target data in the source, so the target measure uses an assumed growth rate.
