---
title: T1041 — Exfiltration Over C2 Channel
source_type: mitre_attack
external_id: T1041
source_url: https://attack.mitre.org/techniques/T1041
source_revision: 2.3@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1041
- attack.exfiltration
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--92d7da27-2d91-488e-a00c-059dc162766d
stix_modified: '2026-05-12T15:12:00.706Z'
technique_version: '2.3'
is_subtechnique: false
tactics:
- exfiltration
platforms:
- ESXi
- Linux
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1041 — Exfiltration Over C2 Channel

## Description

Adversaries may steal data by exfiltrating it over an existing command and control channel. Stolen data is encoded into the normal communications channel using the same protocol as command and control communications.

## ATT&CK tactics

- exfiltration

## Platforms

- ESXi
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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1041
- STIX object: attack-pattern--92d7da27-2d91-488e-a00c-059dc162766d
- ATT&CK object version: 2.3
