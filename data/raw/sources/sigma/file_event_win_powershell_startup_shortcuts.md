---
title: Potential Startup Shortcut Persistence Via PowerShell.EXE
source_type: sigma_rule
external_id: 92fa78e7-4d39-45f1-91a3-8b23f3f1088d
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/file/file_event/file_event_win_powershell_startup_shortcuts.yml
source_revision: 2023-02-23@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.privilege-escalation
- attack.persistence
- attack.t1547.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/file/file_event/file_event_win_powershell_startup_shortcuts.yml
status: test
level: high
author: Christopher Peacock '@securepeacock', SCYTHE
date: '2021-10-24'
modified: '2023-02-23'
related: []
logsource:
  product: windows
  category: file_event
---

# Potential Startup Shortcut Persistence Via PowerShell.EXE

## Summary

Detects PowerShell writing startup shortcuts.
This procedure was highlighted in Red Canary Intel Insights Oct. 2021, "We frequently observe adversaries using PowerShell to write malicious .lnk files into the startup directory to establish persistence.
Accordingly, this detection opportunity is likely to identify persistence mechanisms in multiple threats.
In the context of Yellow Cockatoo, this persistence mechanism eventually launches the command-line script that leads to the installation of a malicious DLL"

## Rule metadata

- Rule ID: 92fa78e7-4d39-45f1-91a3-8b23f3f1088d
- Status: test
- Level: high
- Author: Christopher Peacock '@securepeacock', SCYTHE
- Created: 2021-10-24
- Modified: 2023-02-23
- Upstream path: rules/windows/file/file_event/file_event_win_powershell_startup_shortcuts.yml

## Log source

```yaml
product: windows
category: file_event
```

## Detection logic

```yaml
selection:
  Image|endswith:
  - \powershell.exe
  - \pwsh.exe
  TargetFilename|contains: \start menu\programs\startup\
  TargetFilename|endswith: .lnk
condition: selection
```

## False positives

- Depending on your environment accepted applications may leverage this at times. It is recommended to search for anomalies inidicative of malware.

## References

- https://redcanary.com/blog/intelligence-insights-october-2021/
- https://github.com/redcanaryco/atomic-red-team/blob/36d49de4c8b00bf36054294b4a1fcbab3917d7c5/atomics/T1547.001/T1547.001.md#atomic-test-7---add-executable-shortcut-link-to-user-startup-folder

## ATT&CK and Sigma tags

- attack.privilege-escalation
- attack.persistence
- attack.t1547.001
