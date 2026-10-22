---
title: Password Dumper Remote Thread in LSASS
source_type: sigma_rule
external_id: f239b326-2f41-4d6b-9dfa-c846a60ef505
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/create_remote_thread/create_remote_thread_win_susp_password_dumper_lsass.yml
source_revision: 2021-06-21@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.s0005
- attack.t1003.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/create_remote_thread/create_remote_thread_win_susp_password_dumper_lsass.yml
status: stable
level: high
author: Thomas Patzke
date: '2017-02-19'
modified: '2021-06-21'
related: []
logsource:
  product: windows
  category: create_remote_thread
---

# Password Dumper Remote Thread in LSASS

## Summary

Detects password dumper activity by monitoring remote thread creation EventID 8 in combination with the lsass.exe process as TargetImage.
The process in field Process is the malicious program. A single execution can lead to hundreds of events.

## Rule metadata

- Rule ID: f239b326-2f41-4d6b-9dfa-c846a60ef505
- Status: stable
- Level: high
- Author: Thomas Patzke
- Created: 2017-02-19
- Modified: 2021-06-21
- Upstream path: rules/windows/create_remote_thread/create_remote_thread_win_susp_password_dumper_lsass.yml

## Log source

```yaml
product: windows
category: create_remote_thread
```

## Detection logic

```yaml
selection:
  TargetImage|endswith: \lsass.exe
  StartModule: ''
condition: selection
```

## False positives

- Antivirus products

## References

- https://jpcertcc.github.io/ToolAnalysisResultSheet/details/WCE.htm

## ATT&CK and Sigma tags

- attack.credential-access
- attack.s0005
- attack.t1003.001
