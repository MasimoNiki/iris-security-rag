---
title: T1059.001 — PowerShell
source_type: mitre_attack
external_id: T1059.001
source_url: https://attack.mitre.org/techniques/T1059/001
source_revision: 1.5@a6c366439ede
language: en
domain: enterprise_attack
tags:
- mitre_attack
- t1059.001
- attack.execution
repository: mitre-attack/attack-stix-data
repository_revision: a6c366439edee3a87b79cf90dc0b93f5d7975956
upstream_path: enterprise-attack/enterprise-attack.json
stix_id: attack-pattern--970a3432-3237-47ad-bcca-7d8cbb217736
stix_modified: '2026-05-12T15:12:00.706Z'
technique_version: '1.5'
is_subtechnique: true
tactics:
- execution
platforms:
- Windows
permissions_required: []
data_sources: []
---

# T1059.001 — PowerShell

## Description

Adversaries may abuse PowerShell commands and scripts for execution. PowerShell is a powerful interactive command-line interface and scripting environment included in the Windows operating system.(Citation: TechNet PowerShell) Adversaries can use PowerShell to perform a number of actions, including discovery of information and execution of code. Examples include the <code>Start-Process</code> cmdlet which can be used to run an executable and the <code>Invoke-Command</code> cmdlet which runs a command locally or on a remote computer (though administrator permissions are required to use PowerShell to connect to remote systems).

PowerShell may also be used to download and run executables from the Internet, which can be executed from disk or in memory without touching disk.

A number of PowerShell-based offensive testing tools are available, including [Empire](https://attack.mitre.org/software/S0363),  [PowerSploit](https://attack.mitre.org/software/S0194), [PoshC2](https://attack.mitre.org/software/S0378), and PSAttack.(Citation: Github PSAttack)

PowerShell commands/scripts can also be executed without directly invoking the <code>powershell.exe</code> binary through interfaces to PowerShell's underlying <code>System.Management.Automation</code> assembly DLL exposed through the .NET framework and Windows Common Language Interface (CLI).(Citation: Sixdub PowerPick Jan 2016)(Citation: SilentBreak Offensive PS Dec 2015)(Citation: Microsoft PSfromCsharp APR 2014)

## ATT&CK tactics

- execution

## Platforms

- Windows

## Permissions required

- Not specified

## Data sources

- Not specified

## Detection

Detection guidance is not present in this technique object.

## Source

- Official ATT&CK page: https://attack.mitre.org/techniques/T1059/001
- STIX object: attack-pattern--970a3432-3237-47ad-bcca-7d8cbb217736
- ATT&CK object version: 1.5
