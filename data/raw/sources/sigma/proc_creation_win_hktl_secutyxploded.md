---
title: HackTool - SecurityXploded Execution
source_type: sigma_rule
external_id: 7679d464-4f74-45e2-9e01-ac66c5eb041a
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_hktl_secutyxploded.yml
source_revision: 2023-02-04@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.t1555
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_hktl_secutyxploded.yml
status: stable
level: critical
author: Florian Roth (Nextron Systems)
date: '2018-12-19'
modified: '2023-02-04'
related: []
logsource:
  category: process_creation
  product: windows
---

# HackTool - SecurityXploded Execution

## Summary

Detects the execution of SecurityXploded Tools

## Rule metadata

- Rule ID: 7679d464-4f74-45e2-9e01-ac66c5eb041a
- Status: stable
- Level: critical
- Author: Florian Roth (Nextron Systems)
- Created: 2018-12-19
- Modified: 2023-02-04
- Upstream path: rules/windows/process_creation/proc_creation_win_hktl_secutyxploded.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
- Company: SecurityXploded
- Image|endswith: PasswordDump.exe
- OriginalFileName|endswith: PasswordDump.exe
condition: selection
```

## False positives

- Unlikely

## References

- https://securityxploded.com/
- https://web.archive.org/web/20200601000524/https://cyberx-labs.com/blog/gangnam-industrial-style-apt-campaign-targets-korean-industrial-companies/

## ATT&CK and Sigma tags

- attack.credential-access
- attack.t1555
