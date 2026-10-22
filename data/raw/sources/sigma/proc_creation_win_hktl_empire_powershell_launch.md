---
title: HackTool - Empire PowerShell Launch Parameters
source_type: sigma_rule
external_id: 79f4ede3-402e-41c8-bc3e-ebbf5f162581
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_hktl_empire_powershell_launch.yml
source_revision: 2023-02-21@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.execution
- attack.t1059.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_hktl_empire_powershell_launch.yml
status: test
level: high
author: Florian Roth (Nextron Systems)
date: '2019-04-20'
modified: '2023-02-21'
related: []
logsource:
  category: process_creation
  product: windows
---

# HackTool - Empire PowerShell Launch Parameters

## Summary

Detects suspicious powershell command line parameters used in Empire

## Rule metadata

- Rule ID: 79f4ede3-402e-41c8-bc3e-ebbf5f162581
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2019-04-20
- Modified: 2023-02-21
- Upstream path: rules/windows/process_creation/proc_creation_win_hktl_empire_powershell_launch.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  CommandLine|contains:
  - ' -NoP -sta -NonI -W Hidden -Enc '
  - ' -noP -sta -w 1 -enc '
  - ' -NoP -NonI -W Hidden -enc '
  - ' -noP -sta -w 1 -enc'
  - ' -enc  SQB'
  - ' -nop -exec bypass -EncodedCommand '
condition: selection
```

## False positives

- Other tools that incidentally use the same command line parameters

## References

- https://github.com/EmpireProject/Empire/blob/c2ba61ca8d2031dad0cfc1d5770ba723e8b710db/lib/common/helpers.py#L165
- https://github.com/EmpireProject/Empire/blob/e37fb2eef8ff8f5a0a689f1589f424906fe13055/lib/modules/powershell/persistence/powerbreach/deaduser.py#L191
- https://github.com/EmpireProject/Empire/blob/e37fb2eef8ff8f5a0a689f1589f424906fe13055/lib/modules/powershell/persistence/powerbreach/resolver.py#L178
- https://github.com/EmpireProject/Empire/blob/e37fb2eef8ff8f5a0a689f1589f424906fe13055/data/module_source/privesc/Invoke-EventVwrBypass.ps1#L64

## ATT&CK and Sigma tags

- attack.execution
- attack.t1059.001
