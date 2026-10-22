---
title: Suspicious Desktopimgdownldr Target File
source_type: sigma_rule
external_id: fc4f4817-0c53-4683-a4ee-b17a64bc1039
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/file/file_event/file_event_win_susp_desktopimgdownldr_file.yml
source_revision: 2022-06-02@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.command-and-control
- attack.t1105
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/file/file_event/file_event_win_susp_desktopimgdownldr_file.yml
status: test
level: high
author: Florian Roth (Nextron Systems)
date: '2020-07-03'
modified: '2022-06-02'
related: []
logsource:
  product: windows
  category: file_event
---

# Suspicious Desktopimgdownldr Target File

## Summary

Detects a suspicious Microsoft desktopimgdownldr file creation that stores a file to a suspicious location or contains a file with a suspicious extension

## Rule metadata

- Rule ID: fc4f4817-0c53-4683-a4ee-b17a64bc1039
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2020-07-03
- Modified: 2022-06-02
- Upstream path: rules/windows/file/file_event/file_event_win_susp_desktopimgdownldr_file.yml

## Log source

```yaml
product: windows
category: file_event
```

## Detection logic

```yaml
selection:
  Image|endswith: \svchost.exe
  TargetFilename|contains: \Personalization\LockScreenImage\
filter1:
  TargetFilename|contains: C:\Windows\
filter2:
  TargetFilename|contains:
  - .jpg
  - .jpeg
  - .png
condition: selection and not filter1 and not filter2
```

## False positives

- False positives depend on scripts and administrative tools used in the monitored environment

## References

- https://labs.sentinelone.com/living-off-windows-land-a-new-native-file-downldr/
- https://twitter.com/SBousseaden/status/1278977301745741825

## ATT&CK and Sigma tags

- attack.command-and-control
- attack.t1105
