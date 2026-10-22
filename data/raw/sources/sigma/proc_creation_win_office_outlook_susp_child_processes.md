---
title: Suspicious Outlook Child Process
source_type: sigma_rule
external_id: 208748f7-881d-47ac-a29c-07ea84bf691d
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_office_outlook_susp_child_processes.yml
source_revision: 2023-02-04@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.execution
- attack.t1204.002
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_office_outlook_susp_child_processes.yml
status: test
level: high
author: Michael Haag, Florian Roth (Nextron Systems), Markus Neis, Elastic, FPT.EagleEye
  Team
date: '2022-02-28'
modified: '2023-02-04'
related:
- id: 438025f9-5856-4663-83f7-52f878a70a50
  type: derived
- id: e212d415-0e93-435f-9e1a-f29005bb4723
  type: derived
logsource:
  category: process_creation
  product: windows
---

# Suspicious Outlook Child Process

## Summary

Detects a suspicious process spawning from an Outlook process.

## Rule metadata

- Rule ID: 208748f7-881d-47ac-a29c-07ea84bf691d
- Status: test
- Level: high
- Author: Michael Haag, Florian Roth (Nextron Systems), Markus Neis, Elastic, FPT.EagleEye Team
- Created: 2022-02-28
- Modified: 2023-02-04
- Upstream path: rules/windows/process_creation/proc_creation_win_office_outlook_susp_child_processes.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  ParentImage|endswith: \OUTLOOK.EXE
  Image|endswith:
  - \AppVLP.exe
  - \bash.exe
  - \cmd.exe
  - \cscript.exe
  - \forfiles.exe
  - \hh.exe
  - \mftrace.exe
  - \msbuild.exe
  - \msdt.exe
  - \mshta.exe
  - \msiexec.exe
  - \powershell.exe
  - \pwsh.exe
  - \regsvr32.exe
  - \schtasks.exe
  - \scrcons.exe
  - \scriptrunner.exe
  - \sh.exe
  - \svchost.exe
  - \wmic.exe
  - \wscript.exe
condition: selection
```

## False positives

- Unknown

## References

- https://www.hybrid-analysis.com/sample/465aabe132ccb949e75b8ab9c5bda36d80cf2fd503d52b8bad54e295f28bbc21?environmentId=100
- https://mgreen27.github.io/posts/2018/04/02/DownloadCradle.html

## ATT&CK and Sigma tags

- attack.execution
- attack.t1204.002
