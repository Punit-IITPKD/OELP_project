# Data Cleaning – Progress Report


- Loaded and performed an initial audit of the **UCI Online Retail II dataset**.
- Checked dataset structure, data types, descriptive statistics, and missing values.
- Investigated each feature individually: `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, and `Country`.
- Analysed invoice types and identified `C` invoice records as cancellation/return-related and `A` records as special accounting adjustments.
- Investigated negative quantities and identified non-`C` negative records as mainly operational/inventory-related adjustments.
- Analysed `Price` distribution, including negative, zero, and extreme values.
- Identified negative-price records as `Adjust bad debt` accounting adjustments.
- Investigated zero-price transactions and found that some are associated with valid customer/product records, so they were not removed automatically.
- Investigated missing `Customer ID` values and established that they cannot be reliably imputed for customer-level analysis.
- Verified `InvoiceDate` as a valid datetime feature covering approximately **December 2009 – December 2010**.
- Documented preliminary cleaning decisions based on **business meaning rather than arbitrary outlier thresholds**.
- Kept the **original raw dataset unchanged** throughout the investigation.

## Preliminary Cleaning Decisions

- Missing `Customer ID` → exclude from customer-level analysis.
- Non-`C` negative quantities → exclude as operational/inventory adjustments.
- Negative-price `Adjust bad debt` records → exclude.
- Zero-price records → retain initially and investigate further.
- Extreme prices → investigate based on transaction meaning rather than automatically removing them.
- `StockCode` and `InvoiceDate` → retain without modification.

## Creating Customer-Level Features

The raw dataset contains individual transactions, while clustering and retention analysis require one observation per customer. Transactions will therefore be aggregated into a customer-level table.

### Recency

Measures how recently a customer made a purchase.

**Recency = observation/reference date − last purchase date**

### Frequency

Measures how often a customer purchases. A reasonable initial definition is the number of unique invoices (orders); this definition should be checked against the dataset before it is finalized.

### Monetary

Measures total customer spending. Transaction revenue can be calculated as:

**Revenue = Quantity × Price**

Customer monetary value is the sum of transaction revenue across that customer's orders.

### Average Order Value

Measures average spending per order:

**AOV = Total Revenue / Number of Orders**

### Inter-Purchase Time

For customers with multiple purchases, calculate the time gaps between consecutive purchases. For example, the gaps may be 20 days, 35 days, and 15 days.

These gaps can be summarized using the mean, median, and standard deviation, along with the number of gaps. Customers without sufficient purchase history should not receive inter-purchase gap measures.


