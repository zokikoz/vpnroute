import re
import sys
import ipaddress
import subprocess

codepage = 'cp866'

if __name__ == '__main__':
    if sys.argv[1:]:
        vpnip = sys.argv[1]
    else:
        # Getting VPN adapter IP address
        result = subprocess.run(['ipconfig', '/all'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = result.stdout.decode(codepage).split('\n')
        vpnif = False
        for line in lines:
            if 'VPN' in line: vpnif = True
            if 'IPv4' in line and vpnif is True:
                vpnip = re.search(r'IPv4-адрес.*:\s(\d+\.\d+\.\d+\.\d+)', line)[1]
                break

    result = subprocess.run(['netstat', '-r'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = result.stdout.decode(codepage).split('\n')
    # Removing public routes
    for line in lines:
        if re.search(vpnip, line):
            net = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+\d+', line)
            if not net: continue
            if ipaddress.ip_address(net[1]) in ipaddress.ip_network('10.0.0.0/8') or \
               ipaddress.ip_address(net[1]) in ipaddress.ip_network('172.16.0.0/12') or \
               ipaddress.ip_address(net[1]) in ipaddress.ip_network('192.168.0.0/16') or \
               ipaddress.ip_address(net[1]) in ipaddress.ip_network('127.0.0.0/8'): continue
            result = subprocess.run(['route', 'delete', net[1]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print(f"{net[1]}: {result.stdout.decode(codepage)}")
