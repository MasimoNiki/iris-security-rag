---
title: Suspicious Execution via macOS Script Editor
source_type: sigma_rule
external_id: 6e4dcdd1-e48b-42f7-b2d8-3b413fc58cb4
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/macos/process_creation/proc_creation_macos_susp_execution_macos_script_editor.yml
source_revision: 2022-12-28@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.defense-impairment
- attack.t1566
- attack.t1566.002
- attack.initial-access
- attack.t1059
- attack.t1059.002
- attack.t1204
- attack.t1204.001
- attack.execution
- attack.persistence
- attack.t1553
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/macos/process_creation/proc_creation_macos_susp_execution_macos_script_editor.yml
status: test
level: medium
author: Tim Rauch (rule), Elastic (idea)
date: '2022-10-21'
modified: '2022-12-28'
related: []
logsource:
  category: process_creation
  product: macos
---

# Suspicious Execution via macOS Script Editor

## Summary

Detects when the macOS Script Editor utility spawns an unusual child process.

## Rule metadata

- Rule ID: 6e4dcdd1-e48b-42f7-b2d8-3b413fc58cb4
- Status: test
- Level: medium
- Author: Tim Rauch (rule), Elastic (idea)
- Created: 2022-10-21
- Modified: 2022-12-28
- Upstream path: rules/macos/process_creation/proc_creation_macos_susp_execution_macos_script_editor.yml

## Log source

```yaml
category: process_creation
product: macos
```

## Detection logic

```yaml
selection_parent:
  ParentImage|endswith: /Script Editor
selection_img:
- Image|endswith:
  - /curl
  - /bash
  - /sh
  - /zsh
  - /dash
  - /fish
  - /osascript
  - /mktemp
  - /chmod
  - /php
  - /nohup
  - /openssl
  - /plutil
  - /PlistBuddy
  - /xattr
  - /sqlite
  - /funzip
  - /popen
- Image|contains:
  - python
  - perl
condition: all of selection_*
```

## False positives

- Unknown

## References

- https://github.com/elastic/protections-artifacts/commit/746086721fd385d9f5c6647cada1788db4aea95f#diff-7f541fbc4a4a28a92970e8bf53effea5bd934604429112c920affb457f5b2685
- https://wojciechregula.blog/post/macos-red-teaming-initial-access-via-applescript-url/

## ATT&CK and Sigma tags

- attack.defense-impairment
- attack.t1566
- attack.t1566.002
- attack.initial-access
- attack.t1059
- attack.t1059.002
- attack.t1204
- attack.t1204.001
- attack.execution
- attack.persistence
- attack.t1553
