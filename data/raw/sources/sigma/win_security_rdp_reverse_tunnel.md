---
title: RDP over Reverse SSH Tunnel WFP
source_type: sigma_rule
external_id: 5bed80b6-b3e8-428e-a3ae-d3c757589e41
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/security/win_security_rdp_reverse_tunnel.yml
source_revision: 2022-09-02@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.command-and-control
- attack.lateral-movement
- attack.t1090.001
- attack.t1090.002
- attack.t1021.001
- car.2013-07-002
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/security/win_security_rdp_reverse_tunnel.yml
status: test
level: high
author: Samir Bousseaden
date: '2019-02-16'
modified: '2022-09-02'
related: []
logsource:
  product: windows
  service: security
---

# RDP over Reverse SSH Tunnel WFP

## Summary

Detects svchost hosting RDP termsvcs communicating with the loopback address

## Rule metadata

- Rule ID: 5bed80b6-b3e8-428e-a3ae-d3c757589e41
- Status: test
- Level: high
- Author: Samir Bousseaden
- Created: 2019-02-16
- Modified: 2022-09-02
- Upstream path: rules/windows/builtin/security/win_security_rdp_reverse_tunnel.yml

## Log source

```yaml
product: windows
service: security
```

## Detection logic

```yaml
selection:
  EventID: 5156
sourceRDP:
  SourcePort: 3389
  DestAddress:
  - 127.*
  - ::1
destinationRDP:
  DestPort: 3389
  SourceAddress:
  - 127.*
  - ::1
filter_app_container:
  FilterOrigin: AppContainer Loopback
filter_thor:
  Application|endswith:
  - \thor.exe
  - \thor64.exe
condition: selection and ( sourceRDP or destinationRDP ) and not 1 of filter*
```

## False positives

- Programs that connect locally to the RDP port

## References

- https://twitter.com/SBousseaden/status/1096148422984384514
- https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES/blob/44fbe85f72ee91582876b49678f9a26292a155fb/Command%20and%20Control/DE_RDP_Tunnel_5156.evtx

## ATT&CK and Sigma tags

- attack.command-and-control
- attack.lateral-movement
- attack.t1090.001
- attack.t1090.002
- attack.t1021.001
- car.2013-07-002
