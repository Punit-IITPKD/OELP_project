# PR #1 integration fixes

## Validation protocol

The final purchase-clock model remains trained on the March 1, 2010 90-day TRAIN cohort. Its TRAIN outcomes mature by May 30, and its regularization is selected using the June 1 VAL cohort with outcomes through August 30. It is therefore finalized in time for the September 10 TEST cutoff, but not for the June 1 joint validation forecast.

For the July 1 and August 1 joint validation forecasts, Notebook 07 builds a separate chronological purchase-model vintage: January 1 TRAIN and April 1 VAL. The 90-day validation outcomes mature by June 30, before those forecast cutoffs. This vintage selects `C=0.1` and is saved separately from the final test model.

The June 1 90-day joint validation result is explicitly marked `retrospective/exploratory`; the purchase-model configuration used there was selected with outcomes through August 30. Horizon-specific conditional-spending training and selection remain unchanged. No TEST outcomes are used for fitting or configuration selection.

## Segmentation and inference

- The saved March 1 TRAIN-fitted StandardScaler and K-Means transformation exactly reproduces the purchase-clock segment labels in the 90-day TRAIN, VAL, and TEST splits.
- Spending inference stores and applies a separate TRAIN-fitted segmentation transformation for each horizon. Labels from independently fitted horizon models are checked rather than treated as interchangeable.
- The September 10 purchase-clock P30/P60/P90 predictions are computed once from one customer feature snapshot and reused across all spending horizons. Customer IDs, cutoffs, and monotonic probability ordering are verified.
- The purchase-clock and spending-model interfaces work together from a single raw feature snapshot, without Jupyter.

## Verification

- `pytest`: **38 passed**.
- Notebooks 06 and 07: all code cells executed with no recorded errors.
- Both checked-in model bundles reload successfully.
- Prediction exports contain no future outcome labels; TEST metrics use the same 3,373 customers at each horizon.
- The local GitHub Actions workflow installs only NumPy, pandas, scikit-learn, joblib, and pytest, then runs the complete test suite on pull requests to `main`.

## TEST metric changes

The corrected shared segmentation changes the 30-day and 60-day two-stage TEST forecasts slightly. Historical-rate metrics and all 90-day metrics are unchanged. Latest joint two-stage RMSE values are:

| Horizon | Segment-aware | Personalized |
| --- | ---: | ---: |
| 30 days | 1,012.54 | 871.30 |
| 60 days | 1,870.18 | 1,466.12 |
| 90 days | 2,881.40 | 2,111.73 |

These are the results from the regenerated forecasts and metrics; previous metric values are not reproduced here.
