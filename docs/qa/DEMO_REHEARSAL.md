# Phase 8 demonstration readiness

## Browser-exercised core flow

Playwright completed these flows against the running app:

1. Open the historical business overview and check the saved-data window and
   forecast cutoff disclosures.
2. Open customer 18102 and inspect the forecast, its explanation, and
   historical reliability context.
3. Open the Research Overview and follow a durable `main`-branch source link.
4. Upload a synthetic CSV, inspect its preview and descriptive analysis, and
   download the cleaned export.
5. Change hypothetical campaign assumptions, run a scenario, and compare all
   six supported ranking strategies.
6. Navigate across routes, refresh, use browser history, and retry after a
   temporary API error.

The browser automation passed. This was not a timed 10–15 minute spoken
presentation rehearsal.

## Suggested presentation boundaries

- State that the data covers UCI Online Retail Year 1, 2009–2010.
- Explain that saved forecasts use a historical cutoff of 2010-09-10.
- Treat customer examples as historical demonstrations, not current
  recommendations.
- Describe scenario outputs as analyst-supplied assumptions; do not call them
  measured lift or treatment effects.
- Use the Research Overview links to show the source notebooks and final
  evaluation.

## Recovery plan

If the API is unavailable, do not imply the displayed data is current. The
tested interface shows a retryable error instead of stale dashboard metrics.
Use the QA screenshots in `generated-artifacts/phase8-qa/` only to explain the
interface, not as evidence of live service availability.
