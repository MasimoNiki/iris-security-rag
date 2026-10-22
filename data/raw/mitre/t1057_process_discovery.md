---
title: T1057 — Process Discovery
source_type: mitre_attack
external_id: T1057
source_url: https://attack.mitre.org/techniques/T1057
source_revision: 1.6@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1057
- attack.discovery
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--8f4a33ec-8b1f-4b80-a2f6-642b2e479580
stix_modified: '2026-05-12T15:12:00.705Z'
technique_version: '1.6'
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

# T1057 — Process Discovery

## Description

Adversaries may attempt to get information about running processes on a system. Information obtained could be used to gain an understanding of common software/applications running on systems within the network. Administrator or otherwise elevated access may provide better process details. Adversaries may use the information from [Process Discovery](https://attack.mitre.org/techniques/T1057) during automated discovery to shape follow-on behaviors, including whether or not the adversary fully infects the target and/or attempts specific actions.

In Windows environments, adversaries could obtain details on running processes using the [Tasklist](https://attack.mitre.org/software/S0057) utility via [cmd](https://attack.mitre.org/software/S0106) or <code>Get-Process</code> via [PowerShell](https://attack.mitre.org/techniques/T1059/001). Information about processes can also be extracted from the output of [Native API](https://attack.mitre.org/techniques/T1106) calls such as <code>CreateToolhelp32Snapshot</code>. In Mac and Linux, this is accomplished with the <code>ps</code> command. Adversaries may also opt to enumerate processes via `/proc`. ESXi also supports use of the `ps` command, as well as `esxcli system process list`.(Citation: Sygnia ESXi Ransomware 2025)(Citation: Crowdstrike Hypervisor Jackpotting Pt 2 2021)

On network devices, [Network Device CLI](https://attack.mitre.org/techniques/T1059/008) commands such as `show processes` can be used to display current running processes.(Citation: US-CERT-TA18-106A)(Citation: show_processes_cisco_cmd)

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

- Official ATT&CK page: https://attack.mitre.org/techniques/T1057
- STIX object: attack-pattern--8f4a33ec-8b1f-4b80-a2f6-642b2e479580
- ATT&CK object version: 1.6
