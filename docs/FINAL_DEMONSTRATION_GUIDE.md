# Demonstration guide

This flow is designed for a professor or project evaluator. It presents saved
historical evidence and keeps retrospective records, model outputs, TEST
diagnostics, and hypothetical scenarios distinct.

## 1. Frame the problem and the data

Explain that the project studies repeat purchasing in the Year 1 UCI Online
Retail II data, spanning December 2009 through December 2010. The analysis uses
a historical September 10, 2010 cutoff with 30-, 60-, and 90-day targets. It
does not represent a live retailer or a current customer population.

## 2. Open Business Overview

Show observed customer count, orders, revenue, monthly history, and descriptive
RFM composition. Point out that the displayed forecast totals are saved-model
estimates for the historical cutoff, not realized future revenue.

## 3. Show static customer segmentation

Open **Segments** and compare the full-period descriptive RFM groupings with
the separate historical forecast cohorts. Use the customer table filters to
illustrate how those labels differ. Mention that the RFM segments are
descriptive and are not prospective churn scores.

## 4. Explain the Personalized Purchase Clock

Open **Forecasting** and compare Global, Segment-aware, and Personalized
outputs at the validated horizons. Explain that the purchase model estimates a
finite-horizon probability. “No purchase” within a horizon is not proof of
permanent churn.

## 5. Show expected spending

Open **Model Performance** and compare saved expected-revenue diagnostics. Keep
MAE, RMSE, mean bias, and calibration separate. Explain that the two-stage
quantity is purchase probability multiplied by conditional expected spending;
it is not a realized amount or an estimate of recoverable loss.

## 6. Demonstrate an actual saved customer record

Open **Customer Intelligence** and search for **18102**, an ID present in the
saved historical customer data. The profile endpoint, behavior endpoint,
behavior trajectory, trajectory detail, trajectory explanation, and group
reliability endpoint returned successfully for this record during validation.

Use the cutoff date shown in the profile as the boundary for model inputs.
When the full-period retrospective panel appears, state that its RFM and net
spend can include transactions after the forecast cutoff and are not model
inputs. On-demand feature substitutions describe model sensitivity; they do
not explain customer intent or causal effects.

## 7. Show behavior indicators

Open **Behavior Indicators** and use the history-group or indicator filters.
Explain that the page reports continuous historical indicators and a saved
evaluation, not enabled alerts or customer churn labels. The conditional
Purchase Clock-plus-behavior comparison remains unresolved because the required
earlier saved model vintage was unavailable.

## 8. Explain reliability

Open **Model Performance → Calibration & reliability** and then inspect
customer group context from the profile. Emphasize that calibration bins,
subgroup counts, and bootstrap intervals summarize the historical cohort. They
do not provide a personal accuracy guarantee.

## 9. Explain revenue screening and scenarios

Open **Revenue & Retention**. Distinguish expected revenue, forecast
disagreement, the nonreturn-weighted spending proxy, and reference-based
exposure. The saved exposure total is not estimable and remains null.

If entering a scenario, use clearly hypothetical response, uplift, budget, and
contact-cost assumptions. Do not present the output as a predicted intervention
effect, recovered revenue, or causal campaign benefit.

## 10. Explore trajectories and functional analysis

Open **Trajectory Explorer** and review history support, shape-cluster
eligibility, cluster assignments, and the functional-analysis evaluation.
Explain that the three shape groups are descriptive, only 1,100 TEST customers
meet the shape support rule, and the functional representation evaluates a
separate 659-customer subset. TRAIN explained variance and TEST reconstruction
error have different roles. Do not describe cluster labels as risk ranks.

## 11. Open Research Overview

Use the hypothesis-status filter and notebook search to navigate the
consolidated findings. Open the linked methods or notebook source, then show
the evidence provenance table. The final summary is generated from saved
artifacts and source hashes; it does not train an additional model.

## 12. Close with the limits

Summarize the main supported evidence and the unresolved findings:

- The Personalized Purchase Clock is the strongest saved probability
  comparator in this historical TEST evaluation.
- The behavior-only candidate did not outperform the saved Purchase Clock on
  the recorded TEST average-precision comparisons.
- Reference-based revenue exposure is not estimable; campaign effects are not
  identified.
- Trajectory structure is descriptive, and incremental prediction beyond the
  Purchase Clock remains inconclusive.
- The data are short and left-truncated, and no randomized treatment outcomes
  are available.

Do not reveal or infer customer-level TEST outcomes during the demonstration.
