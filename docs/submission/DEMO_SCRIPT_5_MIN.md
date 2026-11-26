# Professor Demonstration Script — 5-Minute Backup

**Purpose:** A short path through the live app if time or connectivity is limited. Do not reveal individual TEST outcomes or claim a production deployment.

## Step 1 — Frame the dataset (0:00–0:35)

- **Page URL:** `/`
- **Action:** State Year 1 scope, historical cutoff, and the 30/60/90-day task.
- **Expected visible result:** Business Overview summary.
- **Say:** “This is a historical study, not a live customer forecast.”
- **Scientific interpretation:** All forecasts use an explicit cutoff and finite horizon.
- **Limitation:** Short, left-truncated history.
- **Backup:** Use the abstract and ER-01.

## Step 2 — Segments and forecast (0:35–1:35)

- **Page URL:** `/segments`, then `/forecasting`
- **Action:** Show the two descriptive RFM groups, then compare saved purchase probabilities by horizon.
- **Expected visible result:** Segment table and Global/Segment-aware/Personalized outputs.
- **Say:** “Segments describe observed history; the Purchase Clock estimates horizon-specific probability.”
- **Scientific interpretation:** Descriptive clustering and prediction are separate tasks.
- **Limitation:** A horizon non-purchase is not permanent churn.
- **Backup:** Use the report’s Figure 6 and ER-04/ER-05.

## Step 3 — Customer workflow (1:35–2:40)

- **Page URL:** `/intelligence`
- **Action:** Search customer `18102`; show cutoff-safe history and forecast summary without discussing any TEST label.
- **Expected visible result:** Customer profile, available saved forecasts, and explanation/reliability panels.
- **Say:** “The profile may include retrospective descriptive fields; forecasts use only the history available at cutoff.”
- **Scientific interpretation:** A model output is not an individual guarantee.
- **Limitation:** Sensitivity is noncausal and does not reveal customer intent.
- **Backup:** Show `assets/screenshots/research-overview.png` or the report’s customer workflow figure.

## Step 4 — Research evidence and limitations (2:40–4:05)

- **Page URL:** `/research`, optionally `/behavior`
- **Action:** Point to saved source links and status labels.
- **Expected visible result:** Findings, notebook registry, and provenance.
- **Say:** “H1/H3 are supported in multiple horizons, H2/H4 are inconclusive, and H5 is not evaluable. Campaign effects are not measured.”
- **Scientific interpretation:** Statuses are tied to saved tests, not narrative preference.
- **Limitation:** Reference exposure is not estimable; no operational alert policy is supported.
- **Backup:** Open `RESEARCH_EVIDENCE_REGISTER.md`.

## Step 5 — Close (4:05–5:00)

- **Page URL:** `/research`
- **Action:** Recap forecast, spending, and trajectory boundaries.
- **Expected visible result:** Research overview remains visible.
- **Say:** “The project is an auditable historical analysis with frozen models. Three descriptive trajectory clusters do not establish incremental prediction or causal retention value.”
- **Scientific interpretation:** The local cold summary API measurement improved from 4,261.8 to 311.9 ms, but process startup did not improve and the measurement is not a deployment SLA. Future business use requires longer prospective data and treatment-response evidence.
- **Limitation:** No live deployment validation is claimed.
- **Backup:** Use the report conclusion and Chapter 10 limitations.
