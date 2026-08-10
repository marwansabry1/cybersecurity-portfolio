# Cybersecurity Portfolio

Notes, writeups, and tooling from my CPTS preparation journey — documenting methodology as I build it, not just final answers.

> ⚠️ For educational use only. All testing was performed in authorized lab/CTF environments (Hack The Box, TryHackMe, personal labs).

## Writeups

| Box | OS | Difficulty | Key Skills |
|---|---|---|---|
| [Archetype](writeups/htb-archetype.md) | Windows | Easy | SMB enum, MSSQL abuse, `xp_cmdshell`, credential reuse |

## Notes

Methodology, cheat sheets, and lab reference organized by topic — see [`notes/`](notes/).

## Tools

Small scripts written to automate patterns I kept repeating manually. See [`scripts/README.md`](scripts/README.md) for details, usage, and the reasoning behind each one.

| Script | Purpose |
|---|---|
| `creds_from_config.sh` | Extract user/pass pairs from config files |
| `dns_enum_zonetransfer.sh` | Enumerate nameservers and attempt zone transfers |
| `smtp_enumeration.py` | SMTP user enumeration via `VRFY` |

## About

Working toward CPTS. This repo is both exam prep and a record of how I actually approach a target — enumeration first, documented reasoning, and honest write-ups of what didn't work as well as what did.