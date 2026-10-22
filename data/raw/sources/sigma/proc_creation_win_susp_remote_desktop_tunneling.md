---
title: Potential Remote Desktop Tunneling
source_type: sigma_rule
external_id: 8a3038e8-9c9d-46f8-b184-66234a160f6f
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_susp_remote_desktop_tunneling.yml
source_revision: 2022-09-27@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.lateral-movement
- attack.t1021
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_susp_remote_desktop_tunneling.yml
status: test
level: medium
author: Tim Rauch, Elastic (idea)
date: '2022-09-27'
modified: null
related: []
logsource:
  category: process_creation
  product: windows
---

# Potential Remote Desktop Tunneling

## Summary

Detects potential use of an SSH utility to establish RDP over a reverse SSH Tunnel. This can be used by attackers to enable routing of network packets that would otherwise not reach their intended destination.

## Rule metadata

- Rule ID: 8a3038e8-9c9d-46f8-b184-66234a160f6f
- Status: test
- Level: medium
- Author: Tim Rauch, Elastic (idea)
- Created: 2022-09-27
- Modified: Not specified
- Upstream path: rules/windows/process_creation/proc_creation_win_susp_remote_desktop_tunneling.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  CommandLine|contains: :3389
selection_opt:
  CommandLine|contains:
  - ' -L '
  - ' -P '
  - ' -R '
  - ' -pw '
  - ' -ssh '
condition: all of selection*
```

## False positives

- Unknown

## References

- https://www.elastic.co/guide/en/security/current/potential-remote-desktop-tunneling-detected.html

## ATT&CK and Sigma tags

- attack.lateral-movement
- attack.t1021
