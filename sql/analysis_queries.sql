-- ============================================================
-- Sales Performance Dashboard - KPI & Analysis Queries
-- Table: orders  (loaded from data/orders_clean.csv)
-- Each query starts with a "-- name:" marker so src/02_run_sql.py can run and export them.
-- Syntax is SQLite; PostgreSQL/MySQL need only minor changes (quoting of column names).
-- ============================================================

-- name: q01_headline_kpis
-- Business question: What are the headline numbers?
SELECT
    ROUND(SUM(Sales), 2)                                  AS total_sales,
    ROUND(SUM(Profit), 2)                                 AS total_profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2)            AS profit_margin_pct,
    COUNT(DISTINCT "Order ID")                            AS orders,
    COUNT(DISTINCT "Customer ID")                         AS customers,
    ROUND(SUM(Sales) / COUNT(DISTINCT "Order ID"), 2)     AS avg_order_value,
    SUM(Quantity)                                         AS units_sold
FROM orders;

-- name: q02_yearly_growth
-- Business question: How are sales and profit growing year over year?
WITH yearly AS (
    SELECT OrderYear AS year,
           SUM(Sales)  AS sales,
           SUM(Profit) AS profit
    FROM orders GROUP BY OrderYear
)
SELECT
    year,
    ROUND(sales, 2)  AS sales,
    ROUND(profit, 2) AS profit,
    ROUND(100.0 * profit / sales, 2) AS profit_margin_pct,
    ROUND(100.0 * (sales  - LAG(sales)  OVER (ORDER BY year)) / LAG(sales)  OVER (ORDER BY year), 2) AS sales_yoy_pct,
    ROUND(100.0 * (profit - LAG(profit) OVER (ORDER BY year)) / LAG(profit) OVER (ORDER BY year), 2) AS profit_yoy_pct
FROM yearly
ORDER BY year;

-- name: q03_monthly_trend
-- Business question: What does the monthly trend and seasonality look like?
SELECT
    YearMonth,
    ROUND(SUM(Sales), 2)  AS sales,
    ROUND(SUM(Profit), 2) AS profit,
    COUNT(DISTINCT "Order ID") AS orders
FROM orders
GROUP BY YearMonth
ORDER BY YearMonth;

-- name: q04_region_performance
-- Business question: Which regions (and managers) perform best?
SELECT
    Region,
    RegionalManager,
    ROUND(SUM(Sales), 2)  AS sales,
    ROUND(SUM(Profit), 2) AS profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) AS profit_margin_pct,
    ROUND(100.0 * SUM(Sales) / (SELECT SUM(Sales) FROM orders), 2) AS share_of_sales_pct,
    ROUND(100.0 * AVG(Discount), 2) AS avg_discount_pct
FROM orders
GROUP BY Region, RegionalManager
ORDER BY sales DESC;

-- name: q05_category_subcategory
-- Business question: Which products make or lose money?
SELECT
    Category,
    "Sub-Category" AS sub_category,
    ROUND(SUM(Sales), 2)  AS sales,
    ROUND(SUM(Profit), 2) AS profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) AS profit_margin_pct,
    ROUND(100.0 * AVG(Discount), 2) AS avg_discount_pct
FROM orders
GROUP BY Category, "Sub-Category"
ORDER BY profit DESC;

-- name: q06_discount_vs_profit
-- Business question: Do discounts destroy profit?
SELECT
    DiscountBand,
    COUNT(*)                                          AS order_lines,
    ROUND(SUM(Sales), 2)                              AS sales,
    ROUND(SUM(Profit), 2)                             AS profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2)        AS profit_margin_pct,
    ROUND(100.0 * SUM(IsLoss) / COUNT(*), 2)          AS pct_lines_losing_money
FROM orders
GROUP BY DiscountBand
ORDER BY MIN(Discount);

-- name: q07_loss_making_subcategories_by_discount
-- Business question: Where does heavy discounting hit hardest? (Sub-category x discount band)
SELECT
    "Sub-Category" AS sub_category,
    ROUND(SUM(CASE WHEN Discount > 0.2 THEN Profit ELSE 0 END), 2)  AS profit_on_discount_over_20pct,
    ROUND(SUM(CASE WHEN Discount <= 0.2 THEN Profit ELSE 0 END), 2) AS profit_on_discount_up_to_20pct,
    SUM(CASE WHEN Discount > 0.2 THEN 1 ELSE 0 END)                 AS lines_with_discount_over_20pct
FROM orders
GROUP BY "Sub-Category"
ORDER BY profit_on_discount_over_20pct ASC;

-- name: q08_segment_performance
-- Business question: Which customer segment is most valuable?
SELECT
    Segment,
    COUNT(DISTINCT "Customer ID")                       AS customers,
    ROUND(SUM(Sales), 2)                                AS sales,
    ROUND(SUM(Profit), 2)                               AS profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2)          AS profit_margin_pct,
    ROUND(SUM(Sales) / COUNT(DISTINCT "Customer ID"), 2) AS sales_per_customer
FROM orders
GROUP BY Segment
ORDER BY sales DESC;

-- name: q09_top_10_customers
-- Business question: Who are the top customers by profit contribution?
SELECT
    "Customer Name" AS customer,
    Segment,
    COUNT(DISTINCT "Order ID") AS orders,
    ROUND(SUM(Sales), 2)  AS sales,
    ROUND(SUM(Profit), 2) AS profit,
    RANK() OVER (ORDER BY SUM(Profit) DESC) AS profit_rank
FROM orders
GROUP BY "Customer ID", "Customer Name", Segment
ORDER BY profit DESC
LIMIT 10;

-- name: q10_bottom_10_products
-- Business question: Which individual products lose the most money?
SELECT
    "Product Name" AS product,
    Category,
    "Sub-Category" AS sub_category,
    ROUND(SUM(Sales), 2)  AS sales,
    ROUND(SUM(Profit), 2) AS profit,
    SUM(Quantity)         AS units
FROM orders
GROUP BY "Product ID", "Product Name", Category, "Sub-Category"
ORDER BY profit ASC
LIMIT 10;

-- name: q11_state_profit_bottom_10
-- Business question: Which states are least profitable?
SELECT
    State,
    Region,
    ROUND(SUM(Sales), 2)  AS sales,
    ROUND(SUM(Profit), 2) AS profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) AS profit_margin_pct,
    ROUND(100.0 * AVG(Discount), 2) AS avg_discount_pct
FROM orders
GROUP BY State, Region
ORDER BY profit ASC
LIMIT 10;

-- name: q12_ship_mode
-- Business question: Does shipping mode matter?
SELECT
    "Ship Mode" AS ship_mode,
    COUNT(DISTINCT "Order ID") AS orders,
    ROUND(AVG(ShipDays), 2)    AS avg_ship_days,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) AS profit_margin_pct
FROM orders
GROUP BY "Ship Mode"
ORDER BY avg_ship_days;

-- name: q13_return_rate_by_category
-- Business question: What share of orders is returned?
SELECT
    Category,
    COUNT(DISTINCT "Order ID") AS orders,
    COUNT(DISTINCT CASE WHEN Returned = 'Yes' THEN "Order ID" END) AS returned_orders,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN Returned = 'Yes' THEN "Order ID" END)
          / COUNT(DISTINCT "Order ID"), 2) AS return_rate_pct,
    ROUND(SUM(CASE WHEN Returned = 'Yes' THEN Sales ELSE 0 END), 2) AS sales_returned
FROM orders
GROUP BY Category
ORDER BY return_rate_pct DESC;

-- name: q14_quarterly_seasonality
-- Business question: Which quarter is strongest?
SELECT
    OrderQuarter AS quarter,
    ROUND(SUM(Sales), 2)  AS sales,
    ROUND(SUM(Profit), 2) AS profit,
    ROUND(100.0 * SUM(Sales) / (SELECT SUM(Sales) FROM orders), 2) AS share_of_sales_pct
FROM orders
GROUP BY OrderQuarter
ORDER BY quarter;
