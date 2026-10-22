---
title: T1555 — Credentials from Password Stores
source_type: mitre_attack
external_id: T1555
source_url: https://attack.mitre.org/techniques/T1555
source_revision: 1.2@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1555
- attack.credential-access
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--3fc9b85a-2862-4363-a64d-d692e3ffbee0
stix_modified: '2026-05-12T15:12:00.628Z'
technique_version: '1.2'
is_subtechnique: false
tactics:
- credential-access
platforms:
- IaaS
- Linux
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1555 — Credentials from Password Stores

## Description

Adversaries may search for common password storage locations to obtain user credentials.(Citation: F-Secure The Dukes) Passwords are stored in several places on a system, depending on the operating system or application holding the credentials. There are also specific applications and services that store passwords to make them easier for users to manage and maintain, such as password managers and cloud secrets vaults. Once credentials are obtained, they can be used to perform lateral movement and access restricted information.

## ATT&CK tactics

- credential-access

## Platforms

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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1555
- STIX object: attack-pattern--3fc9b85a-2862-4363-a64d-d692e3ffbee0
- ATT&CK object version: 1.2
