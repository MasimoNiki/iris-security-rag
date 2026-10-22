---
title: Suspicious Execution From Outlook Temporary Folder
source_type: sigma_rule
external_id: a018fdc3-46a3-44e5-9afb-2cd4af1d4b39
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_office_outlook_execution_from_temp.yml
source_revision: 2022-10-09@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.initial-access
- attack.t1566.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_office_outlook_execution_from_temp.yml
status: test
level: high
author: Florian Roth (Nextron Systems)
date: '2019-10-01'
modified: '2022-10-09'
related: []
logsource:
  category: process_creation
  product: windows
---

# Suspicious Execution From Outlook Temporary Folder

## Summary

Detects a suspicious program execution in Outlook temp folder

## Rule metadata

- Rule ID: a018fdc3-46a3-44e5-9afb-2cd4af1d4b39
- Status: test
- Level: high
- Author: Florian Roth (Nextron Systems)
- Created: 2019-10-01
- Modified: 2022-10-09
- Upstream path: rules/windows/process_creation/proc_creation_win_office_outlook_execution_from_temp.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  Image|contains: \Temporary Internet Files\Content.Outlook\
condition: selection
```

## False positives

- Unknown

## References

- Internal Research

## ATT&CK and Sigma tags

- attack.initial-access
- attack.t1566.001
