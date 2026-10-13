---
name: farmboy-metrics-report
description: Consolidate FarmBoy's local agent timing records into a simple Excel workbook. Use when explicitly requested from the FarmBoy maintainer checkout.
---

# FarmBoy Metrics Report

This maintainer-only skill is kept in the FarmBoy source repository and is not installed into consumer projects. It will combine local metric records into one Excel workbook while preserving the source records.

This source scaffold is not a working exporter yet. The reporting script and its execution checks are added by later implementation tasks. Until `scripts/metrics_report.py` exists and those checks are in place, do not claim a workbook was generated.

The approved workbook dependencies are declared in `requirements.txt`. Do not install them automatically or change a Python environment as part of reporting.
