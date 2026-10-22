---
title: Suspicious Kernel Dump Using Dtrace
source_type: sigma_rule
external_id: 7124aebe-4cd7-4ccb-8df0-6d6b93c96795
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_dtrace_kernel_dump.yml
source_revision: 2021-12-28@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.discovery
- attack.t1082
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_dtrace_kernel_dump.yml
status: test
level: high
author: Florian Roth (Nextron Systems)
date: '2021-12-28'
modified: null
related: []
logsource:
  product: windows
  category: process_creation
---

# Suspicious Kernel Dump Using Dtrace

## Summary

Detects suspicious way to dump the kernel on Windows systems using dtrace.exe, which is available on Windows systems since Windows 10 19H1

## Rule metadata

- Rule ID: 7124aebe-4cd7-4ccb-8df0-6d6b93c96795
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2021-12-28
- Modified: Not specified
- Upstream path: rules/windows/process_creation/proc_creation_win_dtrace_kernel_dump.yml

## Log source

```yaml
product: windows
category: process_creation
```

## Detection logic

```yaml
selection_plain:
  Image|endswith: \dtrace.exe
  CommandLine|contains: lkd(0)
selection_obfuscated:
  CommandLine|contains|all:
  - syscall:::return
  - lkd(
condition: 1 of selection*
```

## False positives

- Unknown

## References

- https://twitter.com/0gtweet/status/1474899714290208777?s=12
- https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/dtrace

## ATT&CK and Sigma tags

- attack.discovery
- attack.t1082
