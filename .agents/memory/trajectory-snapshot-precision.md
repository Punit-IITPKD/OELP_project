---
name: Trajectory snapshot precision
description: Why serialized trajectory serving records use a normalized float precision.
---

Normalize floating-point values to 12 decimal places when serializing trajectory dataframes into the checked-in serving snapshot.

**Why:** Rebuilding the same derived snapshot in the pinned runtime produced last-decimal differences in trajectory slope features. Exact gzip-byte verification otherwise failed despite unchanged inputs, models, and meaningful results.

**How to apply:** Keep this normalization in the offline snapshot serialization layer; do not round or rewrite the saved trajectory models, research metrics, or Purchase Clock and spending predictions.
