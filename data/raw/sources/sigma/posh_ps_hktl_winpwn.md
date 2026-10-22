---
title: HackTool - WinPwn Execution - ScriptBlock
source_type: sigma_rule
external_id: 851fd622-b675-4d26-b803-14bc7baa517a
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/powershell/powershell_script/posh_ps_hktl_winpwn.yml
source_revision: 2023-12-04@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.discovery
- attack.execution
- attack.privilege-escalation
- attack.t1046
- attack.t1082
- attack.t1106
- attack.t1518
- attack.t1548.002
- attack.t1552.001
- attack.t1555
- attack.t1555.003
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/powershell/powershell_script/posh_ps_hktl_winpwn.yml
status: test
level: high
author: Swachchhanda Shrawan Poudel
date: '2023-12-04'
modified: null
related:
- id: d557dc06-62e8-4468-a8e8-7984124908ce
  type: similar
logsource:
  category: ps_script
  product: windows
  definition: 'Requirements: Script Block Logging must be enabled'
---

# HackTool - WinPwn Execution - ScriptBlock

## Summary

Detects scriptblock text keywords indicative of potential usge of the tool WinPwn. A tool for Windows and Active Directory reconnaissance and exploitation.

## Rule metadata

- Rule ID: 851fd622-b675-4d26-b803-14bc7baa517a
- Status: test
- Level: high
- Author: Swachchhanda Shrawan Poudel
- Created: 2023-12-04
- Modified: Not specified
- Upstream path: rules/windows/powershell/powershell_script/posh_ps_hktl_winpwn.yml

## Log source

```yaml
category: ps_script
product: windows
definition: 'Requirements: Script Block Logging must be enabled'
```

## Detection logic

```yaml
selection:
  ScriptBlockText|contains:
  - Offline_Winpwn
  - 'WinPwn '
  - WinPwn.exe
  - WinPwn.ps1
condition: selection
```

## False positives

- As the script block is a blob of text. False positive may occur with scripts that contain the keyword as a reference or simply use it for detection.

## References

- https://github.com/S3cur3Th1sSh1t/WinPwn
- https://www.publicnow.com/view/EB87DB49C654D9B63995FAD4C9DE3D3CC4F6C3ED?1671634841
- https://reconshell.com/winpwn-tool-for-internal-windows-pentesting-and-ad-security/
- https://github.com/redcanaryco/atomic-red-team/blob/4d6c4e8e23d465af7a2388620cfe3f8c76e16cf0/atomics/T1082/T1082.md
- https://grep.app/search?q=winpwn&filter[repo][0]=redcanaryco/atomic-red-team

## ATT&CK and Sigma tags

- attack.credential-access
- attack.discovery
- attack.execution
- attack.privilege-escalation
- attack.t1046
- attack.t1082
- attack.t1106
- attack.t1518
- attack.t1548.002
- attack.t1552.001
- attack.t1555
- attack.t1555.003
