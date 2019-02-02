import sys
if not sys.version_info >= (3, 6):
    sys.exit('Python 3.6 or greater required.')

import argparse
import json

from lab_base import vagrant
from lab_base import provision


def main():
    parser = argparse.ArgumentParser(description='Lab Base Provisioning')
    parser.add_argument('--ssh-config', default=False, action='store_true',
                        dest='ssh_config', help='Gather Vagrant SSH config')
    parser.add_argument('--provision', nargs='+', help='Apply config to devices')
    args = parser.parse_args()

    if args.ssh_config:
        print('Gathering vagrant SSH config')
        guests = vagrant.get_guests()
        ssh_config_dict = vagrant.worker(guests)
        with open('.sshconfig', 'w') as f:
            f.write('\n'.join(vagrant.ssh_config_to_list(ssh_config_dict)))
        with open('.sshconfig.json', 'w') as f:
            f.write(json.dumps(ssh_config_dict))
        print(f'SSH config saved to file ".sshconfig and .sshconfig.json"')

    if args.provision:
        print('Applying config to devices')
        print(args.provision)
        # provision.worker(args.provision)
