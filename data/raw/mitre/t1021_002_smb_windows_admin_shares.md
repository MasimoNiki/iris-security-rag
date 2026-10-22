---
title: T1021.002 — SMB/Windows Admin Shares
source_type: mitre_attack
external_id: T1021.002
source_url: https://attack.mitre.org/techniques/T1021/002
source_revision: 1.3@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1021.002
- attack.lateral-movement
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--4f9ca633-15c5-463c-9724-bdcd54fde541
stix_modified: '2026-05-12T15:12:00.632Z'
technique_version: '1.3'
is_subtechnique: true
tactics:
- lateral-movement
platforms:
- Windows
permissions_required: []
data_sources: []
---

# T1021.002 — SMB/Windows Admin Shares

## Description

Adversaries may use [Valid Accounts](https://attack.mitre.org/techniques/T1078) to interact with a remote network share using Server Message Block (SMB). The adversary may then perform actions as the logged-on user.

SMB is a file, printer, and serial port sharing protocol for Windows machines on the same network or domain. Adversaries may use SMB to interact with file shares, allowing them to move laterally throughout a network. Linux and macOS implementations of SMB typically use Samba.

Windows systems have hidden network shares that are accessible only to administrators and provide the ability for remote file copy and other administrative functions. Example network shares include `C$`, `ADMIN$`, and `IPC$`. Adversaries may use this technique in conjunction with administrator-level [Valid Accounts](https://attack.mitre.org/techniques/T1078) to remotely access a networked system over SMB,(Citation: Wikipedia Server Message Block) to interact with systems using remote procedure calls (RPCs),(Citation: TechNet RPC) transfer files, and run transferred binaries through remote Execution. Example execution techniques that rely on authenticated sessions over SMB/RPC are [Scheduled Task/Job](https://attack.mitre.org/techniques/T1053), [Service Execution](https://attack.mitre.org/techniques/T1569/002), and [Windows Management Instrumentation](https://attack.mitre.org/techniques/T1047). Adversaries can also use NTLM hashes to access administrator shares on systems with [Pass the Hash](https://attack.mitre.org/techniques/T1550/002) and certain configuration and patch levels.(Citation: Microsoft Admin Shares)

## ATT&CK tactics

- lateral-movement

## Platforms

- Windows

## Permissions required

- Not specified

## Data sources

- Not specified

## Detection

Detection guidance is not present in this technique object.

## Source

- Official ATT&CK page: https://attack.mitre.org/techniques/T1021/002
- STIX object: attack-pattern--4f9ca633-15c5-463c-9724-bdcd54fde541
- ATT&CK object version: 1.3
