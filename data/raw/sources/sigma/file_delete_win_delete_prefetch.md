---
title: Prefetch File Deleted
source_type: sigma_rule
external_id: 0a1f9d29-6465-4776-b091-7f43b26e4c89
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/file/file_delete/file_delete_win_delete_prefetch.yml
source_revision: 2024-01-25@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.stealth
- attack.t1070.004
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/file/file_delete/file_delete_win_delete_prefetch.yml
status: test
level: high
author: Cedric MAURUGEON
date: '2021-09-29'
modified: '2024-01-25'
related: []
logsource:
  product: windows
  category: file_delete
---

# Prefetch File Deleted

## Summary

Detects the deletion of a prefetch file which may indicate an attempt to destroy forensic evidence

## Rule metadata

- Rule ID: 0a1f9d29-6465-4776-b091-7f43b26e4c89
- Status: test
- Level: high
- Author: Cedric MAURUGEON
- Created: 2021-09-29
- Modified: 2024-01-25
- Upstream path: rules/windows/file/file_delete/file_delete_win_delete_prefetch.yml

## Log source

```yaml
product: windows
category: file_delete
```

## Detection logic

```yaml
selection:
  TargetFilename|contains: :\Windows\Prefetch\
  TargetFilename|endswith: .pf
filter_main_svchost:
  Image|endswith: :\windows\system32\svchost.exe
  User|contains:
  - AUTHORI
  - AUTORI
condition: selection and not 1 of filter_main_*
```

## False positives

- Unknown

## References

- Internal Research
- https://www.group-ib.com/blog/hunting-for-ttps-with-prefetch-files/

## ATT&CK and Sigma tags

- attack.stealth
- attack.t1070.004
