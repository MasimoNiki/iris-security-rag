---
title: Potential Credential Dumping Via LSASS Process Clone
source_type: sigma_rule
external_id: c8da0dfd-4ed0-4b68-962d-13c9c884384e
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_lsass_process_clone.yml
source_revision: 2023-03-02@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.t1003
- attack.t1003.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_lsass_process_clone.yml
status: test
level: critical
author: Florian Roth (Nextron Systems), Samir Bousseaden
date: '2021-11-27'
modified: '2023-03-02'
related: []
logsource:
  category: process_creation
  product: windows
---

# Potential Credential Dumping Via LSASS Process Clone

## Summary

Detects a suspicious LSASS process process clone that could be a sign of credential dumping activity

## Rule metadata

- Rule ID: c8da0dfd-4ed0-4b68-962d-13c9c884384e
- Status: test
- Level: critical
- Author: Florian Roth (Nextron Systems), Samir Bousseaden
- Created: 2021-11-27
- Modified: 2023-03-02
- Upstream path: rules/windows/process_creation/proc_creation_win_lsass_process_clone.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  ParentImage|endswith: \Windows\System32\lsass.exe
  Image|endswith: \Windows\System32\lsass.exe
condition: selection
```

## False positives

- Unknown

## References

- https://www.matteomalvica.com/blog/2019/12/02/win-defender-atp-cred-bypass/
- https://twitter.com/Hexacorn/status/1420053502554951689
- https://twitter.com/SBousseaden/status/1464566846594691073?s=20

## ATT&CK and Sigma tags

- attack.credential-access
- attack.t1003
- attack.t1003.001
