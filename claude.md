# OELP Project Context — Customer Segmentation and Retention Analysis

I am working on an Open Ended Lab Project (OELP) at IIT Palakkad titled:

**Customer Segmentation and Retention Analysis Using Machine Learning and Statistical Modelling**

You are my coding assistant inside VS Code. Help me implement this project step-by-step while preserving the statistical and machine-learning methodology described below.

---

## 1. Project Objective

The project uses a real-world retail transaction dataset to understand customer purchasing behaviour over time.

The overall objective is to:

1. Clean and understand transaction-level retail data.
2. Convert transaction-level data into customer-level behavioural features.
3. Analyse customer purchase timing statistically.
4. Identify customer segments using clustering.
5. Statistically validate whether the discovered segments represent genuinely different customer behaviours.
6. Analyse customer retention using survival analysis.
7. Predict which customers are likely to remain active in a future period.
8. Compare interpretable statistical models with machine-learning models.

The primary dataset is **UCI Online Retail II**, covering roughly two years of transactions from a UK-based online gift retailer. It contains approximately one million transaction records and includes customer identifiers, products, dates, quantities and prices. The dataset contains missing customer identifiers and cancellation records that need to be handled carefully.

---

# 2. Overall Project Pipeline

The project should follow this general pipeline:

RAW TRANSACTIONS
↓
DATA CLEANING
↓
CUSTOMER-LEVEL FEATURE ENGINEERING
↓
STATISTICAL EDA
↓
INTER-PURCHASE TIME DISTRIBUTION MODELLING
↓
CUSTOMER SEGMENTATION
↓
STATISTICAL VALIDATION OF SEGMENTS
↓
SURVIVAL / RETENTION ANALYSIS
↓
FUTURE RETENTION PREDICTION
↓
STATISTICAL MODEL vs ML MODEL
↓
FINAL INTERPRETATION

Do not skip directly to machine learning.

---

# 3. Dataset

Primary dataset:

**UCI Online Retail II**

The raw data is transaction-level.

Important fields include concepts such as:

* Invoice
* Stock/Product code
* Description
* Quantity
* Invoice Date
* Price
* Customer ID
* Country

The exact columns and data types must always be inspected from the actual dataset rather than assumed.

---

# 4. Phase 1 — Data Cleaning

First, preserve the raw dataset.

Create a cleaned/processed version rather than modifying the original data.

Investigate:

* missing values
* duplicate records
* data types
* transaction dates
* Customer IDs
* invoice structure
* cancellation/return transactions
* negative quantities
* zero/negative prices
* extreme transaction values
* product/customer information

Do NOT automatically delete unusual observations.

Every cleaning decision must have a methodological reason because the cleaned data will later be used for:

* customer aggregation
* purchase intervals
* clustering
* survival analysis
* retention prediction

Create a clear data-cleaning log documenting important decisions.

---

# 5. Phase 2 — Customer-Level Feature Engineering

The raw dataset contains transactions, but clustering and retention analysis require customer-level observations.

Aggregate transactions into a customer-level table.

Important features will include:

### Recency

How recently the customer made a purchase.

Conceptually:

Recency = observation/reference date − last purchase date

### Frequency

How frequently the customer purchases.

A reasonable initial definition is the number of unique invoices/orders, but investigate the dataset before deciding.

### Monetary

Total customer spending.

Revenue can be calculated as:

Revenue = Quantity × Price

### Average Order Value

AOV = Total Revenue / Number of Orders

### Inter-Purchase Time

For customers with multiple purchases, calculate the gaps between consecutive purchases.

Example:

Purchase 1 → Purchase 2 = 20 days
Purchase 2 → Purchase 3 = 35 days
Purchase 3 → Purchase 4 = 15 days

From these gaps we may calculate:

* mean gap
* median gap
* standard deviation of gap
* number of gaps
* potentially other temporal features

Do not calculate inter-purchase gaps for customers who do not have sufficient purchase history.

---

# 6. Phase 3 — Statistical Exploratory Data Analysis

Customer-level behavioural variables are expected to be skewed.

Investigate distributions rather than assuming normality.

Use appropriate descriptive statistics such as:

* mean
* median
* standard deviation
* quartiles
* percentiles
* minimum/maximum
* IQR

Investigate relationships between variables.

For example:

* Does purchase frequency relate to spending?
* Does recency relate to monetary value?
* Do frequent customers have shorter purchase gaps?

Use appropriate visualizations and correlation measures.

Before clustering, determine whether transformations are appropriate.

For heavily right-skewed positive variables, investigate transformations such as:

log1p(x)

Do not transform variables automatically; first inspect their distributions.

---

# 7. Phase 4 — Inter-Purchase Time Distribution Modelling

For customers who make multiple purchases, analyse the distribution of inter-purchase time gaps.

Candidate distributions:

* Exponential
* Weibull
* Gamma
* Log-normal

Fit the candidate distributions and compare them using:

* log-likelihood
* AIC
* BIC
* appropriate graphical goodness-of-fit checks
* appropriate statistical goodness-of-fit methods where justified

Be aware that distribution parameters are estimated from the same data being evaluated, so naive goodness-of-fit tests may not be directly appropriate.

The goal is to determine which distribution provides a reasonable representation of customer purchase timing.

---

# 8. Phase 5 — Statistically Justified Inactivity Threshold

Instead of arbitrarily defining inactivity as something like 30, 60 or 90 days, investigate whether the fitted purchase-gap distribution can provide a principled threshold.

The threshold should be derived from the observed purchase behaviour and clearly justified.

Document the reasoning behind whichever definition is eventually selected.

This threshold will later be important for defining retention/inactivity and constructing prediction targets.

---

# 9. Phase 6 — Customer Segmentation

Use customer-level behavioural features for clustering.

Potential features include:

* Recency
* Frequency
* Monetary
* Average Order Value
* Mean inter-purchase gap
* Inter-purchase gap variability
* Other justified customer-level behavioural features

Before clustering:

1. Inspect feature distributions.
2. Apply appropriate transformations where justified.
3. Standardize/scale features where appropriate.
4. Check correlations and redundancy.
5. Ensure that large-scale variables do not dominate distance calculations.

Start with **K-Means** as the primary clustering method.

Do not choose the number of clusters arbitrarily.

Evaluate candidate values of k using methods such as:

* Elbow/inertia
* Silhouette score
* Davies-Bouldin index
* interpretability/business usefulness

An alternative clustering method may be investigated later if useful, but do not unnecessarily complicate the project.

---

# 10. Phase 7 — Interpret Customer Segments

After clustering, profile each segment using customer characteristics.

For example, possible discovered groups could resemble:

* high-value frequent customers
* low-value frequent customers
* infrequent customers
* customers becoming inactive
* historically valuable but currently inactive customers

These labels must be assigned **after examining the cluster characteristics**.

Do not assume the clusters will have these exact profiles.

---

# 11. Phase 8 — Statistical Validation of Clusters

Do not validate clusters only using the same variables used to create them.

Use variables that were not used during clustering, especially future outcomes such as:

* future purchasing behaviour
* future revenue
* future number of purchases
* future activity/retention

The purpose is to determine whether the discovered segments correspond to genuinely different future behaviour rather than simply reflecting structure created by the clustering algorithm.

Because customer outcomes may not be normally distributed, select statistical tests based on the actual data.

Potential methods include:

* Kruskal-Wallis for multiple groups
* appropriate post-hoc pairwise tests
* multiple-comparison correction such as Benjamini-Hochberg/FDR where appropriate
* effect sizes alongside p-values

Do not report statistical significance alone.

---

# 12. Phase 9 — Survival / Retention Analysis

Treat customer inactivity as a time-to-event problem rather than simply a binary label.

Estimate survival curves for different customer segments.

Primary method:

**Kaplan-Meier survival analysis**

The survival function represents the probability that a customer remains active beyond a given time.

Compare segments using an appropriate method such as the:

**Log-rank test**

Correctly handle right censoring.

For example, if the dataset ends while a customer is still active, we do not know whether that customer would eventually become inactive after the observation period.

Do not incorrectly label such customers as churned.

---

# 13. Phase 10 — Cox Proportional Hazards Model

If appropriate, use a Cox proportional hazards model to investigate which customer characteristics are associated with the hazard of becoming inactive.

Potential predictors may include:

* Recency
* Frequency
* Monetary
* Average purchase gap
* Gap variability
* customer segment

Check the proportional hazards assumption before interpreting the model.

Report:

* coefficients
* hazard ratios
* confidence intervals
* statistical significance where appropriate

If the assumptions are violated, investigate alternative approaches rather than blindly using the Cox model.

---

# 14. Phase 11 — Future Retention Prediction

Construct a proper temporal prediction setup.

Avoid random transaction-level train/test splitting because it can introduce temporal leakage.

Instead:

FEATURE WINDOW
↓
historical customer behaviour
↓
CUTOFF DATE
↓
FUTURE WINDOW
↓
retention/activity outcome

Features should be calculated using information available before the prediction cutoff.

The target should be based on behaviour after the cutoff.

Example:

Feature period:
January 2010 → September 2011

Prediction period:
October 2011 → December 2011

The exact dates must be determined from the actual dataset and project design.

---

# 15. Statistical Baseline Model

Use an interpretable statistical model alongside machine-learning models.

For binary future retention/activity, use:

**Logistic Regression**

The statistical model should provide:

* coefficients
* odds ratios where appropriate
* confidence intervals
* p-values
* model diagnostics

The purpose is interpretability, not necessarily maximum predictive performance.

---

# 16. Machine Learning Models

Compare the statistical baseline with machine-learning models.

A reasonable starting point:

### Model 1

Logistic Regression

### Model 2

Random Forest

Additional models can be considered only if they provide meaningful value.

Evaluate using appropriate classification metrics:

* ROC-AUC
* PR-AUC
* Precision
* Recall
* F1-score
* confusion matrix

Do not rely on accuracy alone, especially if the retention classes are imbalanced.

---

# 17. Probability Calibration

Because the model predicts the probability of remaining active, evaluate calibration.

For example:

If the model predicts approximately 80% probability for a group of customers, roughly 80% of those customers should actually remain active if the model is well calibrated.

Investigate:

* calibration curves
* Brier score
* predicted vs observed probabilities

---

# 18. Compare Statistical and ML Interpretations

Compare the features identified by the statistical model with those considered important by the ML model.

For example:

Statistical model:

* Frequency significant
* Recency significant
* Monetary significant

ML model:

* Recency highly important
* Frequency highly important
* Monetary moderately important

Agreement can provide supporting evidence.

Disagreement should be investigated rather than ignored.

For tree-based models, prefer robust interpretation methods such as permutation importance or SHAP when appropriate.

---

# 19. Code Architecture

Keep the project modular.

A possible structure:

project/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── src/
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── statistical_analysis.py
│   ├── clustering.py
│   ├── survival_analysis.py
│   └── prediction.py
│
├── models/
│
├── reports/
│   └── figures/
│
└── README.md

The exact structure can be modified if there is a better justified approach.

---

# 20. Coding Rules

When assisting me:

1. Work incrementally.
2. Do not generate the entire project at once.
3. Explain code before or alongside implementation.
4. Prefer simple, readable Python.
5. Use pandas/numpy/scikit-learn and appropriate statistical libraries.
6. Avoid unnecessary libraries.
7. Never silently modify methodological decisions.
8. Never assume a column exists—inspect the dataset first.
9. Never delete data without explaining why.
10. Watch for data leakage in all predictive modelling.
11. Keep train/test temporal separation correct.
12. Save important intermediate datasets where useful.
13. Make the analysis reproducible.
14. Use functions for repeated operations.
15. Add comments only where they improve understanding.
16. When there are multiple valid approaches, explain the trade-offs and recommend one.

---

# 21. Important Project Principle

This is an **academic OELP**, not just a coding project.

The goal is not simply to obtain the highest ML accuracy.

Every major modelling decision should answer:

**Why is this statistically appropriate for this dataset and research question?**

The final project should be able to explain:

* what we did,
* why we did it,
* what assumptions were made,
* what evidence supports the decisions,
* what the limitations are,
* and what the results mean.

When uncertain about a methodological decision, flag it explicitly instead of silently choosing an arbitrary solution.

---

# 22. Current Development Strategy

We will proceed in this order:

**Step 1:** Dataset loading and initial audit
**Step 2:** Data cleaning
**Step 3:** Customer-level feature engineering
**Step 4:** Customer-level EDA
**Step 5:** Inter-purchase distribution modelling
**Step 6:** Inactivity threshold
**Step 7:** Customer clustering
**Step 8:** Cluster interpretation and statistical validation
**Step 9:** Survival analysis
**Step 10:** Retention prediction
**Step 11:** Statistical vs ML comparison
**Step 12:** Final report/dashboard

At every stage, stop and inspect results before moving to the next stage.

**Current stage: Step 1 — Dataset loading and initial audit.**
