# TEST01 Report: Audit and Validation of Customer-Level Feature Engineering

**Project Title:** Customer Segmentation and Retention Analysis Using Machine Learning and Statistical Modelling  
**Date of Audit:** October 24, 2026  
**Auditor / Evaluator:** Antigravity AI Assistant  
**Repository Path:** `c:/Manthan/Customer_segmentation_retention/main_project`  
**Target Notebooks:** `notebooks/01_EDA_analysis.ipynb`, `notebooks/02_Customer_feature_engineering.ipynb`  
**Status for Next Stage (Notebook 03):** **READY (PASS with Specific Scope Decisions Documented)**

---

## 1. Executive Summary

This audit inspected the data-cleaning pipeline and customer-level feature engineering across `notebooks/01_EDA_analysis.ipynb` and `notebooks/02_Customer_feature_engineering.ipynb`. The goal was to validate the data structures, fix logical inconsistencies in feature formulations (such as counting cancellations as purchases, negative AOV, and erroneous same-invoice purchase intervals), ensure cross-platform reproducibility, and verify that the resulting feature matrix is sound for distribution fitting and downstream customer segmentation.

### Key Actions & Discoveries:
1. **Reproducibility & Paths:** Replaced an absolute Windows user path (`C:/Users/ASUS/Desktop/...`) in Notebook 02 with a robust 3-tier fallback that resolves properly from `notebooks/`, repository root, or workspace root. Removed in-cell `%pip install` invocations.
2. **Cancellation Contamination in Purchase Features:** In the original implementation, `Frequency` counted all invoices including cancellations (`C...`), `Recency` evaluated the timestamp of cancellations if they were a customer's last interaction, and `AOV` divided net revenue by total invoices. This produced negative AOV values for 100 customers and assigned positive purchase frequencies to 69 customers who had **zero** valid purchases in the dataset.
3. **Same-Invoice Sub-Minute Interval Artifact:** The original inter-purchase gap calculation used `drop_duplicates(["Customer ID", "Invoice", "InvoiceDate"])`. For invoices with items recorded across consecutive minutes (e.g., 09:51 and 09:52), this produced artificial 1-minute purchase intervals for 4 single-order customers. Aggregating to unique order timestamps `(Customer ID, Invoice)` resolved this, ensuring exactly 1,421 single-order customers have `NaN` gaps and all 2,893 repeat customers have valid intervals.
4. **Dataset Scope Clarification:** The raw dataset `online_retail_raw_data.xlsx` contains two sheets: `Year 2009-2010` (525,461 rows) and `Year 2010-2011` (541,910 rows). The current pipeline and `online_retail_cleaned_data.csv` intentionally operate solely on **Year 1 (December 2009 – December 2010)** (410,763 rows, 4,383 unique customers). This scope is documented and highlighted for a conscious project decision.
5. **Validation Outcome:** All 11 automated unit and integration tests passed (100% PASS). Both notebooks now execute end-to-end without errors. The feature table for 4,314 purchase-eligible customers has been saved to `data/processed/customer_features.csv`.

---

## 2. Repository and Dataset Details

### Directory Structure & File Inventory
- **Repository Root:** `c:/Manthan/Customer_segmentation_retention/main_project/`
  - `data/raw/online_retail_raw_data.xlsx` (45.6 MB Excel file, 2 sheets)
  - `data/processed/online_retail_cleaned_data.csv` (36.8 MB CSV file, 410,763 rows)
  - `data/processed/customer_features.csv` (Generated validated customer feature table)
  - `notebooks/01_EDA_analysis.ipynb` (Cleaned transaction-level EDA)
  - `notebooks/02_Customer_feature_engineering.ipynb` (Customer feature creation & transformations)
  - `notebooks/pandas_profinling.ipynb` (Data profiling exploratory notebook)
  - `notebooks/report.md` (Original preliminary cleaning report)
  - `claude.md` (Methodological context and multi-phase roadmap)
  - `requirements.txt` (Environment dependency specification)

### Dataset Dimensions & Date Coverage
| Dataset | Format | Rows | Columns | Date Range | Unique Customers |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Raw Excel: Sheet 1 (Year 2009-2010)** | `.xlsx` | 525,461 | 8 | 2009-12-01 07:45 to 2010-12-09 20:01 | 4,383 (non-null) + 107,927 missing |
| **Raw Excel: Sheet 2 (Year 2010-2011)** | `.xlsx` | 541,910 | 8 | 2010-12-01 08:26 to 2011-12-09 12:50 | 4,372 (non-null) |
| **Processed Cleaned Transactions** | `.csv` | 410,763 | 8 | 2009-12-01 07:45 to 2010-12-09 20:01 | 4,383 (0 missing) |
| **Purchase-Only Subset (`~Invoice.str.startswith('C')`)** | in-memory | 400,947 | 8 | 2009-12-01 07:45 to 2010-12-09 20:01 | 4,314 |
| **Cancellation Subset (`Invoice.str.startswith('C')`)** | in-memory | 9,816 | 8 | 2009-12-01 09:28 to 2010-12-09 15:46 | 1,607 (including 69 pure cancellation customers) |

### Key Columns
- `Invoice`: Nominal 6-digit transaction identifier; prefix `C` denotes cancellation/return.
- `StockCode`: Nominal 5-digit product code or operational code (e.g., `TEST001`, `POST`, `D`).
- `Description`: Product description (2,928 missing in raw sheet 1; 0 missing in cleaned CSV).
- `Quantity`: Numeric item count per invoice line. Positive for purchases, negative for cancellations.
- `InvoiceDate`: Transaction timestamp (datetime64[ns]).
- `Price`: Unit price in GBP (£).
- `Customer ID`: Unique 5-digit customer identifier (float/int).
- `Country`: Customer geographic country (40 distinct countries).

---

## 3. Initial Audit Findings

### Issue A: Hard-Coded Local Environment Paths
- **Evidence:** `notebooks/02_Customer_feature_engineering.ipynb` (Cell 1) hard-coded:  
  `data_path = Path("C:/Users/ASUS/Desktop/OELP project/data/processed/online_retail_cleaned_data.csv")`
- **Impact:** Immediate `FileNotFoundError` on any other machine or container.

### Issue B: Pure-Cancellation Customers Contaminating Purchase Frequency & Recency
- **Evidence:** Exactly 69 customers in `online_retail_cleaned_data.csv` have **zero** valid purchase invoices and only cancellation invoices (e.g., Customer `17399` with 1 cancellation invoice for -£25,111.09; Customer `18023` with -£3,248.86).
- **Previous Code:**
  ```python
  frequency = df.groupby("Customer ID")["Invoice"].nunique()
  last_purchase = df.groupby("Customer ID")["InvoiceDate"].max()
  recency = (reference_date - last_purchase).dt.days
  ```
- **Impact:** 
  - The 69 cancellation-only customers were assigned `Frequency = 1` or `2` (as if they bought items).
  - Their `Recency` was calculated from their cancellation date rather than a purchase date.
  - In general, repeat buyers who returned an item after their last purchase had their `Recency` improperly shortened by the return date.

### Issue C: Inconsistent and Distorted Average Order Value (AOV)
- **Previous Code:**
  ```python
  monetary = (
      df.assign(Revenue=df["Quantity"] * df["Price"])
      .groupby("Customer ID")["Revenue"]
      .sum()
  )
  customer_features["AOV"] = (
      customer_features["Monetary"] / customer_features["Frequency"]
  )
  ```
- **Impact:**
  - `Monetary` represented Net Revenue (Gross Purchases minus Returns).
  - 90 customers had negative Net Revenue.
  - 100 customers had `AOV <= 0` (including severe negative outliers down to -£25,111.09), creating severe left skewness (-15.87) in AOV.
  - Denominator (`Frequency`) added cancellation invoices, artificially diluting average basket size.

### Issue D: Multi-Line Invoices Spanning Consecutive Minutes Creating False Inter-Purchase Gaps
- **Previous Code:**
  ```python
  customer_invoice_dates = (
      purchase_df[["Customer ID", "Invoice", "InvoiceDate"]]
      .drop_duplicates()
      .sort_values(["Customer ID", "InvoiceDate"])
  )
  ```
- **Impact:**
  - For customers like `13023` (Invoice `513813`), line items were registered across `09:51` and `09:52`. Because `InvoiceDate` differed, `drop_duplicates` kept both rows, creating a 1-minute `diff()` gap (0.00069 days).
  - This erroneously assigned an inter-purchase gap to 4 customers who only placed a single order in reality.

### Issue E: In-Cell Package Installation
- **Evidence:** Notebook 02 contained `%pip install -U scikit-learn` in Cell 62.
- **Impact:** Interrupts clean headless execution, introduces network dependencies, and clutters output.

### Issue F: Scope Restriction to Year 1
- **Evidence:** The raw Excel file contains both `Year 2009-2010` and `Year 2010-2011`. Notebook 01 loaded only sheet 1 via `pd.read_excel(data_path)` without specifying `sheet_name`.
- **Impact:** The resulting cleaned data covers December 2009 to December 2010 (1 year, 4,383 customers) rather than the 2-year combined series (roughly 1 million transactions and ~5,800 customers).

---

## 4. Changes Made

| File & Section | Previous Behaviour | Corrected Behaviour | Rationale |
| :--- | :--- | :--- | :--- |
| `02_Customer_feature_engineering.ipynb`<br>Cell 1 (Data Loading) | Hard-coded path `C:/Users/ASUS/Desktop/...` | 3-tier relative resolution: checks `../data/processed/...`, `data/processed/...`, then `main_project/data/processed/...` | Eliminates machine dependency; works from notebooks directory or workspace root. |
| `01_EDA_analysis.ipynb`<br>Cell 1 (Data Loading) | Path `../data/raw/online_retail_raw_data.xlsx` | 3-tier relative resolution: checks `../data/raw/...`, `data/raw/...`, then `main_project/data/raw/...` | Ensures Notebook 01 runs reliably from both root and subdirectories. |
| `02_Customer_feature_engineering.ipynb`<br>Cells 4-6 (Recency) | `last_purchase` used all rows in `df` (including `C` cancellation invoices). | Filtered `purchase_df = df[~df['Invoice'].astype(str).str.startswith('C')]`; calculated `last_purchase` strictly on valid purchases. | Prevents cancellations from acting as purchase events or artificially shrinking Recency. |
| `02_Customer_feature_engineering.ipynb`<br>Cell 11 (Frequency) | Counted all distinct invoices (`df.groupby('Customer ID')['Invoice'].nunique()`). | Counted distinct purchase invoices (`purchase_df.groupby('Customer ID')['Invoice'].nunique()`). | Reflects true purchasing cadence; eliminates fake purchase counts for 69 cancellation-only customers. |
| `02_Customer_feature_engineering.ipynb`<br>Cell 15 (Monetary) | Single column `Monetary` represented net revenue with negative values. | Defined `Monetary` as gross purchase revenue (`purchase_df['Quantity'] * purchase_df['Price']`), preserving non-negativity for valid buyers. Net revenue is retained for auditing. | Preserves true customer purchasing scale and allows valid log/Power transformations. |
| `02_Customer_feature_engineering.ipynb`<br>Cell 20 (AOV) | Divided net monetary by total invoices, resulting in 100 negative or zero values. | Calculated order-level gross revenue on valid purchase invoices: `order_revenue.groupby('Customer ID')['Revenue'].mean()`. | Guarantees true Average Order Value; eliminates negative values and distortion from return transactions. |
| `02_Customer_feature_engineering.ipynb`<br>Cells 26-28 (Inter-Purchase Gaps) | Deduplicated on `['Customer ID', 'Invoice', 'InvoiceDate']`, keeping sub-minute lines within single invoices. | Aggregated by `['Customer ID', 'Invoice']` using `.min()` of `InvoiceDate` before sorting and computing `.diff()`. | Eliminates false 1-minute gaps within single orders. Exactly aligns repeat buyers with gap availability. |
| `02_Customer_feature_engineering.ipynb`<br>Cell 40 (Cancellation Rate) | Reindexed cancellation count on total invoice index. | Denominator computed as `Frequency + Cancellation_Count` for purchase-eligible customers. | Safely bounded in `[0, 1]` without divide-by-zero errors. |
| `02_Customer_feature_engineering.ipynb`<br>Cell 62 (Dependency) | Executed `%pip install -U scikit-learn`. | Replaced with comment acknowledging project environment installation. | Removes non-reproducible shell executions from the notebook. |
| `main_project/requirements.txt`<br>(New File) | No explicit requirements file existed in repository. | Added explicit pinned/minimum dependencies for pandas, numpy, scipy, statsmodels, scikit-learn, lifelines, ydata-profiling, xgboost, lightgbm. | Provides single-command environment reproducibility. |

---

## 5. Feature Definitions

### 1. Recency
$$\text{Recency} = \text{Reference Date} - \max(\text{InvoiceDate}_{\text{valid purchases}})$$
- **Reference Date:** `2010-12-10 20:01:00` (Dataset max invoice datetime + 1 day).
- **Rule:** Measured in integer days. Applies only to customers with at least 1 valid purchase order. Strictly non-negative.

### 2. Frequency
$$\text{Frequency} = \text{Count}(\text{Distinct Invoices}_{\text{valid purchases}})$$
- **Rule:** Counts unique purchase order numbers (excluding those starting with `C` or adjustments). Must be an integer $\ge 1$.

### 3. Monetary (Gross vs. Net)
$$\text{Monetary}_{\text{Gross}} = \sum (\text{Quantity} \times \text{Price}) \quad \text{for } \text{Invoice} \not\subset \{C\dots\}$$
$$\text{Monetary}_{\text{Net}} = \sum (\text{Quantity} \times \text{Price}) \quad \text{across all customer records}$$
- **Primary Clustering Feature:** $\text{Monetary}_{\text{Gross}}$ represents purchasing volume and avoids negative inputs.
- **Audit/Retention Metric:** $\text{Monetary}_{\text{Net}}$ reflects commercial margin after customer returns.

### 4. Average Order Value (AOV)
$$\text{AOV} = \frac{\sum_{i=1}^{K} \text{OrderRevenue}_i}{\text{Frequency}} = \frac{\text{Monetary}_{\text{Gross}}}{\text{Frequency}}$$
- **Rule:** Calculated strictly on valid purchase invoices. Bounded below at $0.00$.

### 5. Median Inter-Purchase Days
$$\text{InterPurchaseDays}_{i} = \frac{\text{InvoiceDate}_i - \text{InvoiceDate}_{i-1}}{86400 \text{ seconds}}$$
$$\text{Median\_InterPurchase\_Days} = \text{Median}(\{\text{InterPurchaseDays}_i\})$$
- **Eligibility:** Evaluated across distinct purchase invoices ordered chronologically.
- **Condition:** Defined only for customers with $\text{Frequency} \ge 2$. Customers with $\text{Frequency} = 1$ receive $\text{NaN}$ (not $0$).

### 6. Cancellation Rate
$$\text{Cancellation\_Rate} = \frac{\text{Distinct Cancellation Invoices}}{\text{Distinct Purchase Invoices} + \text{Distinct Cancellation Invoices}}$$
- **Rule:** Measures the proportion of customer transactions that resulted in a cancellation or return. Value lies in $[0.0, 1.0)$.

---

## 6. Before-and-After Statistics

### Summary Statistics Comparison

| Metric / Feature | Original Implementation (4,383 Customers) | Corrected Implementation (4,314 Purchase Customers) | Impact / Correction Note |
| :--- | :--- | :--- | :--- |
| **Eligible Customer Count** | 4,383 | 4,314 | Excluded 69 pure cancellation customers with 0 purchases. |
| **Recency (Mean ± Std)** | 91.40 ± 96.95 days | 91.27 ± 96.95 days | Cancellations no longer artificially shorten recency. |
| **Recency Range** | [1, 374] days | [1, 374] days | Maintained consistent observation window. |
| **Recency Skewness** | +1.275 | +1.281 (Raw) $\rightarrow$ **-0.055 (Yeo-Johnson)** | Highly symmetric after Yeo-Johnson transformation. |
| **Frequency (Mean ± Std)** | 5.38 ± 11.87 orders | 4.45 ± 8.01 orders | Shifted from total transactions to valid purchase orders. |
| **Frequency Range** | [1, 270] | [1, 205] | Removed 69 phantom frequencies. |
| **Frequency Skewness** | +10.586 | +10.549 (Raw) $\rightarrow$ **+1.182 (log1p)** | Extreme positive skew dramatically reduced. |
| **Monetary (Mean ± Std)** | £1,897.07 ± £8,485.66 (Net) | £2,039.46 ± £8,531.06 (Gross) | Reflects true purchasing revenue. |
| **Negative Monetary Count** | 90 customers (< £0) | **0 customers** (£0.00 only for 2 test items) | Eliminates negative value distortion. |
| **Monetary Skewness** | +24.706 | +24.005 (Raw) $\rightarrow$ **-0.015 (Yeo-Johnson)** | Near-zero skewness after Yeo-Johnson. |
| **AOV (Mean ± Std)** | £287.88 ± £479.52 | £376.20 ± £443.34 | True basket order value without cancellation penalties. |
| **AOV Range** | [-£25,111.09, £11,880.84] | [£0.00, £11,880.84] | Negative AOV values completely eliminated. |
| **AOV Skewness** | **-15.867** (Severe left skew) | **+11.280** (Raw) $\rightarrow$ **+0.040 (Yeo-Johnson)** | Corrected from negative skew to near-normal distribution. |
| **Median Inter-Purchase (Mean)**| 65.59 days (2,897 non-null) | 65.79 days (2,893 non-null) | 4 false 1-minute same-order intervals removed. |
| **Missing Inter-Purchase Gaps** | 1,486 (1,417 single + 69 pure cancel) | **1,421 (Exactly 100% of single-order buyers)** | Perfectly aligns with repeat purchase condition. |
| **Cancellation Rate (Mean)** | 13.59% | 12.21% (Max: 83.3%) | 69 pure cancellation 100% rates separated. |

---

## 7. Test Results

All assertions were executed programmatically against `data/processed/online_retail_cleaned_data.csv` using `scratch/execute_feature_engineering.py`.

| Test ID | Test Name | Expected Behaviour | Actual Result | Status | Notes |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **T01** | Duplicate Customer IDs | 0 duplicates | `0` | **PASS** | `Customer ID` index is strictly unique. |
| **T02** | Customer Population Scope | Exactly 4,314 purchase-eligible customers | `4,314` | **PASS** | 69 pure-cancellation records excluded from purchase feature matrix. |
| **T03** | Recency Boundary | $\text{Recency} \ge 0$ | Min: `1`, Max: `374` | **PASS** | Strictly non-negative integer days relative to reference date. |
| **T04** | Frequency Integer & Positivity | Positive integer ($\text{Freq} \ge 1$) | Min: `1`, all integer | **PASS** | All eligible customers have at least 1 valid purchase order. |
| **T05** | Purchase Invoice Frequency Count | Matches count of distinct non-`C` invoices | Exact match across all sample IDs | **PASS** | Verified against transaction-level raw purchase IDs. |
| **T06** | AOV Consistency | $\text{AOV} = \frac{\text{Monetary}_{\text{Gross}}}{\text{Frequency}}$ | Exact match (`np.allclose = True`) | **PASS** | Confirms invoice-level mean equals aggregate quotient. |
| **T07** | Inter-Purchase Non-Negativity | Minimum interval $\ge 0$ | Min: `0.0007` days | **PASS** | Chronological ordering verified; no negative time intervals. |
| **T08** | Inter-Purchase Missing Gap Count | Exactly matches $\text{Frequency} == 1$ | `1,421` single buyers = `1,421` NaN gaps | **PASS** | Zero discrepancy. No single-order customer has an artificial gap. |
| **T09** | Cancellation Rate Boundary | $0.0 \le \text{Rate} \le 1.0$ | Min: `0.0`, Max: `0.833` | **PASS** | Bounded; no divide-by-zero errors. |
| **T10** | Absence of Infinite Values | 0 infinite values across all features | `0` `inf` / `-inf` values | **PASS** | All numerical features finite and well-conditioned. |
| **T11** | Transformation Execution | Valid convergence on all non-null series | Yeo-Johnson & log1p converged | **PASS** | Transformed skewness: Recency (-0.05), Freq (1.18), Monetary (-0.01), AOV (0.04), InterPurchase (-0.01). |

---

## 8. Notebook Execution

Both notebooks were tested and verified from clean kernel states:

- **Notebook 01 (`01_EDA_analysis.ipynb`):**
  - **Environment:** Python 3.11.0 (64-bit), Windows 11.
  - **Runtime & Status:** **Executed with 0 errors.**
  - **Memory & Shape:** Loaded 525,461 rows, 8 columns from `Year 2009-2010` sheet. Audited invoice prefixes (`10,206` 'C' cancellations, `3` 'A' adjustments), zero prices, negative quantities, and missing customer IDs (107,927).
- **Notebook 02 (`02_Customer_feature_engineering.ipynb`):**
  - **Environment:** Python 3.11.0 (64-bit), Windows 11.
  - **Runtime & Status:** **Executed with 0 errors.**
  - **Output Verification:** Successfully produced all summary tables, correlation heatmaps, distribution plots, and final feature DataFrames (`customer_features`: 4,314 rows $\times$ 10 cols; `clustering_features`: 4,314 rows $\times$ 6 cols).

---

## 9. Outstanding Issues & Methodological Decisions

Before proceeding to Notebook 03 (Distribution Modelling) and Notebook 04 (Customer Segmentation / K-Means), the following three decisions should be finalized:

### Decision 1: Time Horizon Scope (1 Year vs. 2 Years)
- **Context:** The raw dataset `online_retail_raw_data.xlsx` has two sheets (`Year 2009-2010` and `Year 2010-2011`). The current cleaned data and notebooks only process Year 1.
- **Impact on Next Stages:**
  - *Option A (Keep 1 Year - Recommended for current timeline):* Fast, fully validated, 4,314 customers. Ideal for modeling inter-purchase distribution and segmenting.
  - *Option B (Combine Both Years):* Would yield ~800,000 cleaned transactions and ~5,800 customers. Requires re-running cleaning across both sheets, but provides a natural split for temporal retention prediction (Year 1 = feature window, Year 2 = observation window).
- **Status:** **NEEDS DECISION** by project lead.

### Decision 2: Handling Missing Inter-Purchase Gaps for Clustering
- **Context:** 1,421 customers have only 1 order, meaning their `Median_InterPurchase_Days` is legitimately `NaN`.
- **Recommendation:**
  - *Do NOT impute with zero* (zero implies instantaneous repeat buying, which is the exact opposite of reality).
  - For **distribution modelling (Notebook 03)**: Fit candidate distributions (Exponential, Weibull, Gamma, Log-Normal) on the observed positive gaps from repeat buyers ($N = 2,893$).
  - For **K-Means segmentation (Notebook 04)**: Either segment single-purchase customers as a distinct rule-based cohort ("One-time Buyers") or use RFM (Recency, Frequency, Monetary, AOV) for clustering and evaluate repeat timing within clusters.

### Decision 3: Zero-Spending Test Customers
- **Context:** Customers `14103` and `14827` only purchased `StockCode: TEST001` with `Price = £0.00`.
- **Recommendation:** Filter these 2 test customer accounts out of behavioral clustering as they represent system testing rather than genuine consumer behavior.

---

## 10. Recommendation for Notebook 03

### Verdict: **APPROVED TO PROCEED TO NOTEBOOK 03**
The customer-level feature engineering is now logically consistent, statistically sound, and completely reproducible.

### Next Steps for Notebook 03:
1. Extract all valid order-to-order intervals (`order_inv_dates['InterPurchaseDays']`).
2. Fit the candidate statistical distributions:
   - Exponential ($\lambda$)
   - Weibull ($k, \lambda$)
   - Gamma ($\alpha, \beta$)
   - Log-Normal ($\mu, \sigma$)
3. Evaluate goodness-of-fit via Log-Likelihood, AIC, BIC, and empirical vs. theoretical QQ-plots.
4. Derive a statistically justified inactivity threshold (e.g., 90th or 95th percentile of the fitted inter-purchase distribution) to define customer churn/retention in later phases.

---

## 11. Files Changed

1. `main_project/notebooks/02_Customer_feature_engineering.ipynb`
   - *Modified:* Fixed path fallback, separated valid purchase transactions from cancellations, corrected Recency, Frequency, Gross Monetary, order-level AOV, invoice-level inter-purchase intervals, and cancellation rate. Removed `%pip install`.
2. `main_project/notebooks/01_EDA_analysis.ipynb`
   - *Modified:* Added 3-tier relative path fallback for `online_retail_raw_data.xlsx`.
3. `main_project/notebooks/01_EDA_analysis_original.ipynb`
   - *Created:* Complete untouched backup copy of original Notebook 01.
4. `main_project/notebooks/02_Customer_feature_engineering_original.ipynb`
   - *Created:* Complete untouched backup copy of original Notebook 02.
5. `main_project/requirements.txt`
   - *Created:* Pinned and documented environment dependencies.
6. `main_project/data/processed/customer_features.csv`
   - *Created:* Validated customer feature table containing both raw and transformed features for all 4,314 eligible customers.
7. `main_project/TEST01_Report.md` & `c:/Manthan/Customer_segmentation_retention/TEST01_Report.md`
   - *Created:* Full comprehensive validation and test report for assistant and human review.
