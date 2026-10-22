---
title: T1204.002 — Malicious File
source_type: mitre_attack
external_id: T1204.002
source_url: https://attack.mitre.org/techniques/T1204/002
source_revision: 1.6@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1204.002
- attack.execution
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--232b7f21-adf9-4b42-b936-b9d6f7df856e
stix_modified: '2026-05-12T15:12:00.623Z'
technique_version: '1.6'
is_subtechnique: true
tactics:
- execution
platforms:
- Linux
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1204.002 — Malicious File

## Description

An adversary may rely upon a user opening a malicious file in order to gain execution. Users may be subjected to social engineering to get them to open a file that will lead to code execution. This user action will typically be observed as follow-on behavior from [Spearphishing Attachment](https://attack.mitre.org/techniques/T1566/001). Adversaries may use several types of files that require a user to execute them, including .doc, .pdf, .xls, .rtf, .scr, .exe, .lnk, .pif, .cpl, .reg, and .iso.(Citation: Mandiant Trojanized Windows 10)

Adversaries may employ various forms of [Masquerading](https://attack.mitre.org/techniques/T1036) and [Obfuscated Files or Information](https://attack.mitre.org/techniques/T1027) to increase the likelihood that a user will open and successfully execute a malicious file. These methods may include using a familiar naming convention and/or password protecting the file and supplying instructions to a user on how to open it.(Citation: Password Protected Word Docs) 

While [Malicious File](https://attack.mitre.org/techniques/T1204/002) frequently occurs shortly after Initial Access it may occur at other phases of an intrusion, such as when an adversary places a file in a shared directory or on a user's desktop hoping that a user will click on it. This activity may also be seen shortly after [Internal Spearphishing](https://attack.mitre.org/techniques/T1534).

## ATT&CK tactics

- execution

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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1204/002
- STIX object: attack-pattern--232b7f21-adf9-4b42-b936-b9d6f7df856e
- ATT&CK object version: 1.6
