# Presentation Speaker Notes

The notes below are embedded in the editable PowerPoint as well as provided here for review. Student names, roll numbers, supervisor, institution, and programme remain placeholders until supplied. The submission date is 26 November 2026.

## Slide 01 — Project title

Introduce the project as a historical customer-analysis study using Year 1 of UCI Online Retail II. State that the presentation summarizes eleven completed notebooks and a React/FastAPI dashboard. Leave all academic identity fields as placeholders until names and programme details are supplied; use the actual submission date shown on the cover. Do not describe the system as a live retailer deployment.

## Slide 02 — Research motivation

Explain why repeat purchasing is difficult to interpret in a non-contractual setting: customers do not explicitly cancel, and a gap can have several meanings. Fixed thresholds and static groups can simplify the evidence too aggressively.

## Slide 03 — Problem statement

State the research question: how to turn historical transactions into reproducible segmentation, finite-horizon forecasts, reliability diagnostics, and bounded retention planning. Emphasize the difference between describing behavior, predicting a future event, and estimating intervention effects.

## Slide 04 — Dataset and historical cohort

State the Year 1 observation window, 19,213 valid invoice events, 4,312 descriptive RFM customers, 3,373 locked TEST customers per horizon, and the 10 September 2010 TEST cutoff. Explain that a customer's actual first purchase may precede the file and that forecast predictors use transactions strictly before each cutoff.

## Slide 05 — Research workflow

Use the pipeline diagram to show transactions moving through cleaning, features, temporal validation, saved model outputs, FastAPI, and React. Clarify that notebooks are offline workflows and are not executed by the website.

## Slide 06 — RFM segmentation

Define recency, frequency, and monetary value. Report two descriptive clusters for 4,312 customers and mean seed ARI 0.998, minimum 0.9935. Explain that stability does not prove future risk or intervention value.

## Slide 07 — Personalized Purchase Clock

Describe the saved logistic hazard at 10-day intervals: there are nine intervals through day 90. A 30-, 60-, or 90-day probability combines the first H/10 hazards—3, 6, or 9 intervals. Emphasize that “no purchase in 30 days” is not permanent churn. The model is saved and loaded for inference; the dashboard does not retrain it.

## Slide 08 — Purchase prediction results

Show ROC-AUC, average precision, and Brier score in separate panels. State that all rows use 3,373 TEST customers, but horizon target prevalence and outcome window differ. Avoid describing the metrics as a single score.

## Slide 09 — Expected spending and revenue

Explain that the two-stage forecast multiplies purchase probability by conditional expected spending. Report MAE and mean bias separately; the model has the lowest saved MAE at each horizon but remains negatively biased. Expected revenue is not a realized amount.

## Slide 10 — Behavior evidence

Report H1 and H3 as supported in multiple horizons, H2 and H4 as inconclusive, and H5 as not evaluable. Reliability and feature-sensitivity diagnostics are cohort-level and noncausal.

## Slide 11 — Trajectory clustering and functional PCA

Report three descriptive shape clusters, 1,100 eligible TEST customers, 659 functional curves, 98.82% TRAIN-fitted explained variance, and TEST reconstruction RMSE 0.006248. Explain why the support counts differ and why the PCA variance is not a TEST statistic.

## Slide 12 — Revenue planning and decision support

Separate expected revenue, forecast disagreement, the nonreturn-weighted proxy, and reference exposure. The reference exposure remains not estimable, and the predictive ranking hypothesis is not supported on locked TEST. Scenario inputs are hypothetical, not causal.

## Slide 13 — Dashboard demonstration

Show the Research Overview screenshot and point out that the application serves saved evidence. Briefly identify the Business Overview, Segments, Forecasting, Customer Intelligence, Behavior, Revenue & Retention, and Trajectory Explorer routes. Use customer 18102 without exposing a TEST outcome.

## Slide 14 — Validation and engineering

The Phase 8 baseline passed 195 Python, 32 React, and 28 Chromium tests, plus 37 GET smoke operations and the 67-file artifact check. The Phase 7 optimization reduced cold trajectory summary latency from 4,261.8 ms to 311.9 ms and the initial route gzip graph by 60.3%; process startup itself did not improve. Production deployment, Firefox/WebKit, and manual screen-reader checks were not covered.

## Slide 15 — Conclusions, limitations, and future work

Close with the strongest bounded findings: saved Personalized Purchase Clock comparisons are strongest among saved comparators; spending MAE is lowest but bias remains; behavior evidence is mixed; revenue exposure is not estimable; trajectory incremental value is inconclusive. Future work needs longer prospective data, campaign assignment/response, and a causal evaluation design.
