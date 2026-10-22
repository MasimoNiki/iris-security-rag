---
title: PUA - Netcat Suspicious Execution
source_type: sigma_rule
external_id: e31033fc-33f0-4020-9a16-faf9b31cbf08
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_pua_netcat.yml
source_revision: 2023-02-08@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.command-and-control
- attack.t1095
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_pua_netcat.yml
status: test
level: high
author: frack113, Florian Roth (Nextron Systems)
date: '2021-07-21'
modified: '2023-02-08'
related: []
logsource:
  category: process_creation
  product: windows
---

# PUA - Netcat Suspicious Execution

## Summary

Detects execution of Netcat. Adversaries may use a non-application layer protocol for communication between host and C2 server or among infected hosts within a network

## Rule metadata

- Rule ID: e31033fc-33f0-4020-9a16-faf9b31cbf08
- Status: test
- Level: high
- Author: frack113, Florian Roth (Nextron Systems)
- Created: 2021-07-21
- Modified: 2023-02-08
- Upstream path: rules/windows/process_creation/proc_creation_win_pua_netcat.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection_img:
  Image|endswith:
  - \nc.exe
  - \ncat.exe
  - \netcat.exe
selection_cmdline:
  CommandLine|contains:
  - ' -lvp '
  - ' -lvnp'
  - ' -l -v -p '
  - ' -lv -p '
  - ' -l --proxy-type http '
  - ' -vnl --exec '
  - ' -vnl -e '
  - ' --lua-exec '
  - ' --sh-exec '
condition: 1 of selection_*
```

## False positives

- Legitimate ncat use

## References

- https://nmap.org/ncat/
- https://github.com/redcanaryco/atomic-red-team/blob/f339e7da7d05f6057fdfcdd3742bfcf365fee2a9/atomics/T1095/T1095.md
- https://www.revshells.com/

## ATT&CK and Sigma tags

- attack.command-and-control
- attack.t1095
