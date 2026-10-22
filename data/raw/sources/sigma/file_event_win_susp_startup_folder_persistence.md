---
title: Suspicious Startup Folder Persistence
source_type: sigma_rule
external_id: 28208707-fe31-437f-9a7f-4b1108b94d2e
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/file/file_event/file_event_win_susp_startup_folder_persistence.yml
source_revision: 2025-10-12@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.privilege-escalation
- attack.execution
- attack.t1204.002
- attack.persistence
- attack.t1547.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/file/file_event/file_event_win_susp_startup_folder_persistence.yml
status: test
level: high
author: Nasreddine Bencherchali (Nextron Systems), Swachchhanda Shrawan Poudel (Nextron
  Systems)
date: '2022-08-10'
modified: '2025-10-12'
related:
- id: 2aa0a6b4-a865-495b-ab51-c28249537b75
  type: similar
logsource:
  product: windows
  category: file_event
---

# Suspicious Startup Folder Persistence

## Summary

Detects the creation of potentially malicious script and executable files in Windows startup folders, which is a common persistence technique used by threat actors.
These files (.ps1, .vbs, .js, .bat, etc.) are automatically executed when a user logs in, making the Startup folder an attractive target for attackers.
This technique is frequently observed in malvertising campaigns and malware distribution where attackers attempt to maintain long-term access to compromised systems.

## Rule metadata

- Rule ID: 28208707-fe31-437f-9a7f-4b1108b94d2e
- Status: test
- Level: high
- Author: Nasreddine Bencherchali (Nextron Systems), Swachchhanda Shrawan Poudel (Nextron Systems)
- Created: 2022-08-10
- Modified: 2025-10-12
- Upstream path: rules/windows/file/file_event/file_event_win_susp_startup_folder_persistence.yml

## Log source

```yaml
product: windows
category: file_event
```

## Detection logic

```yaml
selection:
  TargetFilename|contains: \Windows\Start Menu\Programs\Startup\
  TargetFilename|endswith:
  - .bat
  - .cmd
  - .dll
  - .hta
  - .jar
  - .js
  - .jse
  - .msi
  - .ps1
  - .psd1
  - .psm1
  - .scr
  - .url
  - .vba
  - .vbe
  - .vbs
  - .wsf
condition: selection
```

## False positives

- Rare legitimate usage of some of the extensions mentioned in the rule

## References

- https://github.com/last-byte/PersistenceSniper
- https://www.microsoft.com/en-us/security/blog/2025/03/06/malvertising-campaign-leads-to-info-stealers-hosted-on-github/
- https://github.com/redcanaryco/atomic-red-team/blob/5ede8f21e42ebe37e0a6eff757dba60bcfa85859/atomics/T1547.001/T1547.001.md

## ATT&CK and Sigma tags

- attack.privilege-escalation
- attack.execution
- attack.t1204.002
- attack.persistence
- attack.t1547.001
