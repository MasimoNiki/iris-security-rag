---
title: RDP Login from Localhost
source_type: sigma_rule
external_id: 51e33403-2a37-4d66-a574-1fda1782cc31
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/security/account_management/win_security_rdp_localhost_login.yml
source_revision: 2022-10-09@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.lateral-movement
- car.2013-07-002
- attack.t1021.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/security/account_management/win_security_rdp_localhost_login.yml
status: test
level: high
author: Thomas Patzke
date: '2019-01-28'
modified: '2022-10-09'
related: []
logsource:
  product: windows
  service: security
---

# RDP Login from Localhost

## Summary

RDP login with localhost source address may be a tunnelled login

## Rule metadata

- Rule ID: 51e33403-2a37-4d66-a574-1fda1782cc31
- Status: test
- Level: high
- Author: Thomas Patzke
- Created: 2019-01-28
- Modified: 2022-10-09
- Upstream path: rules/windows/builtin/security/account_management/win_security_rdp_localhost_login.yml

## Log source

```yaml
product: windows
service: security
```

## Detection logic

```yaml
selection:
  EventID: 4624
  LogonType: 10
  IpAddress:
  - ::1
  - 127.0.0.1
condition: selection
```

## False positives

- Unknown

## References

- https://www.fireeye.com/blog/threat-research/2019/01/bypassing-network-restrictions-through-rdp-tunneling.html

## ATT&CK and Sigma tags

- attack.lateral-movement
- car.2013-07-002
- attack.t1021.001
