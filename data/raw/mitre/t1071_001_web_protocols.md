---
title: T1071.001 — Web Protocols
source_type: mitre_attack
external_id: T1071.001
source_url: https://attack.mitre.org/techniques/T1071/001
source_revision: 1.5@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1071.001
- attack.command-and-control
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--df8b2a25-8bdf-4856-953c-a04372b1c161
stix_modified: '2026-05-12T15:12:00.722Z'
technique_version: '1.5'
is_subtechnique: true
tactics:
- command-and-control
platforms:
- ESXi
- Linux
- Network Devices
- Windows
- macOS
permissions_required: []
data_sources: []
---

# T1071.001 — Web Protocols

## Description

Adversaries may communicate using application layer protocols associated with web traffic to avoid detection/network filtering by blending in with existing traffic. Commands to the remote system, and often the results of those commands, will be embedded within the protocol traffic between the client and server. 

Protocols such as HTTP/S(Citation: CrowdStrike Putter Panda) and WebSocket(Citation: Brazking-Websockets) that carry web traffic may be very common in environments. HTTP/S packets have many fields and headers in which data can be concealed. An adversary may abuse these protocols to communicate with systems under their control within a victim network while also mimicking normal, expected traffic.

## ATT&CK tactics

- command-and-control

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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1071/001
- STIX object: attack-pattern--df8b2a25-8bdf-4856-953c-a04372b1c161
- ATT&CK object version: 1.5
