---
title: T1560.001 — Archive via Utility
source_type: mitre_attack
external_id: T1560.001
source_url: https://attack.mitre.org/techniques/T1560/001
source_revision: 1.3@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1560.001
- attack.collection
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--00f90846-cbd1-4fc5-9233-df5c2bf2a662
stix_modified: '2026-05-12T15:12:00.619Z'
technique_version: '1.3'
is_subtechnique: true
tactics:
- collection
platforms:
- Linux
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1560.001 — Archive via Utility

## Description

Adversaries may use utilities to compress and/or encrypt collected data prior to exfiltration. Many utilities include functionalities to compress, encrypt, or otherwise package data into a format that is easier/more secure to transport.

Adversaries may abuse various utilities to compress or encrypt data before exfiltration. Some third party utilities may be preinstalled, such as <code>tar</code> on Linux and macOS or <code>zip</code> on Windows systems. 

On Windows, <code>diantz</code> or <code> makecab</code> may be used to package collected files into a cabinet (.cab) file. <code>diantz</code> may also be used to download and compress files from remote locations (i.e. [Remote Data Staging](https://attack.mitre.org/techniques/T1074/002)).(Citation: diantz.exe_lolbas) <code>xcopy</code> on Windows can copy files and directories with a variety of options. Additionally, adversaries may use [certutil](https://attack.mitre.org/software/S0160) to Base64 encode collected data before exfiltration. 

Adversaries may use also third party utilities, such as 7-Zip, WinRAR, and WinZip, to perform similar activities.(Citation: 7zip Homepage)(Citation: WinRAR Homepage)(Citation: WinZip Homepage)

## ATT&CK tactics

- collection

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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1560/001
- STIX object: attack-pattern--00f90846-cbd1-4fc5-9233-df5c2bf2a662
- ATT&CK object version: 1.3
