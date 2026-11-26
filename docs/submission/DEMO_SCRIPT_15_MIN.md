# Professor Demonstration Script — 15 Minutes

**Environment:** Replit development preview; no public deployment is claimed.  
**Forecast cutoff:** 10 September 2010.  
**Example customer:** `18102`.  
**Safety note:** Do not reveal an individual TEST outcome. If a panel is explicitly retrospective and includes post-cutoff data, state that it is not a forecast input.

## Step 1 — Frame the question (0:00–0:50)

- **Page URL:** `/`
- **Action:** Introduce the project and the UCI Online Retail II Year 1 scope.
- **Expected visible result:** Business Overview with historical customer and transaction summaries.
- **Say:** “We study historical repeat purchasing, not live churn. The saved forecast cutoff is 10 September 2010, with 30-, 60-, and 90-day targets.”
- **Scientific interpretation:** Every prediction is tied to a cutoff and a finite outcome window.
- **Limitation:** One historical retail dataset is not representative of a current retailer by default.
- **Backup:** Use the abstract and scope row in `RESEARCH_EVIDENCE_REGISTER.md`.

## Step 2 — Business Overview (0:50–1:50)

- **Page URL:** `/`
- **Action:** Point to customer, order, revenue, and historical trend cards.
- **Expected visible result:** Saved historical totals and overview plots.
- **Say:** “These are observed historical summaries. Forecast totals elsewhere are saved-model estimates, not realized future sales.”
- **Scientific interpretation:** Descriptive history and forecast values are different quantities.
- **Limitation:** Do not call the overview a live production dashboard.
- **Backup:** Open the captured `assets/screenshots/business-overview.png`.

## Step 3 — Customer segmentation (1:50–2:50)

- **Page URL:** `/segments`
- **Action:** Show the descriptive RFM segment comparison and customer table.
- **Expected visible result:** Two saved RFM groups and filters for the customer table.
- **Say:** “The full-period K-means solution has two groups for 4,312 customers, with high seed stability. These are descriptive labels, not churn scores.”
- **Scientific interpretation:** Cluster stability addresses repeatability of assignments under initialization, not business usefulness.
- **Limitation:** The full-period groups are not prospective TEST-time forecasts.
- **Backup:** Use ER-04 in the evidence register and the Notebook 04 output.

## Step 4 — Purchase Clock (2:50–4:00)

- **Page URL:** `/forecasting`
- **Action:** Compare Global, Segment-aware, and Personalized probability outputs; switch among 30/60/90 days.
- **Expected visible result:** Horizon-specific purchase probabilities and saved model comparisons.
- **Say:** “The model estimates a finite-horizon purchase probability. No purchase in 30 days is not proof of permanent churn.”
- **Scientific interpretation:** A discrete-time hazard is conditional on remaining event-free up to each interval.
- **Limitation:** Results are retrospective and tied to historical cohort prevalence.
- **Backup:** Show Figure 6 and ER-05 in the report.

## Step 5 — Model performance and spending (4:00–5:10)

- **Page URL:** `/model-performance`
- **Action:** Open the saved TEST comparison and point to MAE, RMSE, bias, and calibration separately.
- **Expected visible result:** Horizon-specific model metrics and reliability/calibration panels.
- **Say:** “The Personalized two-stage estimate has the lowest saved MAE at all three horizons, but it still underpredicts in aggregate. MAE, RMSE, and bias answer different questions.”
- **Scientific interpretation:** Good average ranking or error does not eliminate calibration and subgroup concerns.
- **Limitation:** Cohort-average metrics are not an individual guarantee.
- **Backup:** Use the tables and Figure 7 in Chapter 7.

## Step 6 — Customer 18102 (5:10–6:50)

- **Page URL:** `/intelligence`
- **Action:** Use the page search to enter `18102`; inspect the saved history and forecast summary.
- **Expected visible result:** Customer profile, cutoff-safe history, 30/60/90-day forecasts, and available diagnostics.
- **Say:** “The inputs for forecast interpretation are bounded by the saved cutoff. A retrospective profile may include later transactions, which are descriptive and not model inputs.”
- **Scientific interpretation:** Customer-level output is a conditional model estimate, not a promise.
- **Limitation:** Do not reveal or infer this customer’s TEST label or outcome.
- **Backup:** Reopen `/intelligence` and search again; if the API is unavailable, show the verified layout screenshot or report workflow and explain the saved API checks.

## Step 7 — Forecast explanation (6:50–7:50)

- **Page URL:** `/intelligence`
- **Action:** Open the explanation or sensitivity panel for customer 18102.
- **Expected visible result:** Feature-level model sensitivities or hazard/spending decomposition.
- **Say:** “These substitutions show how this frozen model output changes under selected input changes. They do not explain intent or a causal effect.”
- **Scientific interpretation:** A model explanation is conditional on the fitted model and explanation procedure.
- **Limitation:** Sensitivity is not a treatment recommendation.
- **Backup:** Use Notebook 09 methodology and its evidence register entry ER-08.

## Step 8 — Reliability and behavior (7:50–8:50)

- **Page URL:** `/behavior` and `/model-performance`
- **Action:** Show behavior hypothesis status, then show calibration or subgroup context.
- **Expected visible result:** H1/H3 supported in multiple horizons, H2/H4 inconclusive, H5 not evaluable; calibration summaries.
- **Say:** “Support is not universal: two behavior hypotheses are inconclusive, and the conditional comparison could not be evaluated with a chronologically eligible saved model vintage.”
- **Scientific interpretation:** Evidence status reflects saved uncertainty and the temporal protocol.
- **Limitation:** No operational alert policy is supported.
- **Backup:** Use ER-07 and ER-08 tables in `RESEARCH_EVIDENCE_REGISTER.md`.

## Step 9 — Hypothetical retention scenario (8:50–9:50)

- **Page URL:** `/revenue-exposure`
- **Action:** Open the scenario controls; if appropriate, keep the displayed defaults and label all assumptions as hypothetical.
- **Expected visible result:** Scenario outputs with budget, cost, response, or uplift assumptions.
- **Say:** “The calculation is conditional on these assumptions. It is not a measured campaign effect, recovered revenue, or profit estimate.”
- **Scientific interpretation:** A ranking or scenario is not evidence of treatment response.
- **Limitation:** Reference exposure remains not estimable; do not substitute forecast disagreement or the nonreturn proxy as loss.
- **Backup:** Show the financial definitions table in the evidence register.

## Step 10 — Trajectory Explorer (9:50–11:00)

- **Page URL:** `/trajectories`
- **Action:** Show history support, shape cluster counts, and functional analysis diagnostics.
- **Expected visible result:** Three descriptive shape clusters and method-specific eligibility counts.
- **Say:** “Only 1,100 TEST customers meet the selected shape-clustering support rule; 659 curves support functional analysis. The 98.82% figure is TRAIN-fitted explained variance, while TEST reconstruction RMSE is 0.006248.”
- **Scientific interpretation:** The two numbers describe different data roles.
- **Limitation:** Clusters are not risk ranks; incremental Purchase Clock value is inconclusive.
- **Backup:** Use Figure 8 and ER-10.

## Step 11 — Research Overview (11:00–12:10)

- **Page URL:** `/research`
- **Action:** Filter the hypothesis status and open one notebook/source entry.
- **Expected visible result:** Saved notebook registry, findings, status labels, and source provenance.
- **Say:** “This view is generated from saved evidence and hashes. It does not train another model.”
- **Scientific interpretation:** Every displayed result can be traced to a saved metric or notebook source.
- **Limitation:** Method-specific populations must be read with their support rules.
- **Backup:** Open `RESEARCH_EVIDENCE_REGISTER.md` and show the source-field rows.

## Step 12 — Architecture and validation (12:10–13:25)

- **Page URL:** `/research` (then show the architecture figure in the report)
- **Action:** Explain offline notebooks → saved artifacts → FastAPI → typed client → React.
- **Expected visible result:** Research evidence sources and the architecture diagram.
- **Say:** “The API serves saved artifacts; notebooks do not run in the page request path. The merged baseline passed regression checks and the 67-file protected-artifact comparison.”
- **Scientific interpretation:** The offline snapshot reduced cold trajectory summary latency from 4,261.8 to 311.9 ms; route splitting reduced initial-route gzip by 60.3%. These are local measurements and do not guarantee deployment performance.
- **Limitation:** Production deployment, Firefox/WebKit, and manual screen-reader testing were not validated.
- **Backup:** Use `SYSTEM_ARCHITECTURE.md` and `docs/qa/FINAL_REPORT.md`.

## Step 13 — Close with conclusions (13:25–15:00)

- **Page URL:** `/research`
- **Action:** Summarize the supported forecast result, mixed behavior findings, non-estimable exposure, and trajectory limitations.
- **Expected visible result:** Research summary and saved evidence status.
- **Say:** “The strongest claim is a historical TEST comparison among saved models. Behavior evidence is mixed, revenue exposure is not estimable, and no causal retention effect is identified.”
- **Scientific interpretation:** Findings are cohort- and method-specific.
- **Limitation:** Do not generalize this historical backtest to a live business without new validation.
- **Backup:** Read the report abstract and Chapter 11 conclusion.

## Walkthrough status

Record the actual page visits and interaction outcomes in `FINAL_SUBMISSION_CHECKLIST.md`. A spoken rehearsal is not claimed unless a person performs one.
