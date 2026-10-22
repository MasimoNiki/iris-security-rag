---
title: "LSASS Process Reconnaissance Via Findstr.EXE"
source_type: "sigma_rule"
language: "en"
domain: "detection_engineering"
tags: ['sigma', 'attack.credential-access', 'attack.t1552.006']
---

# LSASS Process Reconnaissance Via Findstr.EXE

## Summary

Detects findstring commands that include the keyword lsass, which indicates recon actviity for the LSASS process PID

## Sigma metadata

- Rule ID: fe63010f-8823-4864-a96b-a7b4a0f7b929
- Status: test
- Author: Florian Roth (Nextron Systems)
- Date: 2022-08-12
- Modified: 2024-06-04
- Level: high
- Source file: data/external/sigma/proc_creation_win_findstr_lsass.yml

## Logsource

- category: process_creation
- product: windows

## Detection logic

- selection_findstr_img: [{'Image|endswith': ['\\find.exe', '\\findstr.exe']}, {'OriginalFileName': ['FIND.EXE', 'FINDSTR.EXE']}]
- selection_findstr_cli: {'CommandLine|contains': 'lsass'}
- selection_special: {'CommandLine|contains|windash': [' /i "lsass', ' /i lsass.exe', 'findstr "lsass', 'findstr lsass', 'findstr.exe "lsass', 'findstr.exe lsass']}
- condition: all of selection_findstr_* or selection_special

## False positives

- Unknown

## References

- https://blog.talosintelligence.com/2022/08/recent-cyber-attack.html?m=1

## Tags

- attack.credential-access
- attack.t1552.006
