---
title: WCE wceaux.dll Access
source_type: sigma_rule
external_id: 1de68c67-af5c-4097-9c85-fe5578e09e67
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/security/win_security_mal_wceaux_dll.yml
source_revision: 2025-01-30@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.t1003
- attack.s0005
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/security/win_security_mal_wceaux_dll.yml
status: test
level: critical
author: Thomas Patzke
date: '2017-06-14'
modified: '2025-01-30'
related: []
logsource:
  product: windows
  service: security
---

# WCE wceaux.dll Access

## Summary

Detects wceaux.dll access while WCE pass-the-hash remote command execution on source host

## Rule metadata

- Rule ID: 1de68c67-af5c-4097-9c85-fe5578e09e67
- Status: test
- Level: critical
- Author: Thomas Patzke
- Created: 2017-06-14
- Modified: 2025-01-30
- Upstream path: rules/windows/builtin/security/win_security_mal_wceaux_dll.yml

## Log source

```yaml
product: windows
service: security
```

## Detection logic

```yaml
selection:
  EventID:
  - 4656
  - 4663
  ObjectName|endswith: \wceaux.dll
condition: selection
```

## False positives

- Unknown

## References

- https://www.jpcert.or.jp/english/pub/sr/ir_research.html
- https://jpcertcc.github.io/ToolAnalysisResultSheet

## ATT&CK and Sigma tags

- attack.credential-access
- attack.t1003
- attack.s0005
