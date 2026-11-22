# PLP Data Analytics Week 3: Duka Sales Exploration and Agent Network Cleanup

## Overview
This repository contains end-to-end data analytics solutions for two consultancy engagements:
1. **Engagement 1 (Duka Electronics):** Half-year sales exploration (January–June 2026), branch revenue benchmarking, and Excel model reconciliation.
2. **Engagement 2 (Mobile Money Agent Network):** Data quality audit across six dimensions, an automated cleaning pipeline module, and operational county summaries.

---

## Duka Electronics Executive Summary
* In the first half of 2026, Duka Electronics generated a total revenue of **KES 71,792,500.00** across **1,000** customer orders.
* The Nairobi branch was the top-performing location, delivering **KES 26,106,100.00** in sales and contributing **36.36%** of overall business revenue.
* Laptops proved to be the primary revenue engine, contributing **KES 41,535,000.00** (57.85% of total sales) from **639** units sold, despite Tablets leading in unit volume at **691** units.
* Weekday operations drove **72.23%** of total revenue with **723** orders, while maintaining an average order revenue of **KES 71,723.65** compared to **KES 71,972.20** on weekends.
* Revenue peaked in April at **KES 13,518,300.00**, surpassing the slowest month of June (**KES 10,903,400.00**) by **23.98%**.

---

## Agent Network Data: Before-and-After Row Counts
* **Raw Transaction Extract:** 612 rows
* **Deduplicated Transaction Count:** 600 rows (12 duplicate transaction rows removed)
* **Missing/Invalid Amounts Imputed:** 20 records (imputed using group-specific median by transaction type)
* **Statistical Outliers Flagged:** 53 records (including 5 occurrences of KES 250,000)
* **Transactions with Unregistered Agents (AG099):** 7 records (preserved and labeled as `Unknown` county)
* **Final Verified Clean Output:** 600 rows, 8 columns (`outputs/agent_transactions_clean.csv`)

---

## Instructions: Regenerating Data & Running Notebooks

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Regenerate Synthetic Datasets
Run `generate_data.py` to regenerate the raw datasets:
```bash
python generate_data.py
```
*(Creates `duka_sales.csv` with seed 2026, and `agents.csv` and `agent_transactions.csv` with seed 44. Note: these raw CSVs are untracked in git).*

### 3. Run Notebooks
Open your Jupyter environment and run every notebook top-to-bottom:
* `duka_sales_exploration.ipynb`: Analyzes sales performance and exports `outputs/premium_online_coast_capital.csv`.
* `agent_cleanup.ipynb`: Imports `cleaning_pipeline.py`, runs the data quality audit, and exports `outputs/agent_transactions_clean.csv`.

### 4. Build Excel Report
```bash
python build_excel.py
```
Outputs `excel/duka_branch_summary.xlsx` with formulas matching the notebook totals.