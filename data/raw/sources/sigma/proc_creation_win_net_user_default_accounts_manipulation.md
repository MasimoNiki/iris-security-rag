---
title: Suspicious Manipulation Of Default Accounts Via Net.EXE
source_type: sigma_rule
external_id: 5b768e71-86f2-4879-b448-81061cbae951
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_net_user_default_accounts_manipulation.yml
source_revision: 2023-02-21@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.collection
- attack.t1560.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_net_user_default_accounts_manipulation.yml
status: test
level: high
author: Nasreddine Bencherchali (Nextron Systems)
date: '2022-09-01'
modified: '2023-02-21'
related: []
logsource:
  category: process_creation
  product: windows
---

# Suspicious Manipulation Of Default Accounts Via Net.EXE

## Summary

Detects suspicious manipulations of default accounts such as 'administrator' and 'guest'. For example 'enable' or 'disable' accounts or change the password...etc

## Rule metadata

- Rule ID: 5b768e71-86f2-4879-b448-81061cbae951
- Status: test
- Level: high
- Author: Nasreddine Bencherchali (Nextron Systems)
- Created: 2022-09-01
- Modified: 2023-02-21
- Upstream path: rules/windows/process_creation/proc_creation_win_net_user_default_accounts_manipulation.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection_img:
- Image|endswith:
  - \net.exe
  - \net1.exe
- OriginalFileName:
  - net.exe
  - net1.exe
selection_user_option:
  CommandLine|contains: ' user '
selection_username:
  CommandLine|contains:
  - ' Järjestelmänvalvoja '
  - ' Rendszergazda '
  - ' Администратор '
  - ' Administrateur '
  - ' Administrador '
  - ' Administratör '
  - ' Administrator '
  - ' guest '
  - ' DefaultAccount '
  - ' "Järjestelmänvalvoja" '
  - ' "Rendszergazda" '
  - ' "Администратор" '
  - ' "Administrateur" '
  - ' "Administrador" '
  - ' "Administratör" '
  - ' "Administrator" '
  - ' "guest" '
  - ' "DefaultAccount" '
  - ' ''Järjestelmänvalvoja'' '
  - ' ''Rendszergazda'' '
  - ' ''Администратор'' '
  - ' ''Administrateur'' '
  - ' ''Administrador'' '
  - ' ''Administratör'' '
  - ' ''Administrator'' '
  - ' ''guest'' '
  - ' ''DefaultAccount'' '
filter:
  CommandLine|contains|all:
  - guest
  - /active no
condition: all of selection_* and not filter
```

## False positives

- Some false positives could occur with the admin or guest account. It depends on the scripts being used by the admins in your env. If you experience a lot of FP you could reduce the level to medium

## References

- https://www.trellix.com/en-sg/about/newsroom/stories/threat-labs/lockergoga-ransomware-family-used-in-targeted-attacks.html
- https://redacted.com/blog/bianlian-ransomware-gang-gives-it-a-go/
- https://www.microsoft.com/security/blog/2022/09/07/profiling-dev-0270-phosphorus-ransomware-operations/

## ATT&CK and Sigma tags

- attack.collection
- attack.t1560.001
