---
title: HackTool - SharpUp PrivEsc Tool Execution
source_type: sigma_rule
external_id: c484e533-ee16-4a93-b6ac-f0ea4868b2f1
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_hktl_sharpup.yml
source_revision: 2023-02-13@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.persistence
- attack.privilege-escalation
- attack.discovery
- attack.execution
- attack.stealth
- attack.t1615
- attack.t1569.002
- attack.t1574.005
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_hktl_sharpup.yml
status: test
level: critical
author: Florian Roth (Nextron Systems)
date: '2022-08-20'
modified: '2023-02-13'
related: []
logsource:
  category: process_creation
  product: windows
---

# HackTool - SharpUp PrivEsc Tool Execution

## Summary

Detects the use of SharpUp, a tool for local privilege escalation

## Rule metadata

- Rule ID: c484e533-ee16-4a93-b6ac-f0ea4868b2f1
- Status: test
- Level: critical
- Author: Florian Roth (Nextron Systems)
- Created: 2022-08-20
- Modified: 2023-02-13
- Upstream path: rules/windows/process_creation/proc_creation_win_hktl_sharpup.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
- Image|endswith: \SharpUp.exe
- Description: SharpUp
- CommandLine|contains:
  - HijackablePaths
  - UnquotedServicePath
  - ProcessDLLHijack
  - ModifiableServiceBinaries
  - ModifiableScheduledTask
  - DomainGPPPassword
  - CachedGPPPassword
condition: selection
```

## False positives

- Unknown

## References

- https://github.com/GhostPack/SharpUp

## ATT&CK and Sigma tags

- attack.persistence
- attack.privilege-escalation
- attack.discovery
- attack.execution
- attack.stealth
- attack.t1615
- attack.t1569.002
- attack.t1574.005
