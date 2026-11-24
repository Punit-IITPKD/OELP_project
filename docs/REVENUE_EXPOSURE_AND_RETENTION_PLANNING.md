# Revenue Exposure and Retention Planning

Notebook 10 and the React / FastAPI planner present saved historical forecasts,
model disagreements, evidence limits, customer-screening rankings, and
analyst-defined outreach scenarios. They do not train or change the saved
Purchase Clock or spending models.

## Financial definitions

| Quantity | Definition | Interpretation |
| --- | --- | --- |
| Personalized expected revenue | Saved horizon purchase probability × saved conditional expected spending | Current saved-model forecast for the recorded historical cutoff. |
| Historical-rate and segment-aware forecasts | Alternative saved forecast methods | Model comparisons only; neither is a business counterfactual. |
| Revenue exposure | `max(0, matched reference expected revenue − personalized expected revenue)` for the same customer, cutoff, and horizon | Requires a documented, valid reference definition and method. No such matched reference exists in the saved project, so exposure is `null` / `not_estimable`, never silently changed to zero. |
| Nonreturn-spending proxy | `(1 − purchase probability) × conditional expected spending` | A prioritization screen for hypothetical nonpurchase. It is not observed loss, preventable revenue, or recovered revenue. |
| Scenario incremental probability | `min(1 − p, assumed response probability × assumed purchase uplift if responded)` | A scenario assumption, not a fitted treatment effect. |
| Scenario incremental revenue | Scenario incremental probability × saved conditional expected spending | Hypothetical gross revenue only. Contribution is `null` unless an analyst supplies a gross-margin assumption. |
| Historical nonpurchase | Observed `Purchased` outcome in an offline validation or TEST split | A predictive ranking target only. It does not reveal whether outreach would have changed the outcome. |

No randomized campaign treatment, response, or control outcomes are present.
Therefore no route or notebook estimates causal uplift, avoided churn, or
campaign ROI.

When a gross margin is supplied, the API also solves the algebraic minimum
response probability and conditional purchase-uplift assumptions that would
cover selected contacts' costs, and reports when break-even is infeasible under
the supplied assumptions. Without margin, break-even contribution is explicitly
not estimable. Neither threshold is an observed or recommended campaign rate.

## Temporal design and leakage controls

- The inference cohort is the saved 3,373-customer cohort at the September 10,
  2010 cutoff.
- Validation selects ranking policy only for the two forecast vintages available
  prospectively: 30 days at August 1, 2010 and 60 days at July 1, 2010. The saved
  purchase model was available by June 30 for both.
- The policy comparison is restricted to customers at or above the
  horizon-specific TRAIN 75th percentile of historical gross spending. This
  threshold is computed from TRAIN only.
- The ranking module rejects future outcome columns. Forecast features and rank
  orders are prepared independently; `Purchased` and `FutureRevenue` are joined
  only for offline evaluation after ranks are fixed.
- The validation-selected 30- and 60-day policies are reported on the locked
  September 10 TEST cohort. TEST outcomes do not select the policy.
- No prospective 90-day validation vintage is eligible. Its ranking comparison
  is retrospective and exploratory; no 90-day winner is declared.
- Notebook 08 behavior indicators can filter candidates when explicitly
  requested. They are not converted to invented reliability weights.
- Notebook 09 reliability and revenue metrics remain historical group-level
  evidence, not an individual confidence guarantee.

## Recorded findings

All monetary amounts are GBP. Totals reproduce the saved model outputs on the
historical TEST forecast cohort.

| Horizon | Personalized expected revenue | Historical-rate forecast | Segment-aware forecast | Reference exposure | Nonreturn proxy |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 30 days | £639,659.40 | £858,475.87 | £752,723.56 | Not estimable | £904,417.94 |
| 60 days | £1,257,116.38 | £1,763,483.07 | £1,458,412.19 | Not estimable | £780,672.95 |
| 90 days | £1,861,869.51 | £2,942,543.56 | £2,823,576.74 | Not estimable | £598,292.99 |

The top 10% of customers by historical gross spending account for 59.62% of
historical gross spending. The top 10% by personalized expected revenue account
for 45.18%, 47.02%, and 52.67% of forecast revenue at 30, 60, and 90 days,
respectively. This is concentration of the named measures; it is not exposure
or a causal loss estimate.

The personalized model's average customer-level forecast bias on the historical
TEST was −£29.96 at 30 days, −£92.37 at 60 days, and −£187.86 at 90 days. The
corresponding portfolio-level differences between forecast and actual future
revenue were −£101,062.20, −£311,562.13, and −£633,656.69. These retrospective
metrics do not correct the saved forecasts or establish a reference exposure.
Historical-rate forecasts overpredicted the same portfolio; this disagreement
is not an eligible counterfactual.

### Frozen ranking results

Policy selection used future nonpurchase rate among the top 10% of the
TRAIN-defined high-spending validation cohort. On the locked TEST, that frozen
selection did not outperform all matched top-10% ranking baselines:

| Horizon | Selected on validation | Selected method's TEST nonpurchase rate | Stronger matched TEST baseline |
| ---: | --- | ---: | --- |
| 30 days | Nonreturn probability | 68.87% | Recency-only: 81.13% |
| 60 days | Nonreturn-spending proxy | 59.29% | Recency-only: 63.72% |
| 90 days | None; no prospective selection | Exploratory only | Nonreturn-spending proxy: 53.79% (not a validated winner) |

Customer-level bootstrap 95% intervals for the fixed selected TEST groups are
59.88%–77.36% (30 days, 106 customers) and 50.44%–68.14% (60 days, 113
customers). These intervals describe the selected groups' observed
nonpurchase rates; they do not account for model-selection uncertainty and do
not estimate intervention response.

The required top-budget comparisons retain the high-spending group definition
and report observed future nonpurchase among the frozen selection and two
simple baselines:

| Horizon | Top share | Validation-selected method | Selected rate | Recency-only rate | Nonreturn-spending proxy rate |
| ---: | ---: | --- | ---: | ---: | ---: |
| 30d | 1% | Nonreturn probability | 54.5% | 81.8% | 90.9% |
| 30d | 5% | Nonreturn probability | 71.7% | 90.6% | 81.1% |
| 30d | 10% | Nonreturn probability | 68.9% | 81.1% | 76.4% |
| 30d | 20% | Nonreturn probability | 69.3% | 67.0% | 72.6% |
| 60d | 1% | Nonreturn-spending proxy | 83.3% | 66.7% | 83.3% |
| 60d | 5% | Nonreturn-spending proxy | 68.4% | 70.2% | 68.4% |
| 60d | 10% | Nonreturn-spending proxy | 59.3% | 63.7% | 59.3% |
| 60d | 20% | Nonreturn-spending proxy | 55.8% | 49.1% | 55.8% |
| 90d* | 1% | Exploratory only | — | 50.0% | 78.6% |
| 90d* | 5% | Exploratory only | — | 54.5% | 57.6% |
| 90d* | 10% | Exploratory only | — | 51.5% | 53.8% |
| 90d* | 20% | Exploratory only | — | 40.5% | 42.8% |

*No 90-day policy was selected because a prospective validation vintage was
unavailable. Higher nonpurchase rates indicate identification of observed
historical nonpurchase only; they do not demonstrate persuasive effect or
recoverable revenue.

At a fixed 30-day budget of £500 and £3 contact cost, the nonreturn-proxy
illustration selects 166 contacts for each response/uplift combination. Its
scenario-grid gross-revenue range is £189.40–£3,788.05 as assumptions vary from
5% response × 2% uplift to 20% response × 10% uplift. The selected count stays
fixed because budget and contact cost are fixed; the revenue values are
hypothetical by construction.

| Hypothesis | Recorded result |
| --- | --- |
| H1 — Financial concentration | Supported descriptively at the prespecified threshold: top 10% historical spenders hold more than 50% of historical gross spend. |
| H2 — Risk/value interaction | Ranking strategies produce distinct selections; distinctness is not evidence of better outcomes. |
| H3 — Forecast reliability sensitivity | TEST diagnostics show horizon- and group-dependent spending bias. Production forecasts are not corrected from TEST. |
| H4 — Budget sensitivity | Contact count changes across the explicit budget/cost grid. |
| H5 — Scenario robustness | Screening order is intentionally independent of response/uplift assumptions. This design invariance does not establish campaign efficacy. |
| H6 — Predictive ranking | Not supported on the locked TEST: the validation-selected 30- and 60-day rules did not beat every matched high-spend baseline. |

The complete numerical results, subgroup metrics, comparison overlaps, bootstrap
intervals, and scenario grid are in:

- `data/metrics/revenue_exposure_evaluation.json`
- `data/metrics/retention_scenario_sensitivity.json`
- `data/metrics/revenue_exposure_profiling.json`
- `models/revenue_exposure/metadata.json`

## API and app behavior

The API reads the existing cached saved-model cohort. It does not refit models,
read future TEST outcomes for inference, or save campaign/contact actions.

| Endpoint | Purpose |
| --- | --- |
| `GET /api/revenue-exposure/summary` | Saved horizon forecasts, disagreements, nullable exposure, and evidence coverage |
| `GET /api/revenue-exposure/customers` | Deterministic screening ranks, pagination, numeric-ID search, sorting, history and behavior filters |
| `GET /api/revenue-exposure/scatter` | Filtered risk/value points for the historical cohort |
| `GET /api/revenue-exposure/concentration` | Top-customer concentration for historical and forecast measures |
| `GET /api/revenue-exposure/evaluation` | Aggregate Notebook 10 research evidence |
| `GET /api/customers/{customer_id}/revenue-exposure` | Customer forecast, proxy, behavior, reliability context, and limitations |
| `POST /api/retention/scenarios` | One hypothetical contact-budget allocation |
| `POST /api/retention/compare-strategies` | Compare selected screening strategies under shared assumptions |

The customer ranking UI exports its visible page as CSV. Its scatter uses
nonreturn probability on X and conditional expected spending on Y, colored by
historical segment; segment and history-sufficiency filters are shared with the
table. Tooltips expose customer ID, purchase probability, conditional spending,
expected revenue, history group, and group reliability.

The `/revenue-exposure` page supports 30/60/90-day horizons, all six ranking
methods, customer detail, evidence filters, and analyst-supplied budget,
contact-cost, response, uplift, and optional margin assumptions. It displays
the saved scenario sensitivity chart, break-even conditions, and selected
contacts. The existing Customer Intelligence profile has a **Revenue Exposure
& Strategy** section using the same customer and cutoff, with a link into the
planner carrying that customer ID and horizon. Scenario outputs are labeled
hypothetical and noncausal. The UI does not claim that a selected customer will
respond or that model proxy amounts can be recovered.

## Runtime and reproducibility

The React app's `scripts/run-oelp-web.sh` launcher pins its API process to Python
3.11 and the hash-locked `requirements-ci.txt` set used for tests and notebook
execution. Notebook 10 was reproduced with Python 3.11.17, NumPy 2.4.6,
pandas 3.1.1, and scikit-learn 1.9.1; the profiling artifact records these
versions. The existing workspace Run/Preview settings were not replaced.

Warm API measurements use FastAPI's in-process TestClient after one warm-up
request, with five repetitions; timings are in
`data/metrics/revenue_exposure_profiling.json`. They are local measurements, not
production latency guarantees.

Rebuild and execute with:

```bash
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  python scripts/build_notebook10.py
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  --with jupyter --with ipykernel python -m jupyter execute --inplace \
  notebooks/10_Revenue_at_Risk_and_Retention_Planning.ipynb
```
