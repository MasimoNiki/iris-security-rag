---
title: Password Protected ZIP File Opened (Email Attachment)
source_type: sigma_rule
external_id: 571498c8-908e-40b4-910b-d2369159a3da
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/security/win_security_susp_opened_encrypted_zip_outlook.yml
source_revision: 2022-05-09@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.initial-access
- attack.stealth
- attack.t1027
- attack.t1566.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/security/win_security_susp_opened_encrypted_zip_outlook.yml
status: test
level: high
author: Florian Roth (Nextron Systems)
date: '2022-05-09'
modified: null
related: []
logsource:
  product: windows
  service: security
---

# Password Protected ZIP File Opened (Email Attachment)

## Summary

Detects the extraction of password protected ZIP archives. See the filename variable for more details on which file has been opened.

## Rule metadata

- Rule ID: 571498c8-908e-40b4-910b-d2369159a3da
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2022-05-09
- Modified: Not specified
- Upstream path: rules/windows/builtin/security/win_security_susp_opened_encrypted_zip_outlook.yml

## Log source

```yaml
product: windows
service: security
```

## Detection logic

```yaml
selection:
  EventID: 5379
  TargetName|contains|all:
  - Microsoft_Windows_Shell_ZipFolder:filename
  - \Temporary Internet Files\Content.Outlook
condition: selection
```

## False positives

- Legitimate used of encrypted ZIP files

## References

- https://twitter.com/sbousseaden/status/1523383197513379841

## ATT&CK and Sigma tags

- attack.initial-access
- attack.stealth
- attack.t1027
- attack.t1566.001
