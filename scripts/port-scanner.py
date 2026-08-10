import socket
import pyfiglet
import sys

ascii_banner = pyfiglet.figlet_format("PORT SCANNER")
print(ascii_banner)

def scan_port(ip, port):
    #Attempts to connect to a given port on a specified IP address. Prints if the port is open or handles common errors.
    try:
        sock = socket.socket()
        sock.settimeout(1)  # Set a timeout for the connection attempt
        sock.connect((ip, port))
        print(f"[+] Port {port} is open") # Notify if the port is open
        sock.close()
    except KeyboardInterrupt:
        print("\nTerminating Program !!!")
        sys.exit()
    except socket.gaierror:
        print("\nHostname Could Not Be Resolved !!!")
        sys.exit()
    except socket.error:
        #port is closed or unreachable.
        pass

target = input("Enter IP address to scan: ")

print("Loading....")

for port in range(1, 1025):
    scan_port(target, port)

print("Scan complete.")