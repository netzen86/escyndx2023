"""Send commnad to device"""
from csv import DictReader
from concurrent.futures import ThreadPoolExecutor as TE
from itertools import repeat
from netmiko import ConnectHandler as CH

def get_cred(filename):
    """get credential for connect to device"""
    result = []
    with open(filename, encoding="utf-8") as csvfile:
        reader = DictReader(csvfile)
        for row in reader:
            result.append(dict(row))
    return result


def send_command(device, show=None, conf=None):
    """send command to device"""
    cmd_output = []
    result = ''
    with CH(**device) as ssh:
        ssh.enable()
        prompt = ssh.find_prompt()
        if show:
            for cmd in show:
                out = ssh.send_command(cmd)
                cmd_output.append(f"{prompt}{cmd}\n{out}\n")
            result = "\n".join(cmd_output)
        if conf:
            result = f'{ssh.send_config_set(conf)}\n'
    return result


def run_connecting(device, filename, show=None, conf=None, limit=3):
    """run send_command() on multipul device"""
    if show and conf:
        raise ValueError("Choice one arg")
    with TE(max_workers=limit) as runner:
        result = runner.map(send_command, device, repeat(show), repeat(conf))
    with open(filename, "w", encoding="utf-8") as txt_file:
        txt_file.writelines(result)


if __name__ == "__main__":
    confs = ['snmp-server community testcom RO', 'int g0/2', 'des potr2']
    shows = ['show int des', 'show version', 'show inv']
    run_connecting(get_cred("device.csv"), "res_command.txt", show=shows)
    # run_connecting(get_cred("device.csv"), "res_command.txt", conf=confs)
