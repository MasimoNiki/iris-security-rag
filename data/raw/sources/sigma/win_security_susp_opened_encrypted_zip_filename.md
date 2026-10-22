---
title: Password Protected ZIP File Opened (Suspicious Filenames)
source_type: sigma_rule
external_id: 54f0434b-726f-48a1-b2aa-067df14516e4
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/security/win_security_susp_opened_encrypted_zip_filename.yml
source_revision: 2022-05-09@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.command-and-control
- attack.stealth
- attack.t1027
- attack.t1105
- attack.t1036
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/security/win_security_susp_opened_encrypted_zip_filename.yml
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

# Password Protected ZIP File Opened (Suspicious Filenames)

## Summary

Detects the extraction of password protected ZIP archives with suspicious file names. See the filename variable for more details on which file has been opened.

## Rule metadata

- Rule ID: 54f0434b-726f-48a1-b2aa-067df14516e4
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2022-05-09
- Modified: Not specified
- Upstream path: rules/windows/builtin/security/win_security_susp_opened_encrypted_zip_filename.yml

## Log source

```yaml
product: windows
service: security
```

## Detection logic

```yaml
selection:
  EventID: 5379
  TargetName|contains: Microsoft_Windows_Shell_ZipFolder:filename
selection_filename:
  TargetName|contains:
  - invoice
  - new order
  - rechnung
  - factura
  - delivery
  - purchase
  - order
  - payment
condition: selection and selection_filename
```

## False positives

- Legitimate used of encrypted ZIP files

## References

- https://twitter.com/sbousseaden/status/1523383197513379841

## ATT&CK and Sigma tags

- attack.command-and-control
- attack.stealth
- attack.t1027
- attack.t1105
- attack.t1036
