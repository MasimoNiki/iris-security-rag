---
title: Hacktool Ruler
source_type: sigma_rule
external_id: 24549159-ac1b-479c-8175-d42aea947cae
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/security/win_security_alert_ruler.yml
source_revision: 2022-10-09@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.discovery
- attack.execution
- attack.collection
- attack.lateral-movement
- attack.t1087
- attack.t1114
- attack.t1059
- attack.t1550.002
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/security/win_security_alert_ruler.yml
status: test
level: high
author: Florian Roth (Nextron Systems)
date: '2017-05-31'
modified: '2022-10-09'
related: []
logsource:
  product: windows
  service: security
---

# Hacktool Ruler

## Summary

This events that are generated when using the hacktool Ruler by Sensepost

## Rule metadata

- Rule ID: 24549159-ac1b-479c-8175-d42aea947cae
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2017-05-31
- Modified: 2022-10-09
- Upstream path: rules/windows/builtin/security/win_security_alert_ruler.yml

## Log source

```yaml
product: windows
service: security
```

## Detection logic

```yaml
selection1:
  EventID: 4776
  Workstation: RULER
selection2:
  EventID:
  - 4624
  - 4625
  WorkstationName: RULER
condition: (1 of selection*)
```

## False positives

- Go utilities that use staaldraad awesome NTLM library

## References

- https://github.com/sensepost/ruler
- https://github.com/sensepost/ruler/issues/47
- https://github.com/staaldraad/go-ntlm/blob/cd032d41aa8ce5751c07cb7945400c0f5c81e2eb/ntlm/ntlmv1.go#L427
- https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4776
- https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624

## ATT&CK and Sigma tags

- attack.discovery
- attack.execution
- attack.collection
- attack.lateral-movement
- attack.t1087
- attack.t1114
- attack.t1059
- attack.t1550.002
