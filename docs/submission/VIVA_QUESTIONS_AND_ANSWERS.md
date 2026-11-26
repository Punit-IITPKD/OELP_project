# Viva Questions and Answers

These answers are written for spoken explanation. Project values refer to the saved historical evaluation, not to a current retail population.

## Research framing and data

### 1. What is the central research question?

The project asks how historical transaction records can support a reproducible analysis of customer segments, repeat-purchase timing, finite-horizon forecasts, reliability, and retention planning. It keeps descriptive, predictive, reliability, and hypothetical outputs separate.

### 2. Why did you study customer retention?

Repeat purchasing is commercially important, but a non-contractual retailer does not observe a formal cancellation. The project therefore studies observable purchase behavior within finite horizons rather than asserting that a customer has permanently churned.

### 3. What dataset did you use?

The project uses Year 1 of the UCI Online Retail II transaction dataset, from 1 December 2009 through 9 December 2010. The full source contains more than one year; only the project’s stated Year 1 subset is used here.

### 4. Why is the dataset called non-contractual?

Customers are not shown as having a formal subscription or cancellation event. A gap without a transaction cannot be interpreted as a confirmed end of the relationship.

### 5. What is the official prediction cutoff?

The saved TEST cutoff is 10 September 2010. Predictor transactions must be strictly before that cutoff; transactions on the cutoff date are excluded from feature history. Outcomes are evaluated over separate 30-, 60-, or 90-day windows.

### 6. Why are the TEST horizons not directly interchangeable?

They use different outcome windows and different event prevalence. Although each Purchase Clock horizon has 3,373 customers, the 30-, 60-, and 90-day targets are not the same outcome.

### 7. How did you avoid temporal leakage?

TRAIN and VAL cutoffs are chosen so their outcome windows mature before selection; TEST is held out at the official cutoff. Predictor histories use transactions strictly before each cutoff, matching the exclusive cutoff in `src/temporal_framework.py`. The saved split registry records the cutoff and target end date for each horizon.

### 8. What does left-truncated history mean here?

The file begins at a calendar date, but customers may have bought from the retailer before the file started. The first observed order is not necessarily the customer's true first purchase or acquisition date.

### 9. How were missing customer identifiers handled?

Customer IDs were not imputed. Without a reliable identifier, a transaction cannot be assigned to an individual customer history. The exploratory notebook found 107,927 rows with a missing Customer ID.

### 10. How did you treat returns and cancellations?

The notebooks inspect cancellation invoice prefixes and negative quantities before creating purchase histories. Customer-linked return/cancellation behavior is retained where relevant; non-cancellation negative-quantity adjustments are excluded from the cleaned purchase history under the documented rule.

## Methods

### 11. Why use RFM?

RFM gives a compact summary of how recently a customer purchased, how often, and how much they spent. It is useful for descriptive grouping and communication, but it is not a complete behavioral model and does not prove future risk or treatment response.

### 12. How does K-means work?

K-means assigns each standardized feature vector to a cluster center and minimizes the sum of squared within-cluster distances. The result depends on the feature representation, scaling, initialization, and selected cluster count.

### 13. Why did the descriptive segmentation use two clusters?

The saved Notebook 04 analysis selected K=2 under its documented validation and stability procedure for the full-period descriptive cohort of 4,312 customers. The labels remain retrospective and descriptive.

### 14. What does ARI measure?

Adjusted Rand Index measures agreement between two cluster labelings while adjusting for chance. The reported seed ARI summarizes assignment stability across initializations; it does not show that the clusters predict churn or improve marketing.

### 15. What is an interpurchase distribution?

It describes the observed time gaps between consecutive purchases for customers with enough purchase history. The fit summarizes those recorded gaps; censoring and short histories still constrain interpretation.

### 16. Why compare Gamma and other gap distributions?

Different parametric families represent different gap shapes. AIC compares relative fit among the candidate distributions evaluated in the notebook. The best AIC candidate is not automatically a universal model for future customer activity.

### 17. What does the 101.9-day P90 mean?

It is the empirical 90th percentile of observed interpurchase gaps in the saved analysis. It is descriptive only. It is not a permanent churn label, causal threshold, or validated alert rule.

### 18. What is a hazard model?

A hazard model estimates the conditional chance of an event in an interval, given that it has not occurred in earlier intervals and given the available features. The saved Purchase Clock uses logistic hazards over 10-day intervals, with nine intervals spanning up to 90 days.

### 19. How does the Purchase Clock turn hazards into a horizon probability?

For H ∈ {30, 60, 90}, the saved formula is **P(Tᵢ ≤ H | Xᵢ) = 1 − ∏_{j=1}^{H/10}(1 − hᵢⱼ)**. It combines 3, 6, or 9 hazards, respectively.

### 20. Why use Global, Segment-aware, and Personalized comparisons?

They provide saved reference approaches with different levels of customer-specific information. The comparison is limited to the models, cohort, and metrics present in the historical evaluation; it is not an exhaustive benchmark.

### 21. What does ROC-AUC measure?

ROC-AUC summarizes how well the model ranks positive cases above negative cases across thresholds. It does not by itself tell us whether predicted probabilities are calibrated or whether a business action will be profitable.

### 22. What does average precision measure?

Average precision summarizes the precision-recall relationship, emphasizing the positive class. Its baseline and interpretation depend on event prevalence, so horizon-specific values should not be treated as if they shared an identical target rate.

### 23. What is the Brier score?

It is the mean squared difference between predicted probability and binary outcome. Lower is better for the evaluated sample, but the score is affected by both discrimination and calibration and should be read with target prevalence and cohort context.

### 24. What is calibration?

Calibration asks whether events occur at about the predicted rate for groups of predictions. If customers assigned probabilities around 0.4 purchase roughly 40% of the time in the defined cohort and horizon, that is evidence of calibration for that group, not a guarantee for one person.

### 25. What does ECE measure?

Expected calibration error aggregates the gap between average predicted probability and observed event rate across defined bins. Its value depends on the binning procedure and sample size, so the saved definition and calibration plot matter.

### 26. Why not combine all metrics into one score?

ROC-AUC, average precision, Brier score, and calibration error answer different questions. Combining them into a single unqualified number would hide ranking, probability accuracy, and calibration differences.

### 27. How is expected revenue calculated?

The saved two-stage estimate multiplies the probability of at least one purchase in horizon H by expected spending conditional on a purchase in that horizon.

### 28. Why is expected revenue not actual revenue?

It is a probabilistic estimate, not a transaction that has already occurred. It can be wrong for an individual and may be biased in aggregate; the saved TEST diagnostics show horizon-specific error and underprediction.

### 29. What is the difference between MAE and RMSE?

MAE averages absolute errors and is easier to interpret in currency units. RMSE squares errors before averaging and is more sensitive to large errors. Neither alone describes calibration or causal business value.

### 30. What does negative mean forecast bias indicate?

Under the saved convention, negative mean forecast bias indicates average underprediction on the evaluated TEST cohort. It is a diagnostic; it does not justify multiplying each forecast by an aggregate correction factor.

## Behavior, reliability, and retention

### 31. Which behavior hypotheses were supported?

The unusual personal-gap hypothesis H1 and falling-revenue-rate hypothesis H3 were supported in multiple horizons. H2 and H4 were inconclusive; H5 was not evaluable.

### 32. Why was H5 not evaluable?

The required conditional comparison needs a saved Purchase Clock prediction vintage at the official TRAIN cutoffs. That chronologically eligible vintage was unavailable, so the project did not fit a new model to fill the gap.

### 33. Does a supported behavior indicator prove a cause of non-purchase?

No. The result is a historical association or predictive comparison under the saved protocol. It does not show that changing the indicator would cause a purchase.

### 34. What does model reliability mean here?

It refers to cohort-level diagnostics such as calibration, subgroup performance, and bootstrap uncertainty for aggregate metrics. It does not mean every individual prediction is reliable.

### 35. Are the feature explanations causal?

No. Notebook 09 input substitutions show how the frozen model output changes under controlled feature substitutions. They do not establish that a real-world change in that feature would cause a customer to purchase.

### 36. Why is reference-based revenue exposure not estimable?

The saved analysis does not contain a defensible, chronologically valid matched reference forecast for that quantity. The correct output is null with status `not_estimable`, not a manufactured loss estimate.

### 37. What is the nonreturn-weighted spending proxy?

It is one minus purchase probability multiplied by conditional expected spending. It is a screening proxy only; it is not a recoverable amount or revenue “at risk.”

### 38. Are the retention campaign scenarios causal estimates?

No. They use hypothetical response, uplift, budget, contact-cost, and optional margin assumptions. Without observed treatment assignment and a causal evaluation, the resulting values are illustrative calculations.

### 39. Why is churn risk different from treatment response?

A customer with high predicted non-purchase risk may not be persuadable, while a lower-risk customer could respond to a specific offer. Risk prediction estimates an outcome; treatment response estimates a difference between potential outcomes under interventions.

### 40. What did trajectory clustering add?

It provides a descriptive way to group eligible customers by observed trajectory shape. It did not establish that those clusters are risk categories or that trajectory features improve the saved Purchase Clock conditionally.

### 41. Why were some customers ineligible for trajectory analysis?

Trajectory methods require enough observed windows and active periods to construct a curve or summary. Sparse and short histories do not support that representation, so the analysis reports smaller method-specific cohorts.

### 42. What is functional PCA?

It represents variation among curves using a mean curve and a set of orthogonal component functions with customer-specific scores. Retaining fewer components compresses the curves but may discard detail.

### 43. What does the 98.82% explained variance mean?

It is the cumulative explained variance of the PCA fitted on TRAIN. It is not a TEST explained-variance result. Held-out TEST reconstruction error is reported separately as RMSE 0.006248.

### 44. Did trajectories improve prediction beyond the Purchase Clock?

The saved paired Brier interval on the same 1,306-customer summary-trajectory subset includes zero. The comparison is inconclusive and does not establish conditional incremental value or equivalence.

## Engineering and interpretation

### 45. How does the website connect to the notebooks?

The notebooks and saved outputs are offline research artifacts. FastAPI serves saved models and validated aggregate evidence; generated typed API clients connect the React pages to those routes.

### 46. Are notebooks executed when the site opens?

No. The application loads saved model files, metrics, and a versioned trajectory snapshot. Notebook execution is not part of the request path.

### 47. What happens when a research artifact is missing or stale?

The research endpoint validates its schema and source manifest and fails explicitly rather than silently returning an outdated summary.

### 48. What happens if a customer has too little history?

Method-specific support checks determine whether an output can be computed. The application and saved evaluations should preserve unsupported states rather than inventing values for missing history.

### 49. What are the major limitations?

The history is short and left-truncated; customer records can be sparse; evaluation is historical; method eligibility differs; no treatment-response data exists; and there was no production deployment, Firefox/WebKit, manual screen-reader, or application-login validation in the Phase 8 QA record.

### 50. What is the main scientific contribution?

The contribution is a reproducible, temporally bounded system that links descriptive features, saved forecasts, reliability diagnostics, and clearly labeled limitations. It does not claim a new universal algorithm or a causal retention effect.

### 51. How would you extend this work for a real business?

Collect longer prospective histories with reliable customer IDs, exposure and campaign assignment, response, margin, and cost data. Keep a randomized holdout where possible, validate across time and customer groups, and assess both forecast quality and incremental business outcomes.

### 52. Why did you not retrain models for the final report?

The task is to document and validate completed research. Several notebooks can overwrite saved artifacts. Re-running training could alter validated results and is not required to check the submission package.
