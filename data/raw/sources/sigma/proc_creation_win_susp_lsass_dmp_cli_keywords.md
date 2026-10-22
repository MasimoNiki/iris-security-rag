---
title: LSASS Dump Keyword In CommandLine
source_type: sigma_rule
external_id: ffa6861c-4461-4f59-8a41-578c39f3f23e
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_susp_lsass_dmp_cli_keywords.yml
source_revision: 2023-08-29@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.credential-access
- attack.t1003.001
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_susp_lsass_dmp_cli_keywords.yml
status: test
level: high
author: E.M. Anhaus, Tony Lambert, oscd.community, Nasreddine Bencherchali (Nextron
  Systems)
date: '2019-10-24'
modified: '2023-08-29'
related:
- id: a5a2d357-1ab8-4675-a967-ef9990a59391
  type: derived
logsource:
  category: process_creation
  product: windows
---

# LSASS Dump Keyword In CommandLine

## Summary

Detects the presence of the keywords "lsass" and ".dmp" in the commandline, which could indicate a potential attempt to dump or create a dump of the lsass process.

## Rule metadata

- Rule ID: ffa6861c-4461-4f59-8a41-578c39f3f23e
- Status: test
- Level: high
- Author: E.M. Anhaus, Tony Lambert, oscd.community, Nasreddine Bencherchali (Nextron Systems)
- Created: 2019-10-24
- Modified: 2023-08-29
- Upstream path: rules/windows/process_creation/proc_creation_win_susp_lsass_dmp_cli_keywords.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
- CommandLine|contains:
  - lsass.dmp
  - lsass.zip
  - lsass.rar
  - Andrew.dmp
  - Coredump.dmp
  - NotLSASS.zip
  - lsass_2
  - lsassdump
  - lsassdmp
- CommandLine|contains|all:
  - lsass
  - .dmp
- CommandLine|contains|all:
  - SQLDmpr
  - .mdmp
- CommandLine|contains|all:
  - nanodump
  - .dmp
condition: selection
```

## False positives

- Unlikely

## References

- https://github.com/Hackndo/lsassy
- https://medium.com/@markmotig/some-ways-to-dump-lsass-exe-c4a75fdc49bf
- https://github.com/elastic/detection-rules/blob/c76a39796972ecde44cb1da6df47f1b6562c9770/rules/windows/credential_access_lsass_memdump_file_created.toml
- https://www.whiteoaksecurity.com/blog/attacks-defenses-dumping-lsass-no-mimikatz/
- https://github.com/helpsystems/nanodump
- https://github.com/CCob/MirrorDump

## ATT&CK and Sigma tags

- attack.credential-access
- attack.t1003.001
