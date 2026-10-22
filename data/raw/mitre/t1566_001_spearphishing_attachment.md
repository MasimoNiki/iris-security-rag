---
title: T1566.001 — Spearphishing Attachment
source_type: mitre_attack
external_id: T1566.001
source_url: https://attack.mitre.org/techniques/T1566/001
source_revision: 2.2@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1566.001
- attack.initial-access
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--2e34237d-8574-43f6-aace-ae2915de8597
stix_modified: '2026-05-12T15:12:00.624Z'
technique_version: '2.2'
is_subtechnique: true
tactics:
- initial-access
platforms:
- Linux
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1566.001 — Spearphishing Attachment

## Description

Adversaries may send spearphishing emails with a malicious attachment in an attempt to gain access to victim systems. Spearphishing attachment is a specific variant of spearphishing. Spearphishing attachment is different from other forms of spearphishing in that it employs the use of malware attached to an email. All forms of spearphishing are electronically delivered social engineering targeted at a specific individual, company, or industry. In this scenario, adversaries attach a file to the spearphishing email and usually rely upon [User Execution](https://attack.mitre.org/techniques/T1204) to gain execution.(Citation: Unit 42 DarkHydrus July 2018) Spearphishing may also involve social engineering techniques, such as posing as a trusted source.

There are many options for the attachment such as Microsoft Office documents, executables, PDFs, or archived files. Upon opening the attachment (and potentially clicking past protections), the adversary's payload exploits a vulnerability or directly executes on the user's system. The text of the spearphishing email usually tries to give a plausible reason why the file should be opened, and may explain how to bypass system protections in order to do so. The email may also contain instructions on how to decrypt an attachment, such as a zip file password, in order to evade email boundary defenses. Adversaries frequently manipulate file extensions and icons in order to make attached executables appear to be document files, or files exploiting one application appear to be a file for a different one.

## ATT&CK tactics

- initial-access

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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1566/001
- STIX object: attack-pattern--2e34237d-8574-43f6-aace-ae2915de8597
- ATT&CK object version: 2.2
