---
title: Potential Malicious Usage of CloudTrail System Manager
source_type: sigma_rule
external_id: 38e7f511-3f74-41d4-836e-f57dfa18eead
source_url: https://github.com/SigmaHQ/sigma/blob/f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d/rules/cloud/aws/cloudtrail/aws_cloudtrail_ssm_malicious_usage.yml
source_revision: 2025-12-08@f321ac84b7cb
language: en
domain: detection_engineering
tags:
- sigma
- attack.privilege-escalation
- attack.initial-access
- attack.t1566
- attack.t1566.002
repository: SigmaHQ/sigma
repository_revision: f321ac84b7cb0c1e688bb1a6415d0bf73d767d1d
upstream_path: rules/cloud/aws/cloudtrail/aws_cloudtrail_ssm_malicious_usage.yml
status: test
level: high
author: jamesc-grafana
date: '2024-07-11'
modified: '2025-12-08'
related: []
logsource:
  product: aws
  service: cloudtrail
---

# Potential Malicious Usage of CloudTrail System Manager

## Summary

Detect when System Manager successfully executes commands against an instance.

## Rule metadata

- Rule ID: 38e7f511-3f74-41d4-836e-f57dfa18eead
- Status: test
- Level: high
- Author: jamesc-grafana
- Created: 2024-07-11
- Modified: 2025-12-08
- Upstream path: rules/cloud/aws/cloudtrail/aws_cloudtrail_ssm_malicious_usage.yml

## Log source

```yaml
product: aws
service: cloudtrail
```

## Detection logic

```yaml
selection_event:
  eventName: SendCommand
  eventSource: ssm.amazonaws.com
selection_status_success:
  errorCode: Success
selection_status_null:
  errorCode: null
condition: selection_event and 1 of selection_status_*
```

## False positives

- There are legitimate uses of SSM to send commands to EC2 instances
- Legitimate users may have to use SSM to perform actions against machines in the Cloud to update or maintain them

## References

- https://github.com/elastic/detection-rules/blob/v8.6.0/rules/integrations/aws/initial_access_via_system_manager.toml

## ATT&CK and Sigma tags

- attack.privilege-escalation
- attack.initial-access
- attack.t1566
- attack.t1566.002
