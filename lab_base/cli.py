import sys
import argparse
import json

from nornir.plugins.tasks import networking, text, files
from nornir.plugins.functions.text import print_title, print_result
from nornir.core.filter import F

from lab_base import vagrant
from lab_base import provision
from lab_base import init_nornir
from lab_base import generate_base_config
from lab_base import utils

if not sys.version_info >= (3, 6):
    sys.exit('Python 3.6 or greater required.')


def config_device(task, config_type="base", replace_config=False):
    # Load in configuration files
    r = task.run(task=text.template_file,
                 name=f"{config_type} Configuration".upper(),
                 template=f"{task.host}-{task.host['model']}.cfg",
                 path=f"config/{config_type}")

    # Save the compiled configuration into a host variable
    task.host["config"] = r.result

    # Deploy that configuration to the device using NAPALM
    task.run(task=networking.napalm_configure,
             name="Loading Configuration on the device",
             replace=replace_config,
             configuration=task.host["config"])


def validate_devices(devices, ssh_config):
    for dev in devices:
        if dev not in ssh_config:
            sys.exit(f'Device: {dev} either not configured or up.')


def main():
    parser = argparse.ArgumentParser(description='Lab Base Provisioning')
    parser.add_argument('--device-config', default=False, action='store_true',
                        dest='device_config', help='Generate device config')
    parser.add_argument('--ssh-config', default=False, action='store_true',
                        dest='ssh_config', help='Gather Vagrant SSH config')
    parser.add_argument('--apply-config',
                        dest='apply_config', help='Apply a config to devices')
    parser.add_argument('--reload-baseline', nargs='+',
                        dest='reload_baseline', help='Reload baseline config')
    args = parser.parse_args()

    if args.device_config:
        print('Generating device config.')
        generate_base_config.make_config()
        print('Config saved to "./config" directory.')

    if args.ssh_config:
        print('Gathering vagrant SSH config')
        guests = vagrant.get_guests()
        ssh_config_dict = vagrant.worker(guests)
        with open('.sshconfig', 'w') as f:
            f.write('\n'.join(vagrant.ssh_config_to_list(ssh_config_dict)))
        with open('.sshconfig.json', 'w') as f:
            f.write(json.dumps(ssh_config_dict))
        print(f'SSH config saved to files ".sshconfig and .sshconfig.json"')

    if args.apply_config:
        print('Applying config to devices.')
        nr = init_nornir.init_nornir()
        devices = nr.filter(F(groups__contains=args.apply_config))
        result = devices.run(task=config_device, config_type=args.apply_config, replace_config=False)
        print_result(result)
        print('Config applied to devices.')

    if args.reload_baseline:
        ssh_config = utils.load_json_file('.ssh_config.json')
        validate_devices(args.reload_baseline, ssh_config)
        print('Reloading device baselines.')
        provision.worker(args.reload_baseline, 'reload_baseline')
        print('Baseline applied to devices.')
