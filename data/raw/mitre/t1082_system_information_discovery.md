---
title: T1082 — System Information Discovery
source_type: mitre_attack
external_id: T1082
source_url: https://attack.mitre.org/techniques/T1082
source_revision: 3.0@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1082
- attack.discovery
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--354a7f88-63fb-41b5-a801-ce3b377b36f1
stix_modified: '2026-05-12T15:12:00.625Z'
technique_version: '3.0'
is_subtechnique: false
tactics:
- discovery
platforms:
- ESXi
- IaaS
- Linux
- Network Devices
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1082 — System Information Discovery

## Description

An adversary may attempt to get detailed information about the operating system and hardware, including version, patches, hotfixes, service packs, and architecture. Adversaries may use this information to shape follow-on behaviors, including whether or not the adversary fully infects the target and/or attempts specific actions. This behavior is distinct from [Local Storage Discovery](https://attack.mitre.org/techniques/T1680) which is an adversary's discovery of local drive, disks and/or volumes.

Tools such as [Systeminfo](https://attack.mitre.org/software/S0096) can be used to gather detailed system information. If running with privileged access, a breakdown of system data can be gathered through the <code>systemsetup</code> configuration tool on macOS. Adversaries may leverage a [Network Device CLI](https://attack.mitre.org/techniques/T1059/008) on network devices to gather detailed system information (e.g. <code>show version</code>).(Citation: US-CERT-TA18-106A) On ESXi servers, threat actors may gather system information from various esxcli utilities, such as `system hostname get` and `system version get`.(Citation: Crowdstrike Hypervisor Jackpotting Pt 2 2021)(Citation: Varonis)

Infrastructure as a Service (IaaS) cloud providers such as AWS, GCP, and Azure allow access to instance and virtual machine information via APIs. Successful authenticated API calls can return data such as the operating system platform and status of a particular instance or the model view of a virtual machine.(Citation: Amazon Describe Instance)(Citation: Google Instances Resource)(Citation: Microsoft Virutal Machine API)

[System Information Discovery](https://attack.mitre.org/techniques/T1082) combined with information gathered from other forms of discovery and reconnaissance can drive payload development and concealment.(Citation: OSX.FairyTale)(Citation: 20 macOS Common Tools and Techniques)

## ATT&CK tactics

- discovery

## Platforms

- ESXi
- IaaS
- Linux
- Network Devices
- Windows
- macOS

## Permissions required

- Not specified

## Data sources

- Not specified

## Detection

Detection guidance is not present in this technique object.

## Source

- Official ATT&CK page: https://attack.mitre.org/techniques/T1082
- STIX object: attack-pattern--354a7f88-63fb-41b5-a801-ce3b377b36f1
- ATT&CK object version: 3.0
