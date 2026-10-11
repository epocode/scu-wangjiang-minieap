"""GPL-3.0: privately generate a config with an exact GBK service name."""
import argparse
import getpass
import os
from pathlib import Path
import re

SERVICE = bytes.fromhex('b5e7d0c5b3f6bfda')


def credential(value):
    if not value or value != value.strip() or any(c in value for c in '\r\n\0'):
        raise ValueError('Credentials cannot be empty, multiline, or have surrounding whitespace.')
    return value.encode('utf-8')


def build_config(username, password, nic, wan_interface):
    for value in (nic, wan_interface):
        if not re.fullmatch(r'[A-Za-z0-9_.:-]+', value):
            raise ValueError('Invalid network interface name.')
    lines = [b'username=' + credential(username), b'password=' + credential(password)]
    settings = {
        'nic': nic,
        'module': 'rjv3',
        'if-impl': 'sockraw',
        'eap-bcast-addr': '1',
        'heartbeat': '60',
        'dhcp-type': '2',
        'dhcp-script': f'/usr/libexec/scu-dhcp-renew.sh {wan_interface}',
        'stage-timeout': '5',
        'version-str': 'RG-SU For Linux V1.30',
        'max-retries': '4',
        'max-fail': '3',
        'wait-after-fail': '30',
        'daemonize': '0',
        'pid-file': '/var/run/minieap-scu.pid',
    }
    lines += [f'{key}={value}'.encode('ascii') for key, value in settings.items()]
    lines.append(b'service=' + SERVICE)
    return b'\n'.join(lines) + b'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nic', default='eth0')
    parser.add_argument('--wan-interface', default='wan')
    args = parser.parse_args()
    private = Path(__file__).resolve().parents[1] / 'local'
    output = private / 'minieap-scu.conf'
    if output.exists():
        parser.error('Private config already exists. Move it aside to preserve your credentials.')
    username = input('School account / student ID: ')
    password = getpass.getpass('School authentication password: ')
    if password != getpass.getpass('Repeat password: '):
        parser.error('Passwords differ. No config written.')
    try:
        data = build_config(username, password, args.nic, args.wan_interface)
    except ValueError as exc:
        parser.error(str(exc))
    private.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
    print(f'Created private config: {output}')
    print('Keep this file private. It is ignored by Git; router install sets mode 600.')


if __name__ == '__main__':
    main()
