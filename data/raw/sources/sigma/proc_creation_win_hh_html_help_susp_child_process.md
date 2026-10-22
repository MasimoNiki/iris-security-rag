---
title: HTML Help HH.EXE Suspicious Child Process
source_type: sigma_rule
external_id: 52cad028-0ff0-4854-8f67-d25dfcbc78b4
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_hh_html_help_susp_child_process.yml
source_revision: 2023-04-12@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.execution
- attack.initial-access
- attack.stealth
- attack.t1047
- attack.t1059.001
- attack.t1059.003
- attack.t1059.005
- attack.t1059.007
- attack.t1218
- attack.t1218.001
- attack.t1218.010
- attack.t1218.011
- attack.t1566
- attack.t1566.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_hh_html_help_susp_child_process.yml
status: test
level: high
author: Maxim Pavlunin, Nasreddine Bencherchali (Nextron Systems)
date: '2020-04-01'
modified: '2023-04-12'
related: []
logsource:
  category: process_creation
  product: windows
---

# HTML Help HH.EXE Suspicious Child Process

## Summary

Detects a suspicious child process of a Microsoft HTML Help (HH.exe)

## Rule metadata

- Rule ID: 52cad028-0ff0-4854-8f67-d25dfcbc78b4
- Status: test
- Level: high
- Author: Maxim Pavlunin, Nasreddine Bencherchali (Nextron Systems)
- Created: 2020-04-01
- Modified: 2023-04-12
- Upstream path: rules/windows/process_creation/proc_creation_win_hh_html_help_susp_child_process.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  ParentImage|endswith: \hh.exe
  Image|endswith:
  - \CertReq.exe
  - \CertUtil.exe
  - \cmd.exe
  - \cscript.exe
  - \installutil.exe
  - \MSbuild.exe
  - \MSHTA.EXE
  - \msiexec.exe
  - \powershell.exe
  - \pwsh.exe
  - \regsvr32.exe
  - \rundll32.exe
  - \schtasks.exe
  - \wmic.exe
  - \wscript.exe
condition: selection
```

## False positives

- Unknown

## References

- https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/chm-badness-delivers-a-banking-trojan/
- https://github.com/elastic/protections-artifacts/commit/746086721fd385d9f5c6647cada1788db4aea95f#diff-27939090904026cc396b0b629c8e4314acd6f5dac40a676edbc87f4567b47eb7
- https://www.ptsecurity.com/ww-en/analytics/pt-esc-threat-intelligence/higaisa-or-winnti-apt-41-backdoors-old-and-new/
- https://www.zscaler.com/blogs/security-research/unintentional-leak-glimpse-attack-vectors-apt37

## ATT&CK and Sigma tags

- attack.execution
- attack.initial-access
- attack.stealth
- attack.t1047
- attack.t1059.001
- attack.t1059.003
- attack.t1059.005
- attack.t1059.007
- attack.t1218
- attack.t1218.001
- attack.t1218.010
- attack.t1218.011
- attack.t1566
- attack.t1566.001
