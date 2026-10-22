---
title: "AADInternals PowerShell Cmdlets Execution - ProccessCreation"
source_type: "sigma_rule"
language: "en"
domain: "detection_engineering"
tags: ['sigma', 'attack.execution', 'attack.reconnaissance', 'attack.discovery', 'attack.credential-access', 'attack.impact']
---

# AADInternals PowerShell Cmdlets Execution - ProccessCreation

## Summary

Detects ADDInternals Cmdlet execution. A tool for administering Azure AD and Office 365. Which can be abused by threat actors to attack Azure AD or Office 365.

## Sigma metadata

- Rule ID: c86500e9-a645-4680-98d7-f882c70c1ea3
- Status: test
- Author: Austin Songer (@austinsonger), Nasreddine Bencherchali (Nextron Systems), Swachchhanda Shrawan Poudel (Nextron Systems)
- Date: 2022-12-23
- Modified: 2025-02-06
- Level: high
- Source file: data/external/sigma/proc_creation_win_powershell_aadinternals_cmdlets_execution.yml

## Logsource

- product: windows
- category: process_creation

## Detection logic

- selection_img: [{'Image|endswith': ['\\powershell.exe', '\\powershell_ise.exe', '\\pwsh.exe']}, {'OriginalFileName': ['PowerShell.Exe', 'pwsh.dll']}]
- selection_cli: {'CommandLine|contains': ['Add-AADInt', 'ConvertTo-AADInt', 'Disable-AADInt', 'Enable-AADInt', 'Export-AADInt', 'Find-AADInt', 'Get-AADInt', 'Grant-AADInt', 'Initialize-AADInt', 'Install-AADInt', 'Invoke-AADInt', 'Join-AADInt', 'New-AADInt', 'Open-AADInt', 'Read-AADInt', 'Register-AADInt', 'Remove-AADInt', 'Reset-AADInt', 'Resolve-AADInt', 'Restore-AADInt', 'Save-AADInt', 'Search-AADInt', 'Send-AADInt', 'Set-AADInt', 'Start-AADInt', 'Unprotect-AADInt', 'Update-AADInt']}
- condition: all of selection_*

## False positives

- Legitimate use of the library for administrative activity

## References

- https://o365blog.com/aadinternals/
- https://github.com/Gerenios/AADInternals

## Tags

- attack.execution
- attack.reconnaissance
- attack.discovery
- attack.credential-access
- attack.impact
