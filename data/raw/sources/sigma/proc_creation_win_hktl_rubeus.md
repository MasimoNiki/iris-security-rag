---
title: HackTool - Rubeus Execution
source_type: sigma_rule
external_id: 7ec2c172-dceb-4c10-92c9-87c1881b7e18
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_hktl_rubeus.yml
source_revision: 2023-04-20@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.t1003
- attack.t1558.003
- attack.lateral-movement
- attack.t1550.003
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_hktl_rubeus.yml
status: stable
level: critical
author: Florian Roth (Nextron Systems)
date: '2018-12-19'
modified: '2023-04-20'
related:
- id: 7ec2c172-dceb-4c10-92c9-87c1881b7e18
  type: similar
logsource:
  category: process_creation
  product: windows
---

# HackTool - Rubeus Execution

## Summary

Detects the execution of the hacktool Rubeus via PE information of command line parameters

## Rule metadata

- Rule ID: 7ec2c172-dceb-4c10-92c9-87c1881b7e18
- Status: stable
- Level: critical
- Author: Florian Roth (Nextron Systems)
- Created: 2018-12-19
- Modified: 2023-04-20
- Upstream path: rules/windows/process_creation/proc_creation_win_hktl_rubeus.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
- Image|endswith: \Rubeus.exe
- OriginalFileName: Rubeus.exe
- Description: Rubeus
- CommandLine|contains:
  - 'asreproast '
  - 'dump /service:krbtgt '
  - dump /luid:0x
  - 'kerberoast '
  - 'createnetonly /program:'
  - 'ptt /ticket:'
  - '/impersonateuser:'
  - 'renew /ticket:'
  - 'asktgt /user:'
  - 'harvest /interval:'
  - 's4u /user:'
  - 's4u /ticket:'
  - 'hash /password:'
  - 'golden /aes256:'
  - 'silver /user:'
condition: selection
```

## False positives

- Unlikely

## References

- https://blog.harmj0y.net/redteaming/from-kekeo-to-rubeus
- https://m0chan.github.io/2019/07/31/How-To-Attack-Kerberos-101.html
- https://github.com/GhostPack/Rubeus

## ATT&CK and Sigma tags

- attack.credential-access
- attack.t1003
- attack.t1558.003
- attack.lateral-movement
- attack.t1550.003
