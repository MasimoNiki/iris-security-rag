---
title: Potential Powershell ReverseShell Connection
source_type: sigma_rule
external_id: edc2f8ae-2412-4dfd-b9d5-0c57727e70be
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_powershell_reverse_shell_connection.yml
source_revision: 2023-04-05@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.execution
- attack.t1059.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_powershell_reverse_shell_connection.yml
status: stable
level: high
author: FPT.EagleEye, wagga, Nasreddine Bencherchali (Nextron Systems)
date: '2021-03-03'
modified: '2023-04-05'
related: []
logsource:
  category: process_creation
  product: windows
---

# Potential Powershell ReverseShell Connection

## Summary

Detects usage of the "TcpClient" class. Which can be abused to establish remote connections and reverse-shells. As seen used by the Nishang "Invoke-PowerShellTcpOneLine" reverse shell and other.

## Rule metadata

- Rule ID: edc2f8ae-2412-4dfd-b9d5-0c57727e70be
- Status: stable
- Level: high
- Author: FPT.EagleEye, wagga, Nasreddine Bencherchali (Nextron Systems)
- Created: 2021-03-03
- Modified: 2023-04-05
- Upstream path: rules/windows/process_creation/proc_creation_win_powershell_reverse_shell_connection.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection_img:
- OriginalFileName:
  - PowerShell.EXE
  - pwsh.dll
- Image|endswith:
  - \powershell.exe
  - \pwsh.exe
selection_cli:
  CommandLine|contains|all:
  - ' Net.Sockets.TCPClient'
  - .GetStream(
  - .Write(
condition: all of selection_*
```

## False positives

- In rare administrative cases, this function might be used to check network connectivity

## References

- https://www.volexity.com/blog/2021/03/02/active-exploitation-of-microsoft-exchange-zero-day-vulnerabilities/
- https://www.microsoft.com/security/blog/2021/03/02/hafnium-targeting-exchange-servers/
- https://github.com/samratashok/nishang/blob/414ee1104526d7057f9adaeee196d91ae447283e/Shells/Invoke-PowerShellTcpOneLine.ps1

## ATT&CK and Sigma tags

- attack.execution
- attack.t1059.001
