---
title: Network Communication Initiated To Portmap.IO Domain
source_type: sigma_rule
external_id: 07837ab9-60e1-481f-a74d-c31fb496a94c
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/network_connection/net_connection_win_domain_portmap.yml
source_revision: 2024-05-31@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.t1041
- attack.command-and-control
- attack.t1090.002
- attack.exfiltration
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/network_connection/net_connection_win_domain_portmap.yml
status: test
level: medium
author: Florian Roth (Nextron Systems)
date: '2024-05-31'
modified: null
related: []
logsource:
  category: network_connection
  product: windows
---

# Network Communication Initiated To Portmap.IO Domain

## Summary

Detects an executable accessing the portmap.io domain, which could be a sign of forbidden C2 traffic or data exfiltration by malicious actors

## Rule metadata

- Rule ID: 07837ab9-60e1-481f-a74d-c31fb496a94c
- Status: test
- Level: medium
- Author: Florian Roth (Nextron Systems)
- Created: 2024-05-31
- Modified: Not specified
- Upstream path: rules/windows/network_connection/net_connection_win_domain_portmap.yml

## Log source

```yaml
category: network_connection
product: windows
```

## Detection logic

```yaml
selection:
  Initiated: 'true'
  DestinationHostname|endswith: .portmap.io
condition: selection
```

## False positives

- Legitimate use of portmap.io domains

## References

- https://portmap.io/
- https://github.com/rapid7/metasploit-framework/issues/11337
- https://pro.twitter.com/JaromirHorejsi/status/1795001037746761892/photo/2

## ATT&CK and Sigma tags

- attack.t1041
- attack.command-and-control
- attack.t1090.002
- attack.exfiltration
