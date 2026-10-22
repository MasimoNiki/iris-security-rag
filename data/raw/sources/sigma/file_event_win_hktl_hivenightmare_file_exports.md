---
title: HackTool - Typical HiveNightmare SAM File Export
source_type: sigma_rule
external_id: 6ea858a8-ba71-4a12-b2cc-5d83312404c7
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/file/file_event/file_event_win_hktl_hivenightmare_file_exports.yml
source_revision: 2024-06-27@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.t1552.001
- cve.2021-36934
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/file/file_event/file_event_win_hktl_hivenightmare_file_exports.yml
status: test
level: high
author: Florian Roth (Nextron Systems)
date: '2021-07-23'
modified: '2024-06-27'
related: []
logsource:
  product: windows
  category: file_event
---

# HackTool - Typical HiveNightmare SAM File Export

## Summary

Detects files written by the different tools that exploit HiveNightmare

## Rule metadata

- Rule ID: 6ea858a8-ba71-4a12-b2cc-5d83312404c7
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2021-07-23
- Modified: 2024-06-27
- Upstream path: rules/windows/file/file_event/file_event_win_hktl_hivenightmare_file_exports.yml

## Log source

```yaml
product: windows
category: file_event
```

## Detection logic

```yaml
selection:
- TargetFilename|contains:
  - \hive_sam_
  - \SAM-2021-
  - \SAM-2022-
  - \SAM-2023-
  - \SAM-haxx
  - \Sam.save
- TargetFilename: C:\windows\temp\sam
condition: selection
```

## False positives

- Files that accidentally contain these strings

## References

- https://github.com/GossiTheDog/HiveNightmare
- https://github.com/FireFart/hivenightmare/
- https://github.com/WiredPulse/Invoke-HiveNightmare
- https://twitter.com/cube0x0/status/1418920190759378944

## ATT&CK and Sigma tags

- attack.credential-access
- attack.t1552.001
- cve.2021-36934
