---
title: ProcessHacker Privilege Elevation
source_type: sigma_rule
external_id: c4ff1eac-84ad-44dd-a6fb-d56a92fc43a9
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/system/service_control_manager/win_system_service_install_pua_proceshacker.yml
source_revision: 2022-12-25@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.persistence
- attack.execution
- attack.privilege-escalation
- attack.t1543.003
- attack.t1569.002
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/system/service_control_manager/win_system_service_install_pua_proceshacker.yml
status: test
level: high
author: Florian Roth (Nextron Systems)
date: '2021-05-27'
modified: '2022-12-25'
related: []
logsource:
  product: windows
  service: system
---

# ProcessHacker Privilege Elevation

## Summary

Detects a ProcessHacker tool that elevated privileges to a very high level

## Rule metadata

- Rule ID: c4ff1eac-84ad-44dd-a6fb-d56a92fc43a9
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2021-05-27
- Modified: 2022-12-25
- Upstream path: rules/windows/builtin/system/service_control_manager/win_system_service_install_pua_proceshacker.yml

## Log source

```yaml
product: windows
service: system
```

## Detection logic

```yaml
selection:
  Provider_Name: Service Control Manager
  EventID: 7045
  ServiceName|startswith: ProcessHacker
  AccountName: LocalSystem
condition: selection
```

## False positives

- Unlikely

## References

- https://twitter.com/1kwpeter/status/1397816101455765504

## ATT&CK and Sigma tags

- attack.persistence
- attack.execution
- attack.privilege-escalation
- attack.t1543.003
- attack.t1569.002
