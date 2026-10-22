---
title: Credential Dumping Activity By Python Based Tool
source_type: sigma_rule
external_id: f8be3e82-46a3-4e4e-ada5-8e538ae8b9c9
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_access/proc_access_win_lsass_python_based_tool.yml
source_revision: 2023-11-29@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.t1003.001
- attack.s0349
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_access/proc_access_win_lsass_python_based_tool.yml
status: stable
level: high
author: Bhabesh Raj, Jonhnathan Ribeiro
date: '2023-11-27'
modified: '2023-11-29'
related:
- id: 4b9a8556-99c4-470b-a40c-9c8d02c77ed0
  type: obsolete
- id: 7186e989-4ed7-4f4e-a656-4674b9e3e48b
  type: obsolete
logsource:
  category: process_access
  product: windows
---

# Credential Dumping Activity By Python Based Tool

## Summary

Detects LSASS process access for potential credential dumping by a Python-like tool such as LaZagne or Pypykatz.

## Rule metadata

- Rule ID: f8be3e82-46a3-4e4e-ada5-8e538ae8b9c9
- Status: stable
- Level: high
- Author: Bhabesh Raj, Jonhnathan Ribeiro
- Created: 2023-11-27
- Modified: 2023-11-29
- Upstream path: rules/windows/process_access/proc_access_win_lsass_python_based_tool.yml

## Log source

```yaml
category: process_access
product: windows
```

## Detection logic

```yaml
selection:
  TargetImage|endswith: \lsass.exe
  CallTrace|contains|all:
  - _ctypes.pyd+
  - :\Windows\System32\KERNELBASE.dll+
  - :\Windows\SYSTEM32\ntdll.dll+
  CallTrace|contains:
  - python27.dll+
  - python3*.dll+
  GrantedAccess: '0x1FFFFF'
condition: selection
```

## False positives

- Unknown

## References

- https://twitter.com/bh4b3sh/status/1303674603819081728
- https://github.com/skelsec/pypykatz

## ATT&CK and Sigma tags

- attack.credential-access
- attack.t1003.001
- attack.s0349
