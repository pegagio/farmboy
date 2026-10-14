---
title: Maintainer metrics report discovery
type: howto
sources:
- S005
updated: 2026-10-14
---

# Maintainer metrics report discovery

The [installation lifecycle](./installation-and-release-lifecycle.md) separates consumer delivery from maintainer discovery: consumers receive the collection helper, while the catalog excludes `farmboy-metrics-report` and its `openpyxl` dependency. Report discovery belongs to the FarmBoy source checkout. (S005)

The guide documents a local `.agents/skills/farmboy-metrics-report` symlink targeting reviewed `skills/farmboy-metrics-report/` source. That symlink is checkout-local discovery state and is excluded from consumer installation; documenting it does not establish that it exists. (S005)

Workflows and other consuming projects share separate JSON timing files under `~/.farmboy/metrics/`. Collection measures local wall-clock milliseconds around observed turns, excludes human-answer waits, and warns on timing or storage failure without changing the workflow result. (S005)

Reporting requires explicit `$farmboy-metrics-report` invocation in a maintainer checkout. The skill checks reviewed source and approved spreadsheet dependencies before export, preserves source JSON files, and writes a uniquely named workbook under `~/.farmboy/metrics/reports/`. Its result reports snapshot counts and workbook location. These delivery instructions do not prove invocation, successful export, publication or acceptance. (S005)
