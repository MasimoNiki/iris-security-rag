---
title: HackTool - PCHunter Execution
source_type: sigma_rule
external_id: fca949cc-79ca-446e-8064-01aa7e52ece5
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_hktl_pchunter.yml
source_revision: 2024-11-23@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.execution
- attack.discovery
- attack.t1082
- attack.t1057
- attack.t1012
- attack.t1083
- attack.t1007
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_hktl_pchunter.yml
status: test
level: high
author: Florian Roth (Nextron Systems), Nasreddine Bencherchali
date: '2022-10-10'
modified: '2024-11-23'
related: []
logsource:
  category: process_creation
  product: windows
---

# HackTool - PCHunter Execution

## Summary

Detects suspicious use of PCHunter, a tool like Process Hacker to view and manipulate processes, kernel options and other low level stuff

## Rule metadata

- Rule ID: fca949cc-79ca-446e-8064-01aa7e52ece5
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems), Nasreddine Bencherchali
- Created: 2022-10-10
- Modified: 2024-11-23
- Upstream path: rules/windows/process_creation/proc_creation_win_hktl_pchunter.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection_image:
  Image|endswith:
  - \PCHunter64.exe
  - \PCHunter32.exe
selection_pe:
- OriginalFileName: PCHunter.exe
- Description: Epoolsoft Windows Information View Tools
selection_hashes:
  Hashes|contains:
  - SHA1=5F1CBC3D99558307BC1250D084FA968521482025
  - MD5=987B65CD9B9F4E9A1AFD8F8B48CF64A7
  - SHA256=2B214BDDAAB130C274DE6204AF6DBA5AEEC7433DA99AA950022FA306421A6D32
  - IMPHASH=444D210CEA1FF8112F256A4997EED7FF
  - SHA1=3FB89787CB97D902780DA080545584D97FB1C2EB
  - MD5=228DD0C2E6287547E26FFBD973A40F14
  - SHA256=55F041BF4E78E9BFA6D4EE68BE40E496CE3A1353E1CA4306598589E19802522C
  - IMPHASH=0479F44DF47CFA2EF1CCC4416A538663
condition: 1 of selection_*
```

## False positives

- Unlikely

## References

- https://web.archive.org/web/20231210115125/http://www.xuetr.com/
- https://www.crowdstrike.com/blog/falcon-overwatch-report-finds-increase-in-ecrime/
- https://www.hexacorn.com/blog/2018/04/20/kernel-hacking-tool-you-might-have-never-heard-of-xuetr-pchunter/

## ATT&CK and Sigma tags

- attack.execution
- attack.discovery
- attack.t1082
- attack.t1057
- attack.t1012
- attack.t1083
- attack.t1007
