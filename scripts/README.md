# Scripts

Small utilities I built while working through labs and CTF-style machines. Each one automates a manual step I found myself repeating — the goal isn't to reinvent existing tools, but to understand the underlying technique well enough to script it myself.

> ⚠️ **Disclaimer:** These scripts are for educational use in authorized lab, CTF, or otherwise permitted environments only (e.g. Hack The Box, TryHackMe, personal labs). Do not run them against systems you don't have explicit permission to test.

---

## `creds_from_config.sh`

**What it does:** Parses a config file for `user=`/`pass=` (or `User:`/`Pass:`) style key-value pairs, normalizes casing and whitespace, and pairs each username with the password that follows it — printing matches as `user:pass`.

**Why I built it:** Came out of the [Archetype](../writeups/htb-archetype.md) box, where MSSQL service-account credentials were sitting in plaintext inside a config file on an unauthenticated SMB share. Manually grepping for `user=`/`pass=` got old fast, so I automated the pattern-matching and pairing logic.

**Usage:**
```bash
./creds_from_config.sh <config_file>
```

**Example:**
```bash
./creds_from_config.sh prod.dtsConfig
sql_svc:password123
```

**Notes / limitations:** Expects the username line to appear immediately before its matching password line. Pairs are matched strictly in order (`user:` line, then the next `pass:` line resets `current_user` once consumed) — a config with a different key order or extra fields between them won't pair correctly.

---

## `dns_enum_zonetransfer.sh`

**What it does:** Looks up the authoritative nameservers for a domain (`host -t ns`), then attempts a zone transfer (`AXFR`, via `host -l`) against each one, printing any `A` records returned.

**Why I built it:** Wanted a quick first-pass DNS check I could run before reaching for heavier tools like `dnsrecon`/`fierce`, and to understand how misconfigured zone transfers actually work at the protocol level.

**Usage:**
```bash
./dns_enum_zonetransfer.sh <domain>
```

**Example:**
```bash
./dns_enum_zonetransfer.sh megacorp.local
ns1.megacorp.local has address 10.129.14.2
web01.megacorp.local has address 10.129.14.5
```

**Notes / limitations:** If a nameserver refuses the transfer (the normal, secure default), it simply produces no output for that server — the script doesn't currently distinguish "refused" from "no records," so silence on a given NS just means the transfer didn't return anything.

---

## `smtp_enumeration.py`

**What it does:** Connects to an SMTP server on port 25, sends a `HELO`, then issues `VRFY <username>` for each entry in a wordlist, printing the server's response for any that don't come back "rejected."

**Why I built it:** Wanted to understand SMTP user enumeration at the protocol level rather than only running it through Metasploit/Nmap scripts, so I wrote a minimal version by hand against a raw socket.

**Usage:**
```bash
python3 smtp_enumeration.py <target_ip> <wordlist.txt>
```

**Example:**
```bash
python3 smtp_enumeration.py 10.129.14.20 users.txt
220 mail.megacorp.local ESMTP
250 mail.megacorp.local
252 2.0.0 administrator
252 2.0.0 mhope
```

**Notes / limitations:** Relies on `VRFY` being enabled, which many hardened mail servers disable by default — this is more of a protocol-learning exercise than a reliable enumeration technique against modern targets. No connection timeout is currently set, so a non-responsive host on port 25 will hang rather than time out cleanly.

---

## `port_scanner.py`

**What it does:** A single-threaded TCP connect scan against ports 1–1024 of a given IP. Attempts a full `connect()` on each port with a 1-second timeout and prints any that respond as open.

**Why I built it:** Wanted to understand what a tool like Nmap is actually doing under the hood at the socket level, rather than only using it as a black box. Not intended to replace Nmap or similar scanners — it's a learning exercise, not a production tool.

**Usage:**
```bash
python3 port_scanner.py
# then enter an IP address when prompted
```

**Example:**
```
Enter IP address to scan: 10.129.14.20
Loading....
[+] Port 22 is open
[+] Port 80 is open
[+] Port 445 is open
Scan complete.
```

**Notes / limitations:** Prompts interactively for the target rather than taking a CLI argument (unlike the other scripts here) — on the list to change to `argparse` for consistency. Scans sequentially, so it's slow (~1024 seconds worst case at the default 1s timeout); threading is the planned next step. This is a TCP connect scan, not a SYN scan, so it's easily logged by the target and shouldn't be mistaken for a stealthy technique.

---

## Requirements

- **`creds_from_config.sh`, `dns_enum_zonetransfer.sh`:** Bash, standard GNU utilities (`awk`, `grep`, `tr`, `host`, `cut`). Tested on Kali Linux.
- **`smtp_enumeration.py`:** Python 3, standard library only (`socket`, `sys`) — no external dependencies.
- **`port_scanner.py`:** Python 3, standard library (`socket`, `sys`) plus the `pyfiglet` package (`pip install pyfiglet`).

## Notes

- None of these currently have a `-h`/`--help` flag — running with the wrong number of arguments (or, for `port_scanner.py`, at the interactive prompt) prints a usage message and exits.
- Written for clarity and learning first, performance second. Happy to take suggestions/PRs for improvements — known limitations for each script are noted above rather than hidden.
