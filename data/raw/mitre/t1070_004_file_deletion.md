---
title: T1070.004 — File Deletion
source_type: mitre_attack
external_id: T1070.004
source_url: https://attack.mitre.org/techniques/T1070/004
source_revision: 2.0@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1070.004
- attack.stealth
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--d63a3fb8-9452-4e9d-a60a-54be68d5998c
stix_modified: '2026-05-12T15:12:00.718Z'
technique_version: '2.0'
is_subtechnique: true
tactics:
- stealth
platforms:
- ESXi
- Linux
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1070.004 — File Deletion

## Description

Adversaries may delete files left behind by the actions of their intrusion activity. Malware, tools, or other non-native files dropped or created on a system by an adversary (ex: [Ingress Tool Transfer](https://attack.mitre.org/techniques/T1105)) may leave traces to indicate to what was done within a network and how. Removal of these files can occur during an intrusion, or as part of a post-intrusion process to minimize the adversary's footprint.

There are tools available from the host operating system to perform cleanup, but adversaries may use other tools as well.(Citation: Microsoft SDelete July 2016) Examples of built-in [Command and Scripting Interpreter](https://attack.mitre.org/techniques/T1059) functions include <code>del</code> on Windows, <code>rm</code> or <code>unlink</code> on Linux and macOS, and `rm` on ESXi.

## ATT&CK tactics

- stealth

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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1070/004
- STIX object: attack-pattern--d63a3fb8-9452-4e9d-a60a-54be68d5998c
- ATT&CK object version: 2.0
