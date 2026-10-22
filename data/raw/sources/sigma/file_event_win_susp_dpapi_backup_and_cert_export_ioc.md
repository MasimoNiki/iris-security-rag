---
title: DPAPI Backup Keys And Certificate Export Activity IOC
source_type: sigma_rule
external_id: 7892ec59-c5bb-496d-8968-e5d210ca3ac4
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/file/file_event/file_event_win_susp_dpapi_backup_and_cert_export_ioc.yml
source_revision: 2024-06-26@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.t1555
- attack.t1552.004
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/file/file_event/file_event_win_susp_dpapi_backup_and_cert_export_ioc.yml
status: test
level: high
author: Nounou Mbeiri, Nasreddine Bencherchali (Nextron Systems)
date: '2024-06-26'
modified: null
related: []
logsource:
  product: windows
  category: file_event
---

# DPAPI Backup Keys And Certificate Export Activity IOC

## Summary

Detects file names with specific patterns seen generated and used by tools such as Mimikatz and DSInternals related to exported or stolen DPAPI backup keys and certificates.

## Rule metadata

- Rule ID: 7892ec59-c5bb-496d-8968-e5d210ca3ac4
- Status: test
- Level: high
- Author: Nounou Mbeiri, Nasreddine Bencherchali (Nextron Systems)
- Created: 2024-06-26
- Modified: Not specified
- Upstream path: rules/windows/file/file_event/file_event_win_susp_dpapi_backup_and_cert_export_ioc.yml

## Log source

```yaml
product: windows
category: file_event
```

## Detection logic

```yaml
selection:
  TargetFilename|contains:
  - ntds_capi_
  - ntds_legacy_
  - ntds_unknown_
  TargetFilename|endswith:
  - .cer
  - .key
  - .pfx
  - .pvk
condition: selection
```

## False positives

- Unlikely

## References

- https://www.dsinternals.com/en/dpapi-backup-key-theft-auditing/
- https://github.com/MichaelGrafnetter/DSInternals/blob/39ee8a69bbdc1cfd12c9afdd7513b4788c4895d4/Src/DSInternals.Common/Data/DPAPI/DPAPIBackupKey.cs#L28-L32

## ATT&CK and Sigma tags

- attack.credential-access
- attack.t1555
- attack.t1552.004
