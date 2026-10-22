---
title: Suspicious Double Extension File Execution
source_type: sigma_rule
external_id: 1cdd9a09-06c9-4769-99ff-626e2b3991b8
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_susp_double_extension.yml
source_revision: 2025-05-30@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.initial-access
- attack.t1566.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_susp_double_extension.yml
status: stable
level: high
author: Florian Roth (Nextron Systems), @blu3_team (idea), Nasreddine Bencherchali
  (Nextron Systems)
date: '2019-06-26'
modified: '2025-05-30'
related:
- id: 5e6a80c8-2d45-4633-9ef4-fa2671a39c5c
  type: similar
logsource:
  category: process_creation
  product: windows
---

# Suspicious Double Extension File Execution

## Summary

Detects suspicious use of an .exe extension after a non-executable file extension like .pdf.exe, a set of spaces or underlines to cloak the executable file in spear phishing campaigns

## Rule metadata

- Rule ID: 1cdd9a09-06c9-4769-99ff-626e2b3991b8
- Status: stable
- Level: high
- Author: Florian Roth (Nextron Systems), @blu3_team (idea), Nasreddine Bencherchali (Nextron Systems)
- Created: 2019-06-26
- Modified: 2025-05-30
- Upstream path: rules/windows/process_creation/proc_creation_win_susp_double_extension.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  Image|endswith:
  - '      .exe'
  - ______.exe
  - .doc.exe
  - .doc.js
  - .docx.exe
  - .docx.js
  - .gif.exe
  - .jpeg.exe
  - .jpg.exe
  - .mkv.exe
  - .mov.exe
  - .mp3.exe
  - .mp4.exe
  - .pdf.exe
  - .pdf.js
  - .png.exe
  - .ppt.exe
  - .ppt.js
  - .pptx.exe
  - .pptx.js
  - .rtf.exe
  - .rtf.js
  - .svg.exe
  - .txt.exe
  - .txt.js
  - .xls.exe
  - .xls.js
  - .xlsx.exe
  - .xlsx.js
  - ⠀⠀⠀⠀⠀⠀.exe
  CommandLine|contains:
  - '      .exe'
  - ______.exe
  - .doc.exe
  - .doc.js
  - .docx.exe
  - .docx.js
  - .gif.exe
  - .jpeg.exe
  - .jpg.exe
  - .mkv.exe
  - .mov.exe
  - .mp3.exe
  - .mp4.exe
  - .pdf.exe
  - .pdf.js
  - .png.exe
  - .ppt.exe
  - .ppt.js
  - .pptx.exe
  - .pptx.js
  - .rtf.exe
  - .rtf.js
  - .svg.exe
  - .txt.exe
  - .txt.js
  - .xls.exe
  - .xls.js
  - .xlsx.exe
  - .xlsx.js
  - ⠀⠀⠀⠀⠀⠀.exe
condition: selection
```

## False positives

- Unknown

## References

- https://blu3-team.blogspot.com/2019/06/misleading-extensions-xlsexe-docexe.html
- https://twitter.com/blackorbird/status/1140519090961825792
- https://cloud.google.com/blog/topics/threat-intelligence/cybercriminals-weaponize-fake-ai-websites

## ATT&CK and Sigma tags

- attack.initial-access
- attack.t1566.001
