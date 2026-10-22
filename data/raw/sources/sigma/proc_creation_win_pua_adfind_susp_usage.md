---
title: PUA - AdFind Suspicious Execution
source_type: sigma_rule
external_id: 9a132afa-654e-11eb-ae93-0242ac130002
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_pua_adfind_susp_usage.yml
source_revision: 2025-10-24@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.discovery
- attack.t1018
- attack.t1087.002
- attack.t1482
- attack.t1069.002
- stp.1u
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_pua_adfind_susp_usage.yml
status: test
level: high
author: Janantha Marasinghe (https://github.com/blueteam0ps), FPT.EagleEye Team, omkar72,
  oscd.community
date: '2021-02-02'
modified: '2025-10-24'
related:
- id: 455b9d50-15a1-4b99-853f-8d37655a4c1b
  type: similar
- id: 75df3b17-8bcc-4565-b89b-c9898acef911
  type: obsolete
logsource:
  category: process_creation
  product: windows
---

# PUA - AdFind Suspicious Execution

## Summary

Detects AdFind execution with common flags seen used during attacks

## Rule metadata

- Rule ID: 9a132afa-654e-11eb-ae93-0242ac130002
- Status: test
- Level: high
- Author: Janantha Marasinghe (https://github.com/blueteam0ps), FPT.EagleEye Team, omkar72, oscd.community
- Created: 2021-02-02
- Modified: 2025-10-24
- Upstream path: rules/windows/process_creation/proc_creation_win_pua_adfind_susp_usage.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  CommandLine|contains:
  - domainlist
  - trustdmp
  - dcmodes
  - adinfo
  - -sc dclist
  - computer_pwdnotreqd
  - objectcategory=
  - -subnets -f
  - name="Domain Admins"
  - '-sc u:'
  - domainncs
  - dompol
  - ' oudmp '
  - subnetdmp
  - gpodmp
  - fspdmp
  - users_noexpire
  - computers_active
  - computers_pwdnotreqd
condition: selection
```

## False positives

- Legitimate admin activity

## References

- https://www.joeware.net/freetools/tools/adfind/
- https://thedfirreport.com/2020/05/08/adfind-recon/
- https://thedfirreport.com/2021/01/11/trickbot-still-alive-and-well/
- https://www.microsoft.com/security/blog/2021/01/20/deep-dive-into-the-solorigate-second-stage-activation-from-sunburst-to-teardrop-and-raindrop/
- https://social.technet.microsoft.com/wiki/contents/articles/7535.adfind-command-examples.aspx
- https://github.com/center-for-threat-informed-defense/adversary_emulation_library/blob/bf62ece1c679b07b5fb49c4bae947fe24c81811f/fin6/Emulation_Plan/Phase1.md
- https://github.com/redcanaryco/atomic-red-team/blob/0f229c0e42bfe7ca736a14023836d65baa941ed2/atomics/T1087.002/T1087.002.md#atomic-test-7---adfind---enumerate-active-directory-user-objects

## ATT&CK and Sigma tags

- attack.discovery
- attack.t1018
- attack.t1087.002
- attack.t1482
- attack.t1069.002
- stp.1u
