# Baseline cache

Open after recording Q1A. This contains the complete, fresh-seed confirmation baseline for `configs/baseline.json`: 72 matched problems, two conditions. It contains no organizer follow-up results.

`baseline.jsonl` stores raw responses and exact prompts. Adjacent metadata records the model revision, settings, measured runtime, and source/request hashes. The source snapshot is the script used to generate the cache. Problem seed `2026092017` was selected after calibration on different seeds; difficulty/settings were frozen before this run.

New runs are not expected to reproduce every sampled answer exactly across hardware, batch sizes, or dependency versions. Use matched problems and disclose which results you reuse. The cache was generated on a single H100 PCIe 80 GB; first-time installation and downloads are not included in its timing.

The source snapshot preserves the original generation script. The current starter adds uncertainty to plots and summaries; the supplied raw results, metadata, and historical source snapshot are unchanged.
