---
title: T1569.002 — Service Execution
source_type: mitre_attack
external_id: T1569.002
source_url: https://attack.mitre.org/techniques/T1569/002
source_revision: 1.3@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1569.002
- attack.execution
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--f1951e8a-500e-4a26-8803-76d95c4554b4
stix_modified: '2026-05-12T15:12:00.723Z'
technique_version: '1.3'
is_subtechnique: true
tactics:
- execution
platforms:
- Windows
permissions_required: []
data_sources: []
---

# T1569.002 — Service Execution

## Description

Adversaries may abuse the Windows service control manager to execute malicious commands or payloads. The Windows service control manager (<code>services.exe</code>) is an interface to manage and manipulate services.(Citation: Microsoft Service Control Manager) The service control manager is accessible to users via GUI components as well as system utilities such as <code>sc.exe</code> and [Net](https://attack.mitre.org/software/S0039).

[PsExec](https://attack.mitre.org/software/S0029) can also be used to execute commands or payloads via a temporary Windows service created through the service control manager API.(Citation: Russinovich Sysinternals) Tools such as [PsExec](https://attack.mitre.org/software/S0029) and <code>sc.exe</code> can accept remote servers as arguments and may be used to conduct remote execution.

Adversaries may leverage these mechanisms to execute malicious content. This can be done by either executing a new or modified service. This technique is the execution used in conjunction with [Windows Service](https://attack.mitre.org/techniques/T1543/003) during service persistence or privilege escalation.

## ATT&CK tactics

- execution

## Platforms

- Windows

## Permissions required

- Not specified

## Data sources

- Not specified

## Detection

Detection guidance is not present in this technique object.

## Source

- Official ATT&CK page: https://attack.mitre.org/techniques/T1569/002
- STIX object: attack-pattern--f1951e8a-500e-4a26-8803-76d95c4554b4
- ATT&CK object version: 1.3
