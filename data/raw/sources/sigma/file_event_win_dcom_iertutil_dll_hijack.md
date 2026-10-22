---
title: Potential DCOM InternetExplorer.Application DLL Hijack
source_type: sigma_rule
external_id: 2f7979ae-f82b-45af-ac1d-2b10e93b0baa
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/file/file_event/file_event_win_dcom_iertutil_dll_hijack.yml
source_revision: 2022-12-18@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.lateral-movement
- attack.t1021.002
- attack.t1021.003
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/file/file_event/file_event_win_dcom_iertutil_dll_hijack.yml
status: test
level: critical
author: Roberto Rodriguez @Cyb3rWard0g, Open Threat Research (OTR), wagga
date: '2020-10-12'
modified: '2022-12-18'
related:
- id: e554f142-5cf3-4e55-ace9-a1b59e0def65
  type: obsolete
- id: f354eba5-623b-450f-b073-0b5b2773b6aa
  type: similar
logsource:
  product: windows
  category: file_event
---

# Potential DCOM InternetExplorer.Application DLL Hijack

## Summary

Detects potential DLL hijack of "iertutil.dll" found in the DCOM InternetExplorer.Application Class over the network

## Rule metadata

- Rule ID: 2f7979ae-f82b-45af-ac1d-2b10e93b0baa
- Status: test
- Level: critical
- Author: Roberto Rodriguez @Cyb3rWard0g, Open Threat Research (OTR), wagga
- Created: 2020-10-12
- Modified: 2022-12-18
- Upstream path: rules/windows/file/file_event/file_event_win_dcom_iertutil_dll_hijack.yml

## Log source

```yaml
product: windows
category: file_event
```

## Detection logic

```yaml
selection:
  Image: System
  TargetFilename|endswith: \Internet Explorer\iertutil.dll
condition: selection
```

## False positives

- Unknown

## References

- https://threathunterplaybook.com/hunts/windows/201009-RemoteDCOMIErtUtilDLLHijack/notebook.html

## ATT&CK and Sigma tags

- attack.lateral-movement
- attack.t1021.002
- attack.t1021.003
