---
title: HackTool - Potential Impacket Lateral Movement Activity
source_type: sigma_rule
external_id: 10c14723-61c7-4c75-92ca-9af245723ad2
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_hktl_impacket_lateral_movement.yml
source_revision: 2023-02-21@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.execution
- attack.t1047
- attack.lateral-movement
- attack.t1021.003
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_hktl_impacket_lateral_movement.yml
status: stable
level: high
author: Ecco, oscd.community, Jonhnathan Ribeiro, Tim Rauch
date: '2019-09-03'
modified: '2023-02-21'
related:
- id: e31f89f7-36fb-4697-8ab6-48823708353b
  type: obsolete
logsource:
  category: process_creation
  product: windows
---

# HackTool - Potential Impacket Lateral Movement Activity

## Summary

Detects wmiexec/dcomexec/atexec/smbexec from Impacket framework

## Rule metadata

- Rule ID: 10c14723-61c7-4c75-92ca-9af245723ad2
- Status: stable
- Level: high
- Author: Ecco, oscd.community, Jonhnathan Ribeiro, Tim Rauch
- Created: 2019-09-03
- Modified: 2023-02-21
- Upstream path: rules/windows/process_creation/proc_creation_win_hktl_impacket_lateral_movement.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection_other:
  ParentImage|endswith:
  - \wmiprvse.exe
  - \mmc.exe
  - \explorer.exe
  - \services.exe
  CommandLine|contains|all:
  - cmd.exe
  - /Q
  - /c
  - \\\\127.0.0.1\\
  - '&1'
selection_atexec:
  ParentCommandLine|contains:
  - svchost.exe -k netsvcs
  - taskeng.exe
  CommandLine|contains|all:
  - cmd.exe
  - /C
  - Windows\Temp\
  - '&1'
condition: 1 of selection_*
```

## False positives

- Unknown

## References

- https://github.com/SecureAuthCorp/impacket/blob/8b1a99f7c715702eafe3f24851817bb64721b156/examples/wmiexec.py
- https://github.com/SecureAuthCorp/impacket/blob/8b1a99f7c715702eafe3f24851817bb64721b156/examples/atexec.py
- https://github.com/SecureAuthCorp/impacket/blob/8b1a99f7c715702eafe3f24851817bb64721b156/examples/smbexec.py
- https://github.com/SecureAuthCorp/impacket/blob/8b1a99f7c715702eafe3f24851817bb64721b156/examples/dcomexec.py
- https://www.elastic.co/guide/en/security/current/suspicious-cmd-execution-via-wmi.html

## ATT&CK and Sigma tags

- attack.execution
- attack.t1047
- attack.lateral-movement
- attack.t1021.003
