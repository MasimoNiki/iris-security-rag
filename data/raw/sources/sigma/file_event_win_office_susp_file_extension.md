---
title: File With Uncommon Extension Created By An Office Application
source_type: sigma_rule
external_id: c7a74c80-ba5a-486e-9974-ab9e682bc5e4
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/file/file_event/file_event_win_office_susp_file_extension.yml
source_revision: 2025-10-17@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.t1204.002
- attack.execution
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/file/file_event/file_event_win_office_susp_file_extension.yml
status: test
level: high
author: Vadim Khrykov (ThreatIntel), Cyb3rEng (Rule), Nasreddine Bencherchali (Nextron
  Systems)
date: '2021-08-23'
modified: '2025-10-17'
related: []
logsource:
  product: windows
  category: file_event
---

# File With Uncommon Extension Created By An Office Application

## Summary

Detects the creation of files with an executable or script extension by an Office application.

## Rule metadata

- Rule ID: c7a74c80-ba5a-486e-9974-ab9e682bc5e4
- Status: test
- Level: high
- Author: Vadim Khrykov (ThreatIntel), Cyb3rEng (Rule), Nasreddine Bencherchali (Nextron Systems)
- Created: 2021-08-23
- Modified: 2025-10-17
- Upstream path: rules/windows/file/file_event/file_event_win_office_susp_file_extension.yml

## Log source

```yaml
product: windows
category: file_event
```

## Detection logic

```yaml
selection1:
  Image|endswith:
  - \excel.exe
  - \msaccess.exe
  - \mspub.exe
  - \powerpnt.exe
  - \visio.exe
  - \winword.exe
selection2:
  TargetFilename|endswith:
  - .bat
  - .cmd
  - .com
  - .dll
  - .exe
  - .hta
  - .ocx
  - .proj
  - .ps1
  - .scf
  - .scr
  - .sys
  - .vbe
  - .vbs
  - .wsf
  - .wsh
filter_main_localassembly:
  TargetFilename|contains: \AppData\Local\assembly\tmp\
  TargetFilename|endswith: .dll
filter_optional_webservicecache:
  TargetFilename|contains|all:
  - C:\Users\
  - \AppData\Local\Microsoft\Office\
  - \WebServiceCache\AllUsers
  TargetFilename|endswith: .com
filter_optional_webex:
  Image|endswith: \winword.exe
  TargetFilename|contains: \AppData\Local\Temp\webexdelta\
  TargetFilename|endswith:
  - .dll
  - .exe
filter_optional_backstageinappnavcache:
  TargetFilename|contains|all:
  - C:\Users\
  - \AppData\Local\Microsoft\Office\
  - \BackstageInAppNavCache\
  TargetFilename|endswith: .com
condition: all of selection* and not 1 of filter_main_* and not 1 of filter_optional_*
```

## False positives

- Unknown

## References

- https://thedfirreport.com/2021/03/29/sodinokibi-aka-revil-ransomware/
- https://github.com/vadim-hunter/Detection-Ideas-Rules/blob/02bcbfc2bfb8b4da601bb30de0344ae453aa1afe/Threat%20Intelligence/The%20DFIR%20Report/20210329_Sodinokibi_(aka_REvil)_Ransomware.yaml

## ATT&CK and Sigma tags

- attack.t1204.002
- attack.execution
