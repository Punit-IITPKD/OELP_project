# Research Notes: Academic foundations for customer retention analysis

**Status:** complete
**Depth:** Standard

## Plan

- **Question:** Which established academic methods inform customer segmentation, repeat-purchase prediction, reliability analysis, behavioural change, functional trajectories, and retention decisions?
- **Scope:** Foundational peer-reviewed methods and evidence relevant to the eleven-notebook historical retail study; exclude claims that would imply this project validated methods or business effects it did not test.
- **Audience:** Academic project evaluators and viva examiners.
- **Deliverable:** A cited literature review integrated into the final project report, with a source register and evidence trail.

## Focus Areas

| # | Area | Status | Sources |
|---|---|---|---|
| 1 | RFM and customer segmentation | collected | 5 sources |
| 2 | Purchase timing, interpurchase gaps, and hazard models | collected | 5 sources |
| 3 | Prediction metrics, calibration, reliability, and explanations | collected | 5 sources |
| 4 | Behavioural change detection and functional data analysis | collected | 5 sources |
| 5 | Customer lifetime value, retention decisions, and causal evaluation | collected | 5 sources |

## Coverage Checklist

- [x] Explain what RFM and K-means contribute, and what descriptive segments cannot establish.
- [x] Distinguish interpurchase-gap summaries and inactivity cutoffs from time-to-event purchase probabilities.
- [x] Explain ROC-AUC, average precision, Brier score, and calibration without collapsing them into one score.
- [x] Explain how behavioural-change and functional-trajectory methods work, including data-support requirements.
- [x] Separate expected revenue and screening rules from realized revenue, causal campaign uplift, and treatment response.
- [x] Connect each method to the project’s saved findings without claiming a literature result is a project result.

## Findings Log

_[@key] markers reference sources in research/sources.json; they become numbered citations in the final report._

### RFM and customer segmentation

- RFM is a transaction-summary representation; scoring and clustering are different methods, with outputs depending on feature representation and validation choices [@salminen-2023-segmentation-review] [@ernawati-2021-rfm-review] [@uk-retail-clustering-2023].
- Segmentation papers describe candidate approaches, not proof that cluster assignments improve retention or intervention outcomes [@salminen-2023-segmentation-review] [@sarvari-2016-rfm-comparison].

### Purchase timing and hazard models

- Repeated-event and customer-base models formalize purchase timing and future activity under differing observation assumptions; timing regularity is one studied extension [@bijwaard-franses-paap-repeated-events] [@platzer-reutterer-2016-timing] [@batislam-denizel-filiztekin-2007-validation].
- This literature does not establish a universally best hazard or purchase-timing model for the project's historical cohort [@bijwaard-franses-paap-repeated-events] [@platzer-reutterer-2016-timing] [@batislam-denizel-filiztekin-2007-validation].

### Prediction reliability and explanation

- Discrimination, probability accuracy, and calibration answer different evaluation questions; ROC/PR interpretation depends on target prevalence and use [@saito-rehmsmeier-2015-pr-roc] [@silva-filho-2023-calibration-survey] [@brier-1950-probability-score].
- Feature attribution describes a model output under a defined method and is not, by itself, a causal effect [@ma-tourani-2020-shapley] [@silva-filho-2023-calibration-survey].

### Behavioural change and functional data analysis

- Offline changepoint segmentation and sequential monitoring are distinct tasks; algorithm guarantees depend on the specified cost and assumptions [@aminikhanghahi-cook-2017-changepoints] [@killick-2012-pelt].
- Functional analysis represents repeated observations as curves, with smoothing, alignment, sparse support, and dimension reduction affecting interpretation [@gertheiss-et-al-2024-functional-data-review] [@fda-systematic-review-2013].

### Retention decisions and causal evaluation

- Customer lifetime value and retention are decision-support constructs whose estimates depend on the contractual setting, time horizon, and model assumptions [@casteran-meyer-waarden-reinartz-2021-clv-review] [@fader-hardie-2009-customer-base].
- Risk ranking is not treatment response; intervention effect requires causal evaluation, and randomized-study results are setting-specific [@ascarza-2018-retention-futility] [@godinho-matos-2018-randomized-retention] [@gordon-et-al-2019-ad-measurement].

## Conflicts & Open Questions

- RFM-use prevalence differs across reviews with different search scopes and denominators; no population-wide prevalence estimate is inferred [@salminen-2023-segmentation-review] [@ernawati-2021-rfm-review].
- ROC-AUC and precision-recall summaries are not interchangeable; metric choice depends on prevalence and the research question [@saito-rehmsmeier-2015-pr-roc] [@silva-filho-2023-calibration-survey].
- Some academic pages expose only abstracts or search snippets. Detailed claims will be limited to what the saved evidence supports.
- Literature findings provide methodological context; project claims must remain tied to saved evaluations and their own cohorts.

## Gaps

- No project-specific literature comparison or claim of methodological superiority is planned.
- Snippet-only references will support only bibliographic or narrowly stated contextual claims; they will not be used for detailed empirical findings.
- No cited source establishes causal effects for the project's hypothetical campaign scenarios.
- The final report numbers citations by first appearance and includes saved evidence paths in the bibliography and research evidence register.
