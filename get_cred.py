"""Module providingFunction printing python version."""
from csv import DictReader
from concurrent.futures import ThreadPoolExecutor as TE
from itertools import repeat
from netmiko import ConnectHandler as CH

def get_cred(filename):
    """get credential for connet to device"""
    result = []
    with open(filename, encoding="utf-8") as csvfile:
        reader = DictReader(csvfile)
        for row in reader:
            result.append(dict(row))
    return result


def send_command(device, show=None, conf=None):
    """send command to device"""
    with CH(**device) as ssh:
        ssh.enable()
        prompt = ssh.find_prompt()
        if show:
            cmd = show
            result = ssh.send_command(show)
            return f"{prompt}{cmd}\n{result}\n"
        if conf:
            result = ssh.send_config_set(conf)
            return f"{result}\n"
    # return result


def run_connecting(device, filename, *, show=None, conf=None, limit=3):
    """run multipul command to device"""
    if show and conf:
        raise ValueError("Choice one arg")
    with TE(max_workers=limit) as runner:
        result = runner.map(send_command, device, repeat(show), repeat(conf))
    with open(filename, "w", encoding="utf-8") as txt_file:
        txt_file.writelines(result)


if __name__ == "__main__":
    confs = ['router ospf 55', 'network 0.0.0.0 255.255.255.255 area 0']
    shows = "show ip int b"
    run_connecting(get_cred("device.csv"), "res_command.txt", show=shows)
