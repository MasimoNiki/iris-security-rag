---
title: T1018 — Remote System Discovery
source_type: mitre_attack
external_id: T1018
source_url: https://attack.mitre.org/techniques/T1018
source_revision: 3.6@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1018
- attack.discovery
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--e358d692-23c0-4a31-9eb6-ecc13a8d7735
stix_modified: '2026-05-12T15:12:00.722Z'
technique_version: '3.6'
is_subtechnique: false
tactics:
- discovery
platforms:
- ESXi
- Linux
- Network Devices
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1018 — Remote System Discovery

## Description

Adversaries may attempt to get a listing of other systems by IP address, hostname, or other logical identifier on a network that may be used for Lateral Movement from the current system. Functionality could exist within remote access tools to enable this, but utilities available on the operating system could also be used such as  [Ping](https://attack.mitre.org/software/S0097), <code>net view</code> using [Net](https://attack.mitre.org/software/S0039), or, on ESXi servers, `esxcli network diag ping`.

Adversaries may also analyze data from local host files (ex: <code>C:\Windows\System32\Drivers\etc\hosts</code> or <code>/etc/hosts</code>) or other passive means (such as local [Arp](https://attack.mitre.org/software/S0099) cache entries) in order to discover the presence of remote systems in an environment.

Adversaries may also target discovery of network infrastructure as well as leverage [Network Device CLI](https://attack.mitre.org/techniques/T1059/008) commands on network devices to gather detailed information about systems within a network (e.g. <code>show cdp neighbors</code>, <code>show arp</code>).(Citation: US-CERT-TA18-106A)(Citation: CISA AR21-126A FIVEHANDS May 2021)

## ATT&CK tactics

- discovery

## Platforms

- ESXi
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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1018
- STIX object: attack-pattern--e358d692-23c0-4a31-9eb6-ecc13a8d7735
- ATT&CK object version: 3.6
