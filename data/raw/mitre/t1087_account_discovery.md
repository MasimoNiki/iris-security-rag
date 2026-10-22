---
title: T1087 — Account Discovery
source_type: mitre_attack
external_id: T1087
source_url: https://attack.mitre.org/techniques/T1087
source_revision: 2.6@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1087
- attack.discovery
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--72b74d71-8169-42aa-92e0-e7b04b9f5a08
stix_modified: '2026-05-12T15:12:00.641Z'
technique_version: '2.6'
is_subtechnique: false
tactics:
- discovery
platforms:
- ESXi
- IaaS
- Identity Provider
- Linux
- Office Suite
- SaaS
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1087 — Account Discovery

## Description

Adversaries may attempt to get a listing of valid accounts, usernames, or email addresses on a system or within a compromised environment. This information can help adversaries determine which accounts exist, which can aid in follow-on behavior such as brute-forcing, spear-phishing attacks, or account takeovers (e.g., [Valid Accounts](https://attack.mitre.org/techniques/T1078)).

Adversaries may use several methods to enumerate accounts, including abuse of existing tools, built-in commands, and potential misconfigurations that leak account names and roles or permissions in the targeted environment.

For examples, cloud environments typically provide easily accessible interfaces to obtain user lists.(Citation: AWS List Users)(Citation: Google Cloud - IAM Servie Accounts List API) On hosts, adversaries can use default [PowerShell](https://attack.mitre.org/techniques/T1059/001) and other command line functionality to identify accounts. Information about email addresses and accounts may also be extracted by searching an infected system’s files.

## ATT&CK tactics

- discovery

## Platforms

- ESXi
- IaaS
- Identity Provider
- Linux
- Office Suite
- SaaS
- Windows
- macOS

## Permissions required

- Not specified

## Data sources

- Not specified

## Detection

Detection guidance is not present in this technique object.

## Source

- Official ATT&CK page: https://attack.mitre.org/techniques/T1087
- STIX object: attack-pattern--72b74d71-8169-42aa-92e0-e7b04b9f5a08
- ATT&CK object version: 2.6
