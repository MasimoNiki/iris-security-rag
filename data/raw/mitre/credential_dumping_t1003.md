---
title: T1003 — OS Credential Dumping
source_type: mitre_attack
external_id: T1003
source_url: https://attack.mitre.org/techniques/T1003
source_revision: 2.2@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1003
- attack.credential-access
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--0a3ead4e-6d47-4ccb-854c-a6a4f9d96b22
stix_modified: '2025-10-24T17:48:22.201Z'
technique_version: '2.2'
is_subtechnique: false
tactics:
- credential-access
platforms:
- Linux
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1003 — OS Credential Dumping

## Description

Adversaries may attempt to dump credentials to obtain account login and credential material, normally in the form of a hash or a clear text password. Credentials can be obtained from OS caches, memory, or structures.(Citation: Brining MimiKatz to Unix) Credentials can then be used to perform [Lateral Movement](https://attack.mitre.org/tactics/TA0008) and access restricted information.

Several of the tools mentioned in associated sub-techniques may be used by both adversaries and professional security testers. Additional custom tools likely exist as well.

## ATT&CK tactics

- credential-access

## Platforms

- Linux
- Windows
- macOS

## Permissions required

- Not specified

## Data sources

- Not specified

## Detection

Detection guidance is not present in this technique object.

## Source

- Official ATT&CK page: https://attack.mitre.org/techniques/T1003
- STIX object: attack-pattern--0a3ead4e-6d47-4ccb-854c-a6a4f9d96b22
- ATT&CK object version: 2.2
