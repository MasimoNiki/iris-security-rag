---
title: Potential Regsvr32 Commandline Flag Anomaly
source_type: sigma_rule
external_id: b236190c-1c61-41e9-84b3-3fe03f6d76b0
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_regsvr32_flags_anomaly.yml
source_revision: 2024-03-13@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.stealth
- attack.t1218.010
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_regsvr32_flags_anomaly.yml
status: test
level: medium
author: Florian Roth (Nextron Systems)
date: '2019-07-13'
modified: '2024-03-13'
related: []
logsource:
  category: process_creation
  product: windows
---

# Potential Regsvr32 Commandline Flag Anomaly

## Summary

Detects a potential command line flag anomaly related to "regsvr32" in which the "/i" flag is used without the "/n" which should be uncommon.

## Rule metadata

- Rule ID: b236190c-1c61-41e9-84b3-3fe03f6d76b0
- Status: test
- Level: medium
- Author: Florian Roth (Nextron Systems)
- Created: 2019-07-13
- Modified: 2024-03-13
- Upstream path: rules/windows/process_creation/proc_creation_win_regsvr32_flags_anomaly.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  Image|endswith: \regsvr32.exe
  CommandLine|contains|windash: ' -i:'
filter_main_flag:
  CommandLine|contains|windash: ' -n '
condition: selection and not 1 of filter_main_*
```

## False positives

- Administrator typo might cause some false positives

## References

- https://twitter.com/sbousseaden/status/1282441816986484737?s=12

## ATT&CK and Sigma tags

- attack.stealth
- attack.t1218.010
