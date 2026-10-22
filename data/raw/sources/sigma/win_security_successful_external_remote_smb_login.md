---
title: External Remote SMB Logon from Public IP
source_type: sigma_rule
external_id: 78d5cab4-557e-454f-9fb9-a222bd0d5edc
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/security/account_management/win_security_successful_external_remote_smb_login.yml
source_revision: 2024-03-11@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.privilege-escalation
- attack.persistence
- attack.initial-access
- attack.credential-access
- attack.stealth
- attack.t1133
- attack.t1078
- attack.t1110
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/security/account_management/win_security_successful_external_remote_smb_login.yml
status: test
level: high
author: Micah Babinski (@micahbabinski), Zach Mathis (@yamatosecurity)
date: '2023-01-19'
modified: '2024-03-11'
related:
- id: 259a9cdf-c4dd-4fa2-b243-2269e5ab18a2
  type: derived
logsource:
  product: windows
  service: security
---

# External Remote SMB Logon from Public IP

## Summary

Detects successful logon from public IP address via SMB. This can indicate a publicly-exposed SMB port.

## Rule metadata

- Rule ID: 78d5cab4-557e-454f-9fb9-a222bd0d5edc
- Status: test
- Level: high
- Author: Micah Babinski (@micahbabinski), Zach Mathis (@yamatosecurity)
- Created: 2023-01-19
- Modified: 2024-03-11
- Upstream path: rules/windows/builtin/security/account_management/win_security_successful_external_remote_smb_login.yml

## Log source

```yaml
product: windows
service: security
```

## Detection logic

```yaml
selection:
  EventID: 4624
  LogonType: 3
filter_main_local_ranges:
  IpAddress|cidr:
  - ::1/128
  - 10.0.0.0/8
  - 127.0.0.0/8
  - 172.16.0.0/12
  - 192.168.0.0/16
  - 169.254.0.0/16
  - fc00::/7
  - fe80::/10
filter_main_empty:
  IpAddress: '-'
condition: selection and not 1 of filter_main_*
```

## False positives

- Legitimate or intentional inbound connections from public IP addresses on the SMB port.

## References

- https://www.inversecos.com/2020/04/successful-4624-anonymous-logons-to.html
- https://twitter.com/Purp1eW0lf/status/1616144561965002752

## ATT&CK and Sigma tags

- attack.privilege-escalation
- attack.persistence
- attack.initial-access
- attack.credential-access
- attack.stealth
- attack.t1133
- attack.t1078
- attack.t1110
