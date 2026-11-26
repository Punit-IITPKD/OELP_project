# Phase 8 security and accessibility results

## Security scanners

The final Replit scans reported:

| Scanner | Result |
|---|---|
| Dependency audit | 0 critical, 0 high, 0 moderate advisories |
| Static analysis | 0 findings |
| Privacy/dataflow | 0 findings |

The audit was initially affected by vulnerable lower bounds in the broad
research requirements and an old resolved CSS parser. Patched minimums were
added for AnyIO, certifi, idna, nbconvert, and Pillow; the workspace lock now
resolves `postcss-selector-parser` to 6.1.6. The exact production/CI
environment remains defined by the unchanged `requirements-ci.txt` lock.
Resolving `requirements.txt` for Python 3.11 succeeded with the patched
versions.

## Access control and data handling

The app has no account, login, or role-based access-control feature. This QA
run did not add one. A deployment must be treated as public unless a separate
access-control layer is configured.

The upload browser test uses a small synthetic CSV in memory and checks
preview, analysis, and export. No real customer file was used or persisted.
The interface labels saved forecasts as historical and explicitly identifies
retention scenarios as assumptions rather than causal treatment effects.

## Accessibility

axe-core ran on all 10 routes at the tested viewport. No serious or critical
violations were reported. The suite also checked:

- Keyboard focus reaches navigation links and scrollable data tables.
- Tables that overflow can receive focus and expose a region label.
- Charts have accessible summaries while decorative SVG content is hidden
  from the accessibility tree.
- The tested routes do not overflow the 360 px viewport horizontally.

This is automated coverage only. Manual screen-reader and cross-browser
accessibility review remain outstanding.
