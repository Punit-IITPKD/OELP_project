# Phase 8 frontend and browser validation

## Browser coverage

The Playwright release-readiness suite passed **28/28** checks using Chromium
155. It covered the 10 application routes at desktop width and at a 360 px
small-phone width.

The suite exercised:

- Route rendering with live API data and no page-level server errors.
- Mobile document width and navigation behavior.
- Navigation, browser back/forward, refresh, and deep-link state.
- Keyboard focus for navigation links and scrollable tables.
- Customer 18102 forecast, explanation, and historical reliability context.
- Research links to stable `main` documentation and notebook locations.
- In-memory synthetic CSV preview, analysis, and export.
- Hypothetical retention scenario and six-strategy comparison.
- Error display and recovery after a simulated temporary API failure.
- axe-core checks on every route, with no serious or critical findings.

React unit tests passed **32/32**. Typechecking and the production build passed.

## Visual review

The running preview was inspected at desktop 1440×1000 and mobile 402×874.
The business overview, research evidence cards, and compact mobile navigation
rendered without visible clipping. Automated 360 px checks found no
document-level horizontal overflow.

Screenshots and machine-readable browser reports are kept under
`generated-artifacts/phase8-qa/` and are excluded from source commits.

## Browser limits

Only Chromium was available for this run. Firefox, WebKit, screen-reader
testing, and Lighthouse were not executed. The axe result is an automated
check, not a substitute for manual assistive-technology review.
