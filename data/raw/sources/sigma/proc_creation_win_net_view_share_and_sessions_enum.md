---
title: Share And Session Enumeration Using Net.EXE
source_type: sigma_rule
external_id: 62510e69-616b-4078-b371-847da438cc03
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_net_view_share_and_sessions_enum.yml
source_revision: 2023-02-21@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.discovery
- attack.t1018
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_net_view_share_and_sessions_enum.yml
status: stable
level: low
author: Endgame, JHasenbusch (ported for oscd.community)
date: '2018-10-30'
modified: '2023-02-21'
related: []
logsource:
  category: process_creation
  product: windows
---

# Share And Session Enumeration Using Net.EXE

## Summary

Detects attempts to enumerate file shares, printer shares and sessions using "net.exe" with the "view" flag.

## Rule metadata

- Rule ID: 62510e69-616b-4078-b371-847da438cc03
- Status: stable
- Level: low
- Author: Endgame, JHasenbusch (ported for oscd.community)
- Created: 2018-10-30
- Modified: 2023-02-21
- Upstream path: rules/windows/process_creation/proc_creation_win_net_view_share_and_sessions_enum.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection_img:
- Image|endswith:
  - \net.exe
  - \net1.exe
- OriginalFileName:
  - net.exe
  - net1.exe
selection_cli:
  CommandLine|contains: view
filter:
  CommandLine|contains: \\\\
condition: all of selection_* and not filter
```

## False positives

- Legitimate use of net.exe utility by legitimate user

## References

- https://eqllib.readthedocs.io/en/latest/analytics/b8a94d2f-dc75-4630-9d73-1edc6bd26fff.html
- https://github.com/redcanaryco/atomic-red-team/blob/f339e7da7d05f6057fdfcdd3742bfcf365fee2a9/atomics/T1018/T1018.md

## ATT&CK and Sigma tags

- attack.discovery
- attack.t1018
