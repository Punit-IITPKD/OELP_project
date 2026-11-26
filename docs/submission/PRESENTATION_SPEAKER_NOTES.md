# Presentation Speaker Notes

The notes below are embedded in the editable PowerPoint as well as provided here for review. Student, faculty, and institutional names remain placeholders.

## Slide 01 — Project title

Introduce the project as a historical customer-analysis study using Year 1 of UCI Online Retail II. State that the presentation summarizes eleven completed notebooks and a React/FastAPI dashboard. Do not describe the system as a live retailer deployment.

## Slide 02 — Research motivation

Explain why repeat purchasing is difficult to interpret in a non-contractual setting: customers do not explicitly cancel, and a gap can have several meanings. Fixed thresholds and static groups can simplify the evidence too aggressively.

## Slide 03 — Problem statement

State the research question: how to turn historical transactions into reproducible segmentation, finite-horizon forecasts, reliability diagnostics, and bounded retention planning. Emphasize the difference between describing behavior, predicting a future event, and estimating intervention effects.

## Slide 04 — Objectives

Walk through the pipeline objectives: audit transaction quality, construct customer features, preserve temporal validation, evaluate saved forecasts, examine reliability and trajectories, and serve the evidence through the dashboard. Mention that no new model is trained for this final submission.

## Slide 05 — Dataset and preprocessing

Identify the Year 1 date range and official 10 September 2010 TEST cutoff. Explain missing customer IDs, cancellation/return records, invoice aggregation, and the distinction between the 4,312-customer descriptive segmentation and the 3,373-customer TEST cohort.

## Slide 06 — Research workflow

Use the pipeline diagram to show how transactions move through cleaning, features, temporal validation, saved model outputs, FastAPI, and React. Clarify that notebooks are offline research workflows and are not executed by the website.

## Slide 07 — RFM segmentation

Define recency, frequency, and monetary value. Report two descriptive clusters for 4,312 customers and mean seed ARI 0.998, minimum 0.9935. Explain that stability does not prove future risk or intervention value.

## Slide 08 — Personalized Purchase Clock

Describe the discrete-time hazard and finite-horizon conversion. Emphasize that “no purchase in 30 days” is not permanent churn. The model is saved and is loaded for inference; it is not retrained by the dashboard.

## Slide 09 — Purchase prediction results

Show the three saved metrics in separate panels: ROC-AUC, average precision, and Brier score. State that all rows use 3,373 TEST customers, but horizon target prevalence and outcome window differ. Avoid describing the metrics as a single score.

## Slide 10 — Expected spending and revenue

Explain that the two-stage forecast multiplies purchase probability by conditional expected spending. Report MAE and mean bias separately; the model has lowest saved MAE at each horizon but is negatively biased. Expected revenue is not a realized amount.

## Slide 11 — Behavior and reliability

Report H1 and H3 as supported in multiple horizons, H2 and H4 as inconclusive, and H5 as not evaluable. Point out that reliability and feature-sensitivity diagnostics are cohort-level and noncausal.

## Slide 12 — Trajectory clustering and functional PCA

Report three descriptive shape clusters, 1,100 eligible TEST customers, 659 functional curves, 98.82% TRAIN-fitted explained variance, and TEST reconstruction RMSE 0.006248. Explain why the support counts differ and why the PCA variance is not a TEST statistic.

## Slide 13 — Revenue planning and decision support

Separate expected revenue, forecast disagreement, the nonreturn-weighted proxy, and reference exposure. The reference exposure remains not estimable and the predictive ranking hypothesis is not supported on locked TEST. Scenario inputs are hypothetical, not causal.

## Slide 14 — Website demonstration and QA

Show Business Overview, Segments, Forecasting, Customer Intelligence, Behavior, Revenue & Retention, Trajectory Explorer, and Research Overview. Describe the saved-customer workflow using 18102 without exposing a TEST outcome. The Phase 8 baseline passed 195 Python, 32 React, and 28 Chromium tests, plus 37 GET smoke operations and the 67-file artifact check. The Phase 7 optimization reduced cold trajectory summary latency from 4,261.8 ms to 311.9 ms and the initial route gzip graph by 60.3%; process startup itself did not improve.

## Slide 15 — Conclusions, limitations, and future work

Close with the strongest bounded findings: saved Personalized Purchase Clock comparisons are strongest among saved comparators; spending MAE is lowest but bias remains; behavior evidence is mixed; revenue exposure is not estimable; trajectory incremental value is inconclusive. Future work needs longer prospective data, campaign assignment/response, and a causal evaluation design.
