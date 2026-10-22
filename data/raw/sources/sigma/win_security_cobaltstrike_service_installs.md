---
title: CobaltStrike Service Installations - Security
source_type: sigma_rule
external_id: d7a95147-145f-4678-b85d-d1ff4a3bb3f6
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/security/win_security_cobaltstrike_service_installs.yml
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
upstream_path: rules/windows/builtin/security/win_security_cobaltstrike_service_installs.yml
status: test
level: high
author: Florian Roth (Nextron Systems), Wojciech Lesicki
date: '2021-05-26'
modified: '2022-11-27'
related:
- id: 5a105d34-05fc-401e-8553-272b45c1522d
  type: derived
logsource:
  product: windows
  service: security
  definition: The 'System Security Extension' audit subcategory need to be enabled
    to log the EID 4697
---

# CobaltStrike Service Installations - Security

## Summary

Detects known malicious service installs that appear in cases in which a Cobalt Strike beacon elevates privileges or lateral movement

## Rule metadata

- Rule ID: d7a95147-145f-4678-b85d-d1ff4a3bb3f6
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems), Wojciech Lesicki
- Created: 2021-05-26
- Modified: 2022-11-27
- Upstream path: rules/windows/builtin/security/win_security_cobaltstrike_service_installs.yml

## Log source

```yaml
product: windows
service: security
definition: The 'System Security Extension' audit subcategory need to be enabled to
  log the EID 4697
```

## Detection logic

```yaml
event_id:
  EventID: 4697
selection1:
  ServiceFileName|contains|all:
  - ADMIN$
  - .exe
selection2:
  ServiceFileName|contains|all:
  - '%COMSPEC%'
  - start
  - powershell
selection3:
  ServiceFileName|contains: powershell -nop -w hidden -encodedcommand
selection4:
  ServiceFileName|base64offset|contains: 'IEX (New-Object Net.Webclient).DownloadString(''http://127.0.0.1:'
condition: event_id and 1 of selection*
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
