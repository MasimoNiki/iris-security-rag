---
title: Remote LSASS Process Access Through Windows Remote Management
source_type: sigma_rule
external_id: aa35a627-33fb-4d04-a165-d33b4afca3e8
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_access/proc_access_win_lsass_remote_access_trough_winrm.yml
source_revision: 2023-11-29@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.execution
- attack.t1003.001
- attack.t1059.001
- attack.lateral-movement
- attack.t1021.006
- attack.s0002
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_access/proc_access_win_lsass_remote_access_trough_winrm.yml
status: stable
level: high
author: Patryk Prauze - ING Tech
date: '2019-05-20'
modified: '2023-11-29'
related: []
logsource:
  category: process_access
  product: windows
---

# Remote LSASS Process Access Through Windows Remote Management

## Summary

Detects remote access to the LSASS process via WinRM. This could be a sign of credential dumping from tools like mimikatz.

## Rule metadata

- Rule ID: aa35a627-33fb-4d04-a165-d33b4afca3e8
- Status: stable
- Level: high
- Author: Patryk Prauze - ING Tech
- Created: 2019-05-20
- Modified: 2023-11-29
- Upstream path: rules/windows/process_access/proc_access_win_lsass_remote_access_trough_winrm.yml

## Log source

```yaml
category: process_access
product: windows
```

## Detection logic

```yaml
selection:
  TargetImage|endswith: \lsass.exe
  SourceImage|endswith: :\Windows\system32\wsmprovhost.exe
filter_main_access:
  GrantedAccess: '0x80000000'
condition: selection and not 1 of filter_main_*
```

## False positives

- Unlikely

## References

- https://pentestlab.blog/2018/05/15/lateral-movement-winrm/

## ATT&CK and Sigma tags

- attack.credential-access
- attack.execution
- attack.t1003.001
- attack.t1059.001
- attack.lateral-movement
- attack.t1021.006
- attack.s0002
