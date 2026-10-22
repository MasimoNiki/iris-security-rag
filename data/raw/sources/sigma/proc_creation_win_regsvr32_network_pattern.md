---
title: Potentially Suspicious Regsvr32 HTTP/FTP Pattern
source_type: sigma_rule
external_id: 867356ee-9352-41c9-a8f2-1be690d78216
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_regsvr32_network_pattern.yml
source_revision: 2023-05-26@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.stealth
- attack.t1218.010
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_regsvr32_network_pattern.yml
status: test
level: medium
author: Florian Roth (Nextron Systems)
date: '2023-05-24'
modified: '2023-05-26'
related:
- id: 8e2b24c9-4add-46a0-b4bb-0057b4e6187d
  type: obsolete
logsource:
  category: process_creation
  product: windows
---

# Potentially Suspicious Regsvr32 HTTP/FTP Pattern

## Summary

Detects regsvr32 execution to download/install/register new DLLs that are hosted on Web or FTP servers.

## Rule metadata

- Rule ID: 867356ee-9352-41c9-a8f2-1be690d78216
- Status: test
- Level: medium
- Author: Florian Roth (Nextron Systems)
- Created: 2023-05-24
- Modified: 2023-05-26
- Upstream path: rules/windows/process_creation/proc_creation_win_regsvr32_network_pattern.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection_img:
- Image|endswith: \regsvr32.exe
- OriginalFileName: REGSVR32.EXE
selection_flag:
  CommandLine|contains:
  - ' /i'
  - ' -i'
selection_protocol:
  CommandLine|contains:
  - ftp
  - http
condition: all of selection_*
```

## False positives

- Unknown

## References

- https://twitter.com/mrd0x/status/1461041276514623491
- https://twitter.com/tccontre18/status/1480950986650832903
- https://lolbas-project.github.io/lolbas/Binaries/Regsvr32/

## ATT&CK and Sigma tags

- attack.stealth
- attack.t1218.010
