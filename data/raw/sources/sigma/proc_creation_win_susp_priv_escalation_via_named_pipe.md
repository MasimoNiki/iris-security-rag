---
title: Privilege Escalation via Named Pipe Impersonation
source_type: sigma_rule
external_id: 9bd04a79-dabe-4f1f-a5ff-92430265c96b
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_susp_priv_escalation_via_named_pipe.yml
source_revision: 2022-12-30@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.lateral-movement
- attack.t1021
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_susp_priv_escalation_via_named_pipe.yml
status: test
level: high
author: Tim Rauch, Elastic (idea)
date: '2022-09-27'
modified: '2022-12-30'
related:
- id: f35c5d71-b489-4e22-a115-f003df287317
  type: derived
logsource:
  category: process_creation
  product: windows
---

# Privilege Escalation via Named Pipe Impersonation

## Summary

Detects a remote file copy attempt to a hidden network share. This may indicate lateral movement or data staging activity.

## Rule metadata

- Rule ID: 9bd04a79-dabe-4f1f-a5ff-92430265c96b
- Status: test
- Level: high
- Author: Tim Rauch, Elastic (idea)
- Created: 2022-09-27
- Modified: 2022-12-30
- Upstream path: rules/windows/process_creation/proc_creation_win_susp_priv_escalation_via_named_pipe.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection_name:
- Image|endswith:
  - \cmd.exe
  - \powershell.exe
- OriginalFileName:
  - Cmd.Exe
  - PowerShell.EXE
selection_args:
  CommandLine|contains|all:
  - echo
  - '>'
  - \\\\.\\pipe\\
condition: all of selection*
```

## False positives

- Other programs that cause these patterns (please report)

## References

- https://www.elastic.co/guide/en/security/current/privilege-escalation-via-named-pipe-impersonation.html

## ATT&CK and Sigma tags

- attack.lateral-movement
- attack.t1021
