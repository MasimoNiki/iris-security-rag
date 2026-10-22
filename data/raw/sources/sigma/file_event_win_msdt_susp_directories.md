---
title: File Creation In Suspicious Directory By Msdt.EXE
source_type: sigma_rule
external_id: 318557a5-150c-4c8d-b70e-a9910e199857
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/file/file_event/file_event_win_msdt_susp_directories.yml
source_revision: 2023-02-23@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.privilege-escalation
- attack.persistence
- attack.t1547.001
- cve.2022-30190
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/file/file_event/file_event_win_msdt_susp_directories.yml
status: test
level: high
author: Vadim Varganov, Florian Roth (Nextron Systems)
date: '2022-08-24'
modified: '2023-02-23'
related: []
logsource:
  category: file_event
  product: windows
---

# File Creation In Suspicious Directory By Msdt.EXE

## Summary

Detects msdt.exe creating files in suspicious directories which could be a sign of exploitation of either Follina or Dogwalk vulnerabilities

## Rule metadata

- Rule ID: 318557a5-150c-4c8d-b70e-a9910e199857
- Status: test
- Level: high
- Author: Vadim Varganov, Florian Roth (Nextron Systems)
- Created: 2022-08-24
- Modified: 2023-02-23
- Upstream path: rules/windows/file/file_event/file_event_win_msdt_susp_directories.yml

## Log source

```yaml
category: file_event
product: windows
```

## Detection logic

```yaml
selection:
  Image|endswith: \msdt.exe
  TargetFilename|contains:
  - \Desktop\
  - \Start Menu\Programs\Startup\
  - C:\PerfLogs\
  - C:\ProgramData\
  - C:\Users\Public\
condition: selection
```

## False positives

- Unknown

## References

- https://irsl.medium.com/the-trouble-with-microsofts-troubleshooters-6e32fc80b8bd
- https://msrc-blog.microsoft.com/2022/05/30/guidance-for-cve-2022-30190-microsoft-support-diagnostic-tool-vulnerability/

## ATT&CK and Sigma tags

- attack.privilege-escalation
- attack.persistence
- attack.t1547.001
- cve.2022-30190
