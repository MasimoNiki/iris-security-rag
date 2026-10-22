---
title: Suspicious Scheduled Task Creation
source_type: sigma_rule
external_id: 3a734d25-df5c-4b99-8034-af1ddb5883a4
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/builtin/security/win_security_susp_scheduled_task_creation.yml
source_revision: 2022-12-07@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.execution
- attack.privilege-escalation
- attack.persistence
- attack.t1053.005
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/builtin/security/win_security_susp_scheduled_task_creation.yml
status: test
level: high
author: Nasreddine Bencherchali (Nextron Systems)
date: '2022-12-05'
modified: '2022-12-07'
related: []
logsource:
  product: windows
  service: security
  definition: The Advanced Audit Policy setting Object Access > Audit Other Object
    Access Events has to be configured to allow this detection. We also recommend
    extracting the Command field from the embedded XML in the event data.
---

# Suspicious Scheduled Task Creation

## Summary

Detects suspicious scheduled task creation events. Based on attributes such as paths, commands line flags, etc.

## Rule metadata

- Rule ID: 3a734d25-df5c-4b99-8034-af1ddb5883a4
- Status: test
- Level: high
- Author: Nasreddine Bencherchali (Nextron Systems)
- Created: 2022-12-05
- Modified: 2022-12-07
- Upstream path: rules/windows/builtin/security/win_security_susp_scheduled_task_creation.yml

## Log source

```yaml
product: windows
service: security
definition: The Advanced Audit Policy setting Object Access > Audit Other Object Access
  Events has to be configured to allow this detection. We also recommend extracting
  the Command field from the embedded XML in the event data.
```

## Detection logic

```yaml
selection_eid:
  EventID: 4698
selection_paths:
  TaskContent|contains:
  - \AppData\Local\Temp\
  - \AppData\Roaming\
  - \Users\Public\
  - \WINDOWS\Temp\
  - C:\Temp\
  - \Desktop\
  - \Downloads\
  - \Temporary Internet
  - C:\ProgramData\
  - C:\Perflogs\
selection_commands:
  TaskContent|contains:
  - regsvr32
  - rundll32
  - cmd.exe</Command>
  - cmd</Command>
  - '<Arguments>/c '
  - '<Arguments>/k '
  - '<Arguments>/r '
  - powershell
  - pwsh
  - mshta
  - wscript
  - cscript
  - certutil
  - bitsadmin
  - bash.exe
  - 'bash '
  - scrcons
  - 'wmic '
  - wmic.exe
  - forfiles
  - scriptrunner
  - hh.exe
condition: all of selection_*
```

## False positives

- Unknown

## References

- https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4698

## ATT&CK and Sigma tags

- attack.execution
- attack.privilege-escalation
- attack.persistence
- attack.t1053.005
