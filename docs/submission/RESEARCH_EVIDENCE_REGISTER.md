# Research Evidence Register

This register ties every quantitative research claim used in the submission to its saved source artifact and field. The academic literature bibliography provides methodological context; project measurements below come from the repository’s saved evaluation artifacts and notebook outputs.

## Project evidence

| ID | Claim used in report | Source file and field | Saved value / interpretation |
|---|---|---|---|
| ER-01 | Dataset, dates, historical cutoff, and core populations | `data/metrics/final_project_evaluation.json` → `research_scope`, `coverage_summary.trajectory` | UCI Online Retail II, Year 1; observed 2009-12-01 to 2010-12-09; 19,213 valid invoice events; TEST cutoff 2010-09-10; 3,373 TEST customers; 30/60/90-day horizons. |
| ER-02 | Chronological split and target-maturity dates | `data/metrics/final_project_evaluation.json` → `coverage_summary.temporal_splits.{30,60,90}.summary` | All three TEST cutoffs are 2010-09-10; TRAIN and VAL cutoffs and target end dates vary by horizon. |
| ER-03 | Gamma fit and empirical interpurchase P90 | `data/metrics/final_project_evaluation.json` → `notebook_registry[2].major_findings`; source notebook `notebooks/03_Interpurchase_Distribution_Analysis.ipynb` → distribution fit summary and empirical threshold output | Gamma has the lowest saved AIC, 123,760; empirical P90 is 101.9 days. Descriptive only; not a churn label. |
| ER-04 | Descriptive RFM K-means result and stability | `data/metrics/final_project_evaluation.json` → `notebook_registry[3].major_findings`, `evaluation_population_counts`; source notebook `notebooks/04_KMeans_Customer_Segmentation.ipynb` → `final_metrics`, `stability_check`, `cluster_sizes` | K=2, 4,312 customers; mean seed ARI 0.998, minimum 0.9935. Not a prospective churn score. |
| ER-05 | Personalized Purchase Clock metrics | `data/metrics/notebook_evaluation_summary.json` → `purchase_clock.test_metrics`; consolidated copy in `data/metrics/final_project_evaluation.json` → `purchase_clock_evaluation.test_metrics` | 3,373 customers at each horizon; ROC-AUC 0.720882/0.721767/0.719368; AP 0.537588/0.716292/0.784723; Brier 0.178534/0.214200/0.215308. |
| ER-06 | Saved spending forecast results | `data/metrics/notebook_evaluation_summary.json` → `spending_forecast.test_metrics`; consolidated copy in `data/metrics/final_project_evaluation.json` → `spending_forecast_evaluation.test_metrics` | Personalized two-stage MAE £243.18/£383.78/£547.38; RMSE £871.30/£1,466.12/£2,111.73; mean bias -£29.96/-£92.37/-£187.86; aggregate calibration ratio 0.864/0.801/0.746. |
| ER-07 | Notebook 08 hypothesis statuses and model vintage constraint | `data/metrics/behavior_monitor_evaluation.json` → `hypotheses`, `candidate_f_status`, `model_comparison`; consolidated copy in `final_project_evaluation.json` → `behavior_evaluation` | H1 and H3 supported in multiple horizons; H2 and H4 inconclusive; H5 not evaluable because no chronologically eligible saved Purchase Clock vintage exists. No operational alert policy supported. |
| ER-08 | Reliability and calibration | `data/metrics/prediction_reliability_evaluation.json` → `evaluation.purchase_calibration`, `evaluation.bootstrap_intervals`, `evaluation.subgroups` | Personalized Brier 0.178534/0.214200/0.215308; fixed-bin ECE 0.060562/0.062264/0.068906 for 30/60/90 days. Group-level historical diagnostics, not individual guarantees. |
| ER-09 | Revenue screening and hypothesis status | `data/metrics/revenue_exposure_evaluation.json` → `financial_definitions`, `hypotheses.H6_predictive_ranking`, `ranking_selection_and_test_evaluation`, `metadata.reference_exposure`; consolidated copy in `final_project_evaluation.json` → `revenue_exposure_evaluation` | Reference exposure status `not_estimable`, total `null`; H6 not supported on locked TEST; 90-day policy selection exploratory; campaign assumptions hypothetical. |
| ER-10 | Trajectory support, FPCA, and incremental comparison | `data/metrics/trajectory_analysis_evaluation.json` → `data_scope`, `cluster_selection`, `functional_analysis.test_evaluation`, `predictive_evaluation.paired_brier_differences`; consolidated copy in `final_project_evaluation.json` → `trajectory_evaluation` | Three descriptive shape clusters; 1,100 TEST cluster-eligible customers; 1,306 summary-trajectory customers; 659 functional curves; 98.82% TRAIN-fitted explained variance; TEST reconstruction RMSE 0.006248; same-cohort paired Brier interval includes zero. |
| ER-11 | Regression, browser, API, artifact-integrity, and deployment limitations | `docs/qa/FINAL_REPORT.md`, `docs/qa/MODEL_VALIDATION.md`, `docs/qa/KNOWN_LIMITATIONS.md`, `docs/qa/FRONTEND_E2E.md` | Phase 8 baseline: 195 Python, 32 React, 28 Chromium E2E tests; 37 GET smoke operations; 67 protected files match; typecheck/build passed. No production deployment validation, Firefox/WebKit, manual screen-reader testing, or application login. |
| ER-12 | Cold trajectory API and route-split performance | `docs/FINAL_ENGINEERING_VALIDATION.md` → “Backend performance” and “Frontend bundle and visual verification”; `docs/qa/PERFORMANCE_RELIABILITY.md` → “API latency” and “Frontend bundles” | Cold trajectory summary 4,261.8 → 311.9 ms (92.7% lower); customer 18102 4,292.6 → 349.8 ms (91.9% lower). Initial JS graph 889,810 → 306,125 bytes raw and 240,940 → 95,685 bytes gzip (65.6% / 60.3% lower). Process start-to-health was 3,747 → 3,907 ms, not an improvement. Phase 8 measured 265.9/270.2 ms cold endpoint medians and a 307,062-byte initial route graph. |

### Temporal split detail

| Horizon | TRAIN cutoff → outcome end | VAL cutoff → outcome end | Locked TEST cutoff → outcome end | TEST n |
|---:|---|---|---|---:|
| 30 days | 2010-06-01 → 2010-07-01 | 2010-08-01 → 2010-08-31 | 2010-09-10 → 2010-10-10 | 3,373 |
| 60 days | 2010-05-01 → 2010-06-30 | 2010-07-01 → 2010-08-30 | 2010-09-10 → 2010-11-09 | 3,373 |
| 90 days | 2010-03-01 → 2010-05-30 | 2010-06-01 → 2010-08-30 | 2010-09-10 → 2010-12-09 | 3,373 |

## Literature sources and saved evidence

The source registry in `research/sources.json` contains the citation key, URL, publication date, credibility tier, and saved evidence path. Snippet-only items are labeled and are used only for the bibliographic or narrow contextual facts visible in the saved snippet.

| Key | Source | Publication | Evidence path |
|---|---|---:|---|
| `chen-uci-online-retail-ii` | UCI Machine Learning Repository, *Online Retail II* | Dataset created 2012; donated 2019 | `research/sources/uci-online-retail-ii.md` |
| `salminen-2023-segmentation-review` | *How can algorithms help in segmenting users and customers?* | 2023 | `research/sources/rfm-03-systematic-review-algorithms.md` |
| `ernawati-2021-rfm-review` | *A review of data mining methods in RFM-based customer segmentation* | 2021 | `research/sources/rfm-04-rfm-method-review.md` |
| `uk-retail-clustering-2023` | John, Shobayo, and Ogunleye, *An Exploration of Clustering Algorithms for Customer Segmentation in the UK Retail Market* | 2023 | `research/sources/rfm-05-uk-retail-clustering.md` |
| `sarvari-2016-rfm-comparison` | Sarvari, Ustundag, and Takci, *Performance evaluation of different customer segmentation approaches based on RFM and demographics analysis* | 2016 | `research/sources/rfm-snippets.md` (bibliographic snippet only) |
| `bijwaard-franses-paap-repeated-events` | Bijwaard, Franses, and Paap, *Modeling Purchases as Repeated Events* | 2006 | `research/sources/timing-04-repeated-events-journal-version.md`; 2003 working paper also saved |
| `platzer-reutterer-2016-timing` | Platzer and Reutterer, *Ticking Away the Moments* | 2016 | `research/sources/timing-02-ticking-away-the-moments.md` |
| `batislam-denizel-filiztekin-2007-validation` | Batislam, Denizel, and Filiztekin, *Empirical validation and comparison of models for customer base analysis* | 2007 | `research/sources/timing-03-empirical-validation-customer-base-analysis.md` |
| `fader-hardie-2009-customer-base` | Fader and Hardie, *Probability Models for Customer-Base Analysis* | 2009 | `research/sources/retention-snippets.md` |
| `saito-rehmsmeier-2015-pr-roc` | Saito and Rehmsmeier, *The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets* | 2015 | `research/sources/reliability-01-pr-roc-imbalance.md` |
| `silva-filho-2023-calibration-survey` | Silva Filho et al., *Classifier calibration: a survey on how to assess and improve predicted class probabilities* | 2023 | `research/sources/reliability-02-classifier-calibration-survey.md` |
| `brier-1950-probability-score` | Brier, *Verification of forecasts expressed in terms of probability* | 1950 | `research/sources/reliability-snippets.md` |
| `ma-tourani-2020-shapley` | Ma and Tourani, *Predictive and Causal Implications of using Shapley Value for Model Interpretation* | 2020 | `research/sources/reliability-03-shap-predictive-causal.md` |
| `aminikhanghahi-cook-2017-changepoints` | Aminikhanghahi and Cook, *A Survey of Methods for Time Series Change Point Detection* | 2017 | `research/sources/behavior-fda-05-change-point-survey-full.md` |
| `killick-2012-pelt` | Killick, Fearnhead, and Eckley, *Optimal detection of changepoints with a linear computational cost* | 2012 | `research/sources/behavior-fda-04-pelt-primary-arxiv.md` |
| `gertheiss-et-al-2024-functional-data-review` | Gertheiss et al., *Functional Data Analysis: An Introduction and Recent Developments* | 2024 journal article; 2023 preprint | `research/sources/behavior-fda-03-fda-intro-review.md` |
| `fda-systematic-review-2013` | Ullah and Finch, *Applications of functional data analysis: A systematic review* | 2013 | `research/sources/behavior-fda-snippets.md` |
| `casteran-meyer-waarden-reinartz-2021-clv-review` | Castéran, Meyer-Waarden, and Reinartz, *Modeling Customer Lifetime Value, Retention, and Churn* | 2021 | `research/sources/retention-01-clv-retention-churn.md` |
| `ascarza-2018-retention-futility` | Ascarza, *Retention Futility: Targeting High-Risk Customers Might be Ineffective* | 2018 | `research/sources/retention-02-retention-futility.md` |
| `godinho-matos-2018-randomized-retention` | Godinho de Matos, Ferreira, and Belo, *Target the Ego or Target the Group* | 2018 | `research/sources/retention-03-randomized-churn-experiment.md` |
| `gordon-et-al-2019-ad-measurement` | Gordon et al., *A Comparison of Approaches to Advertising Measurement* | 2019 | `research/sources/retention-snippets.md` |

## Citation and interpretation rules

- Use the saved evaluation JSON fields for all project metrics, not estimates reconstructed from prose.
- Keep TRAIN explained variance and TEST reconstruction error distinct.
- Do not report a hypothetical scenario as an observed outcome or causal effect.
- Do not interpret a descriptive cluster as a risk rank or a treatment-response segment.
- Do not treat snippets as full-text evidence; their limitations remain visible in the registry.
