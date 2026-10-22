---
title: T1021.001 — Remote Desktop Protocol
source_type: mitre_attack
external_id: T1021.001
source_url: https://attack.mitre.org/techniques/T1021/001
source_revision: 1.4@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1021.001
- attack.lateral-movement
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--eb062747-2193-45de-8fa2-e62549c37ddf
stix_modified: '2026-05-12T15:12:00.723Z'
technique_version: '1.4'
is_subtechnique: true
tactics:
- lateral-movement
platforms:
- Windows
permissions_required: []
data_sources: []
---

# T1021.001 — Remote Desktop Protocol

## Description

Adversaries may use [Valid Accounts](https://attack.mitre.org/techniques/T1078) to log into a computer using the Remote Desktop Protocol (RDP). The adversary may then perform actions as the logged-on user.

Remote desktop is a common feature in operating systems. It allows a user to log into an interactive session with a system desktop graphical user interface on a remote system. Microsoft refers to its implementation of the Remote Desktop Protocol (RDP) as Remote Desktop Services (RDS).(Citation: TechNet Remote Desktop Services) 

Adversaries may connect to a remote system over RDP/RDS to expand access if the service is enabled and allows access to accounts with known credentials. Adversaries will likely use Credential Access techniques to acquire credentials to use with RDP. Adversaries may also use RDP in conjunction with the [Accessibility Features](https://attack.mitre.org/techniques/T1546/008) or [Terminal Services DLL](https://attack.mitre.org/techniques/T1505/005) for Persistence.(Citation: Alperovitch Malware)

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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1021/001
- STIX object: attack-pattern--eb062747-2193-45de-8fa2-e62549c37ddf
- ATT&CK object version: 1.4
