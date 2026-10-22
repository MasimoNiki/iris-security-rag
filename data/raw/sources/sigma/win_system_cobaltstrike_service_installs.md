---
title: CobaltStrike Service Installations - System
source_type: sigma_rule
external_id: 5a105d34-05fc-401e-8553-272b45c1522d
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/system/service_control_manager/win_system_cobaltstrike_service_installs.yml
source_revision: 2022-11-27@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.persistence
- attack.execution
- attack.privilege-escalation
- attack.lateral-movement
- attack.t1021.002
- attack.t1543.003
- attack.t1569.002
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/system/service_control_manager/win_system_cobaltstrike_service_installs.yml
status: test
level: critical
author: Florian Roth (Nextron Systems), Wojciech Lesicki
date: '2021-05-26'
modified: '2022-11-27'
related: []
logsource:
  product: windows
  service: system
---

# CobaltStrike Service Installations - System

## Summary

Detects known malicious service installs that appear in cases in which a Cobalt Strike beacon elevates privileges or lateral movement

## Rule metadata

- Rule ID: 5a105d34-05fc-401e-8553-272b45c1522d
- Status: test
- Level: critical
- Author: Florian Roth (Nextron Systems), Wojciech Lesicki
- Created: 2021-05-26
- Modified: 2022-11-27
- Upstream path: rules/windows/builtin/system/service_control_manager/win_system_cobaltstrike_service_installs.yml

## Log source

```yaml
product: windows
service: system
```

## Detection logic

```yaml
selection_id:
  Provider_Name: Service Control Manager
  EventID: 7045
selection1:
  ImagePath|contains|all:
  - ADMIN$
  - .exe
selection2:
  ImagePath|contains|all:
  - '%COMSPEC%'
  - start
  - powershell
selection3:
  ImagePath|contains: powershell -nop -w hidden -encodedcommand
selection4:
  ImagePath|base64offset|contains: 'IEX (New-Object Net.Webclient).DownloadString(''http://127.0.0.1:'
condition: selection_id and (selection1 or selection2 or selection3 or selection4)
```

## False positives

- Unknown

## References

- https://www.sans.org/webcasts/119395
- https://www.crowdstrike.com/blog/getting-the-bacon-from-cobalt-strike-beacon/
- https://thedfirreport.com/2021/08/29/cobalt-strike-a-defenders-guide/

## ATT&CK and Sigma tags

- attack.persistence
- attack.execution
- attack.privilege-escalation
- attack.lateral-movement
- attack.t1021.002
- attack.t1543.003
- attack.t1569.002
