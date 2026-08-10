#!/usr/bin/python3
import socket, sys

if len(sys.argv) != 3:
    print("Usage: <IP> <file>")
    sys.exit(0)

ip = sys.argv[1]
file = sys.argv[2]

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, 25))

    print(s.recv(1024).decode().strip())

    # SMTP requires HELO
    s.send(b"HELO test\r\n")
    print(s.recv(1024).decode().strip())

    with open(file) as f:
        for x in f:
            user = x.strip()
            if not user:
                continue
            s.send(f"VRFY {user}\r\n".encode())
            back = s.recv(1024).decode().strip()
            if (back.find("rejected")!=-1):
                continue
            print(back)

except FileNotFoundError:
    print("User file not found.")
except socket.timeout:
    print("Connection timed out.")
except socket.error as e:
    print(f"Socket error: {e}")
finally:
    try:
        s.close()
    except:
        pass


