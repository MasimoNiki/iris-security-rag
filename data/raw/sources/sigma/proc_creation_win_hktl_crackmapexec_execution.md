---
title: HackTool - CrackMapExec Execution
source_type: sigma_rule
external_id: 42a993dd-bb3e-48c8-b372-4d6684c4106c
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_hktl_crackmapexec_execution.yml
source_revision: 2023-03-08@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.execution
- attack.persistence
- attack.privilege-escalation
- attack.credential-access
- attack.discovery
- attack.t1047
- attack.t1053
- attack.t1059.003
- attack.t1059.001
- attack.t1110
- attack.t1201
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_hktl_crackmapexec_execution.yml
status: test
level: high
author: Florian Roth (Nextron Systems)
date: '2022-02-25'
modified: '2023-03-08'
related: []
logsource:
  category: process_creation
  product: windows
---

# HackTool - CrackMapExec Execution

## Summary

This rule detect common flag combinations used by CrackMapExec in order to detect its use even if the binary has been replaced.

## Rule metadata

- Rule ID: 42a993dd-bb3e-48c8-b372-4d6684c4106c
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2022-02-25
- Modified: 2023-03-08
- Upstream path: rules/windows/process_creation/proc_creation_win_hktl_crackmapexec_execution.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection_binary:
  Image|endswith: \crackmapexec.exe
selection_special:
  CommandLine|contains: ' -M pe_inject '
selection_execute:
  CommandLine|contains|all:
  - ' --local-auth'
  - ' -u '
  - ' -x '
selection_hash:
  CommandLine|contains|all:
  - ' --local-auth'
  - ' -u '
  - ' -p '
  - ' -H ''NTHASH'''
selection_module_mssql:
  CommandLine|contains|all:
  - ' mssql '
  - ' -u '
  - ' -p '
  - ' -M '
  - ' -d '
selection_module_smb1:
  CommandLine|contains|all:
  - ' smb '
  - ' -u '
  - ' -H '
  - ' -M '
  - ' -o '
selection_module_smb2:
  CommandLine|contains|all:
  - ' smb '
  - ' -u '
  - ' -p '
  - ' --local-auth'
part_localauth_1:
  CommandLine|contains|all:
  - ' --local-auth'
  - ' -u '
  - ' -p '
part_localauth_2:
  CommandLine|contains|all:
  - ' 10.'
  - ' 192.168.'
  - '/24 '
condition: 1 of selection_* or all of part_localauth*
```

## False positives

- Unknown

## References

- https://mpgn.gitbook.io/crackmapexec/smb-protocol/authentication/checking-credentials-local
- https://www.mandiant.com/resources/telegram-malware-iranian-espionage
- https://www.infosecmatter.com/crackmapexec-module-library/?cmem=mssql-mimikatz
- https://www.infosecmatter.com/crackmapexec-module-library/?cmem=smb-pe_inject

## ATT&CK and Sigma tags

- attack.execution
- attack.persistence
- attack.privilege-escalation
- attack.credential-access
- attack.discovery
- attack.t1047
- attack.t1053
- attack.t1059.003
- attack.t1059.001
- attack.t1110
- attack.t1201
