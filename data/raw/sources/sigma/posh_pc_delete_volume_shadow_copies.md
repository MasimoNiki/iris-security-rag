---
title: Delete Volume Shadow Copies Via WMI With PowerShell
source_type: sigma_rule
external_id: 87df9ee1-5416-453a-8a08-e8d4a51e9ce1
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/powershell/powershell_classic/posh_pc_delete_volume_shadow_copies.yml
source_revision: 2023-10-27@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.impact
- attack.t1490
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/powershell/powershell_classic/posh_pc_delete_volume_shadow_copies.yml
status: stable
level: high
author: frack113
date: '2021-06-03'
modified: '2023-10-27'
related: []
logsource:
  product: windows
  category: ps_classic_start
---

# Delete Volume Shadow Copies Via WMI With PowerShell

## Summary

Shadow Copies deletion using operating systems utilities via PowerShell

## Rule metadata

- Rule ID: 87df9ee1-5416-453a-8a08-e8d4a51e9ce1
- Status: stable
- Level: high
- Author: frack113
- Created: 2021-06-03
- Modified: 2023-10-27
- Upstream path: rules/windows/powershell/powershell_classic/posh_pc_delete_volume_shadow_copies.yml

## Log source

```yaml
product: windows
category: ps_classic_start
```

## Detection logic

```yaml
selection:
  Data|contains|all:
  - Get-WmiObject
  - Win32_ShadowCopy
  Data|contains:
  - Delete()
  - Remove-WmiObject
condition: selection
```

## False positives

- Legitimate Administrator deletes Shadow Copies using operating systems utilities for legitimate reason

## References

- https://github.com/redcanaryco/atomic-red-team/blob/f339e7da7d05f6057fdfcdd3742bfcf365fee2a9/atomics/T1490/T1490.md
- https://www.fortinet.com/blog/threat-research/stomping-shadow-copies-a-second-look-into-deletion-methods

## ATT&CK and Sigma tags

- attack.impact
- attack.t1490
