---
title: "PowerShell Web Access Feature Enabled Via DISM"
source_type: "sigma_rule"
language: "en"
domain: "detection_engineering"
tags: ['sigma', 'attack.privilege-escalation', 'attack.persistence', 'attack.t1548.002']
---

# PowerShell Web Access Feature Enabled Via DISM

## Summary

Detects the use of DISM to enable the PowerShell Web Access feature, which could be used for remote access and potential abuse

## Sigma metadata

- Rule ID: 7e8f2d3b-9c1a-4f67-b9e8-8d9006e0e51f
- Status: test
- Author: Michael Haag
- Date: 2024-09-03
- Modified: N/A
- Level: high
- Source file: data/external/sigma/proc_creation_win_dism_enable_powershell_web_access_feature.yml

## Logsource

- category: process_creation
- product: windows

## Detection logic

- selection_img: [{'Image|endswith': '\\dism.exe'}, {'OriginalFileName': 'DISM.EXE'}]
- selection_cli: {'CommandLine|contains|all': ['WindowsPowerShellWebAccess', '/online', '/enable-feature']}
- condition: all of selection_*

## False positives

- Legitimate PowerShell Web Access installations by administrators

## References

- https://docs.microsoft.com/en-us/powershell/module/dism/enable-windowsoptionalfeature
- https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-241a
- https://gist.github.com/MHaggis/7e67b659af9148fa593cf2402edebb41

## Tags

- attack.privilege-escalation
- attack.persistence
- attack.t1548.002
