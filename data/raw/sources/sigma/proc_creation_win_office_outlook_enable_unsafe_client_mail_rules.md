---
title: "Outlook EnableUnsafeClientMailRules Setting Enabled"
source_type: "sigma_rule"
language: "en"
domain: "detection_engineering"
tags: ['sigma', 'attack.execution', 'attack.stealth', 'attack.t1059', 'attack.t1202']
---

# Outlook EnableUnsafeClientMailRules Setting Enabled

## Summary

Detects an attacker trying to enable the outlook security setting "EnableUnsafeClientMailRules" which allows outlook to run applications or execute macros

## Sigma metadata

- Rule ID: 55f0a3a1-846e-40eb-8273-677371b8d912
- Status: test
- Author: Markus Neis, Nasreddine Bencherchali (Nextron Systems)
- Date: 2018-12-27
- Modified: 2023-02-09
- Level: high
- Source file: data/external/sigma/proc_creation_win_office_outlook_enable_unsafe_client_mail_rules.yml

## Logsource

- category: process_creation
- product: windows

## Detection logic

- selection: {'CommandLine|contains': '\\Outlook\\Security\\EnableUnsafeClientMailRules'}
- condition: selection

## False positives

- Unknown

## References

- https://www.fireeye.com/blog/threat-research/2018/12/overruled-containing-a-potentially-destructive-adversary.html
- https://speakerdeck.com/heirhabarov/hunting-for-persistence-via-microsoft-exchange-server-or-outlook?slide=44
- https://support.microsoft.com/en-us/topic/how-to-control-the-rule-actions-to-start-an-application-or-run-a-macro-in-outlook-2016-and-outlook-2013-e4964b72-173c-959d-5d7b-ead562979048

## Tags

- attack.execution
- attack.stealth
- attack.t1059
- attack.t1202
