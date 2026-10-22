---
title: HackTool - CrackMapExec Execution Patterns
source_type: sigma_rule
external_id: 058f4380-962d-40a5-afce-50207d36d7e2
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_hktl_crackmapexec_execution_patterns.yml
source_revision: 2023-11-06@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.privilege-escalation
- attack.persistence
- attack.execution
- attack.t1047
- attack.t1053
- attack.t1059.003
- attack.t1059.001
- attack.s0106
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_hktl_crackmapexec_execution_patterns.yml
status: stable
level: high
author: Thomas Patzke
date: '2020-05-22'
modified: '2023-11-06'
related: []
logsource:
  category: process_creation
  product: windows
---

# HackTool - CrackMapExec Execution Patterns

## Summary

Detects various execution patterns of the CrackMapExec pentesting framework

## Rule metadata

- Rule ID: 058f4380-962d-40a5-afce-50207d36d7e2
- Status: stable
- Level: high
- Author: Thomas Patzke
- Created: 2020-05-22
- Modified: 2023-11-06
- Upstream path: rules/windows/process_creation/proc_creation_win_hktl_crackmapexec_execution_patterns.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  CommandLine|contains:
  - cmd.exe /Q /c * 1> \\\\*\\*\\* 2>&1
  - cmd.exe /C * > \\\\*\\*\\* 2>&1
  - cmd.exe /C * > *\\Temp\\* 2>&1
  - powershell.exe -exec bypass -noni -nop -w 1 -C "
  - 'powershell.exe -noni -nop -w 1 -enc '
condition: selection
```

## False positives

- Unknown

## References

- https://github.com/byt3bl33d3r/CrackMapExec

## ATT&CK and Sigma tags

- attack.privilege-escalation
- attack.persistence
- attack.execution
- attack.t1047
- attack.t1053
- attack.t1059.003
- attack.t1059.001
- attack.s0106
