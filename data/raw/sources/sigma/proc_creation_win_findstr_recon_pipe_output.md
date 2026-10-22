---
title: Recon Command Output Piped To Findstr.EXE
source_type: sigma_rule
external_id: ccb5742c-c248-4982-8c5c-5571b9275ad3
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/windows/process_creation/proc_creation_win_findstr_recon_pipe_output.yml
source_revision: 2025-10-08@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.discovery
- attack.t1057
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/windows/process_creation/proc_creation_win_findstr_recon_pipe_output.yml
status: test
level: medium
author: Nasreddine Bencherchali (Nextron Systems), frack113
date: '2023-07-06'
modified: '2025-10-08'
related:
- id: fe63010f-8823-4864-a96b-a7b4a0f7b929
  type: derived
logsource:
  category: process_creation
  product: windows
---

# Recon Command Output Piped To Findstr.EXE

## Summary

Detects the execution of a potential recon command where the results are piped to "findstr". This is meant to trigger on inline calls of "cmd.exe" via the "/c" or "/k" for example.
Attackers often time use this technique to extract specific information they require in their reconnaissance phase.

## Rule metadata

- Rule ID: ccb5742c-c248-4982-8c5c-5571b9275ad3
- Status: test
- Level: medium
- Author: Nasreddine Bencherchali (Nextron Systems), frack113
- Created: 2023-07-06
- Modified: 2025-10-08
- Upstream path: rules/windows/process_creation/proc_creation_win_findstr_recon_pipe_output.yml

## Log source

```yaml
category: process_creation
product: windows
```

## Detection logic

```yaml
selection:
  CommandLine|contains:
  - ipconfig*|*find
  - net*|*find
  - netstat*|*find
  - ping*|*find
  - systeminfo*|*find
  - tasklist*|*find
  - whoami*|*find
filter_optional_xampp:
  CommandLine|contains|all:
  - cmd.exe /c TASKLIST /V |
  - FIND /I
  - \xampp\
  - \catalina_start.bat
condition: selection and not 1 of filter_optional_*
```

## False positives

- Unknown

## References

- https://github.com/redcanaryco/atomic-red-team/blob/02cb591f75064ffe1e0df9ac3ed5972a2e491c97/atomics/T1057/T1057.md#atomic-test-6---discover-specific-process---tasklist
- https://www.hhs.gov/sites/default/files/manage-engine-vulnerability-sector-alert-tlpclear.pdf
- https://www.trendmicro.com/en_us/research/22/d/spring4shell-exploited-to-deploy-cryptocurrency-miners.html

## ATT&CK and Sigma tags

- attack.discovery
- attack.t1057
