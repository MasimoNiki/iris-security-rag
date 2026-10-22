---
title: T1552.001 — Credentials In Files
source_type: mitre_attack
external_id: T1552.001
source_url: https://attack.mitre.org/techniques/T1552/001
source_revision: 1.3@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1552.001
- attack.credential-access
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--837f9164-50af-4ac0-8219-379d8a74cefc
stix_modified: '2026-05-12T15:12:00.672Z'
technique_version: '1.3'
is_subtechnique: true
tactics:
- credential-access
platforms:
- Containers
- IaaS
- Linux
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1552.001 — Credentials In Files

## Description

Adversaries may search local file systems and remote file shares for files containing insecurely stored credentials. These can be files created by users to store their own credentials, shared credential stores for a group of individuals, configuration files containing passwords for a system or service, or source code/binary files containing embedded passwords.

It is possible to extract passwords from backups or saved virtual machines through [OS Credential Dumping](https://attack.mitre.org/techniques/T1003).(Citation: CG 2014) Passwords may also be obtained from Group Policy Preferences stored on the Windows Domain Controller.(Citation: SRD GPP)

In cloud and/or containerized environments, authenticated user and service account credentials are often stored in local configuration and credential files.(Citation: Unit 42 Hildegard Malware) They may also be found as parameters to deployment commands in container logs.(Citation: Unit 42 Unsecured Docker Daemons) In some cases, these files can be copied and reused on another machine or the contents can be read and then used to authenticate without needing to copy any files.(Citation: Specter Ops - Cloud Credential Storage)

## ATT&CK tactics

- credential-access

## Platforms

- Containers
- IaaS
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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1552/001
- STIX object: attack-pattern--837f9164-50af-4ac0-8219-379d8a74cefc
- ATT&CK object version: 1.3
