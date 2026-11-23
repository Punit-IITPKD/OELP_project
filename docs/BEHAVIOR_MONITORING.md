# Behavioral Change Monitoring

## Purpose and boundary

Notebook 08 evaluates customer-level behavior changes in the historical UK retail
dataset. The outcome is **no observed purchase in the next 30, 60, or 90 days**;
it is horizon-specific and does not mean permanent churn. The `/behavior` page
displays continuous historical indicators for the September 10, 2010 cutoff. It is
not a live monitor, intervention recommendation, or categorical alert system.

The reusable implementation is in `src/behavior_monitor.py`; validation-only
model-selection helpers and the study runner are in `src/behavior_evaluation.py`
and `src/behavior_research.py`. The executed notebook is
`notebooks/08_Behavioral_Change_Detection.ipynb`.

## Feature definitions

- **Personal gap deviation:** current elapsed gap minus the customer's median
  completed pre-cutoff gap, divided by a robust MAD scale. It is unavailable until
  the configured minimum number of completed gaps is observed.
- **Purchase-rate change:** recent `[t−30,t)` order rate compared with reference
  `[t−120,t−30)` rate. Rates use observed exposure, a documented rate prior, and
  non-overlapping windows. Exposure starts at the customer's first observed
  purchase when that occurs inside a window.
- **Revenue-rate change:** gross revenue per observed day over the same windows.
  There is no artificial revenue pseudocount; the ratio is unavailable if the
  reference rate is unsupported or zero.
- **EWMA gap trajectory:** recent and reference exponentially weighted means of
  completed purchase gaps. Gaps crossing the cutoff are excluded. λ is selected
  from `{0.2, 0.4, 0.6}` using validation only; the saved serving configuration
  uses λ = `0.6`.
- **History sufficiency:** explicit `sufficient`, `limited`, or `insufficient`
  support labels, with missing statistics left unavailable instead of imputed
  into the descriptive dashboard.

Feature and policy versions are recorded in
`models/behavior_monitor/metadata.json`. The saved policy version is
`behavior-continuous-v1`; no categorical threshold policy or fitted model artifact
is saved.

## Research design

The study reads the established matured temporal split metadata and feature
snapshots. It does not read TEST target columns during feature construction or
model selection. TRAIN and VAL targets are built with the existing temporal target
function; the TEST target is constructed only after selection is frozen, and the
full horizon must be observable by the dataset end.

Candidate E is an L2 logistic regression using behavior features only. λ is chosen
from the prespecified candidate set, and `C` from `{0.1, 1, 10}`. Validation
average precision is the selection objective, with Brier score as a tie-breaker.
The baselines are:

1. A: TRAIN-derived global inactivity indicator.
2. B: recency-only ranking.
3. C: the existing personalized delay ratio.
4. D: the saved Purchase Clock.
5. E: behavior-only model.
6. F: Purchase Clock plus behavior, only if its saved probability vintage is
   chronologically available at every official TRAIN cutoff.

Candidate F is **not fitted**. The validation Purchase Clock vintage was available
only from June 30, 2010, after every official TRAIN cutoff, so H5 cannot establish
independent incremental value. Candidate E is compared with D on the locked TEST
cohorts, but a two-model comparison is not a conditional-value test.

Metrics include ROC-AUC, average precision, precision and recall at a fixed top-10%
ranking budget, calibration metrics for probabilistic models, false-alert rate and
coverage, history-sufficiency and segment subgroups, and paired customer-level
bootstrap intervals. The executed run uses 500 paired customer bootstrap
resamples. The ranking budget and validation-frozen thresholds are research
evaluation references only; they do not enable product alerts.

## Locked TEST findings

The test cohort has 3,373 customers at each horizon. Candidate E's recorded average
precision is:

| Horizon | Behavior-only E | Purchase Clock D |
| --- | ---: | ---: |
| 30 days | 0.815 | 0.852 |
| 60 days | 0.666 | 0.712 |
| 90 days | 0.550 | 0.611 |

Candidate E did not outperform the saved Purchase Clock on these TEST cohorts.
The saved results report positive paired AP differences for the Purchase Clock
over behavior-only E at all three horizons. Feature-family ablations show
multiple-horizon evidence for personalized gap and spending changes; purchase-rate
and EWMA contributions remain inconclusive in this evaluation. These are
historical associations and ranking results, not causal evidence or current
customer recommendations.

The complete model metrics, subgroups, hypotheses, bootstrap intervals, and
limitations are in `data/metrics/behavior_monitor_evaluation.json`. Measured runtime
and throughput are in `data/metrics/behavior_monitor_profiling.json`.

## API and interface

- `GET /api/behavior/summary` — fixed cutoff, feature distributions, and support
  counts.
- `GET /api/behavior/customers` — filterable, sortable, paginated customer rows.
- `GET /api/behavior/evaluation` — saved validation/test metrics and study caveats.
- `GET /api/customers/{customer_id}/behavior` — one customer's indicators and
  explanations.
- `GET /api/customers/{customer_id}/behavior/trajectory` — compact pre-cutoff
  history in 30-day windows.

The React `/behavior` page provides customer filters, search, sorting, pagination,
CSV export of visible rows, indicator detail, trajectory history, and evaluation
results. The Customer Intelligence profile also shows a Behavior History section.
Both surfaces use the generated API client and show loading, error, and empty
states. They explicitly state that indicators are historical and no validated
alert policy exists.

Run the research again to regenerate the versioned metadata and metrics:

```bash
jupyter execute --inplace notebooks/08_Behavioral_Change_Detection.ipynb
```

After regenerating, restart the app so the process reloads the saved behavior
configuration and cached feature snapshot.

## Limitations

- The dataset is sparse and historical; findings may not generalize to current
  customers or other retail settings.
- “No observed purchase” is not proof of churn.
- Some customers lack enough history for gap or rate indicators, and zero or
  unsupported reference revenue makes the revenue ratio unavailable.
- The TEST cutoff contributes one row per customer, while customers repeat across
  historical TRAIN/VAL/TEST cutoffs. Bootstrap resampling is clustered by customer
  within each held-out cutoff.
- Candidate E is weaker than the saved Purchase Clock on the recorded TEST AP.
  Candidate F is unavailable due to model-vintage timing, leaving H5 unresolved.
- No causal intervention, real-time monitoring, or production alert policy has
  been evaluated.
