---
name: farmboy-metrics-report
description: Consolidate FarmBoy's local agent timing records into a simple Excel workbook. Use when explicitly requested from the FarmBoy maintainer checkout.
---

# FarmBoy Metrics Report

This maintainer-only skill is available in the FarmBoy source repository and is not delivered to consumer projects. When explicitly invoked, create one workbook from a fixed snapshot of the local metric files and leave those files unchanged.

## Before exporting

Run the source exporter from the FarmBoy checkout. Confirm that `.agents/skills/farmboy-metrics-report` resolves to `skills/farmboy-metrics-report`, that `skills/farmboy-metrics-report/scripts/metrics_report.py` and `controllers/farmboy/scripts/python/metrics.py` exist, and that `skills/farmboy-metrics-report/requirements.txt` declares `openpyxl==3.1.5` and `et-xmlfile`.

Before creating any output, check the approved dependencies with the skill-tools interpreter:

```bash
~/.codex/venvs/skill-tools/bin/python -c 'import openpyxl, et_xmlfile; assert openpyxl.__version__ == "3.1.5"'
```

If the source layout or dependency check fails, explain the specific issue and stop without creating output. Do not install packages or modify a Python environment.

## Create the workbook

Run the source script with the same interpreter:

```bash
~/.codex/venvs/skill-tools/bin/python skills/farmboy-metrics-report/scripts/metrics_report.py
```

The exporter reads one top-level snapshot from `~/.farmboy/metrics` and publishes a uniquely named workbook under `~/.farmboy/metrics/reports/`. It preserves input files and existing reports. Missing input is treated as an empty snapshot and produces a workbook with the thirteen headers and no data rows. Inaccessible input, dependency or layout problems, capacity limits, and output failures are errors; report the failure without claiming success.

After a successful run, show the workbook's portable location and the counts printed by the exporter: candidates, accepted rows, identical duplicates, conflicting invocation groups and files, skipped files, and any invalid-file counts. Do not include absolute host paths or metric contents in the summary. Do not launch another FarmBoy workflow or phase.
