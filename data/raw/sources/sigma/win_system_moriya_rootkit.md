---
title: Moriya Rootkit - System
source_type: sigma_rule
external_id: 25b9c01c-350d-4b95-bed1-836d04a4f324
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/system/service_control_manager/win_system_moriya_rootkit.yml
source_revision: 2022-11-29@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.persistence
- attack.privilege-escalation
- attack.t1543.003
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/system/service_control_manager/win_system_moriya_rootkit.yml
status: test
level: critical
author: Bhabesh Raj
date: '2021-05-06'
modified: '2022-11-29'
related: []
logsource:
  product: windows
  service: system
---

# Moriya Rootkit - System

## Summary

Detects the use of Moriya rootkit as described in the securelist's Operation TunnelSnake report

## Rule metadata

- Rule ID: 25b9c01c-350d-4b95-bed1-836d04a4f324
- Status: test
- Level: critical
- Author: Bhabesh Raj
- Created: 2021-05-06
- Modified: 2022-11-29
- Upstream path: rules/windows/builtin/system/service_control_manager/win_system_moriya_rootkit.yml

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
  ServiceName: ZzNetSvc
condition: selection
```

## False positives

- Unknown

## References

- https://securelist.com/operation-tunnelsnake-and-moriya-rootkit/101831

## ATT&CK and Sigma tags

- attack.persistence
- attack.privilege-escalation
- attack.t1543.003
