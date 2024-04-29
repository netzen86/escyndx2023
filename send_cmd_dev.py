"""Send commnad to device"""
from csv import DictReader
from concurrent.futures import ThreadPoolExecutor as te
from itertools import repeat
from netmiko import ConnectHandler as ch
from pprint import pprint


def get_cred(filename):
    """get credential for connect to device"""
    result = []
    with open(filename, "r", encoding="utf-8") as csvfile:
        reader = DictReader(csvfile)
        for row in reader:
            result.append(dict(row))
    return result


def send_commands(device, show=None, conf=None):
    """send command to device"""
    # result = ""
    result = {}
    # cmd_output = []
    cmd_output = {}
    with ch(**device) as connection:
        connection.enable()
        prompt = connection.find_prompt()[:-1]
        if show:
            for cmd in show:
                if isinstance(cmd, list):
                    out = connection.send_multiline(cmd)
                else:
                    out = connection.send_command(cmd)
                # cmd_output.append(f"{prompt}{cmd}\n{out}\n")
                cmd_output[cmd] = out
            # result = "\n".join(cmd_output)
            result[prompt] = cmd_output
        if conf:
            result[prompt] = f"{connection.send_config_set(conf)}"
    return result


def run_multi_connect(device, filename, show=None, conf=None, limit=3):
    """run send_command() on multipul device"""
    if show and conf:
        raise ValueError("shoice least one arg")
    with te(max_workers=limit) as runner:
        result = runner.map(send_commands, device, repeat(show), repeat(conf))
    # with open(filename, "w", encoding="utf-8") as report:
    #     report.writelines(result)

    return result


if __name__ == "__main__":
    shows = [
        "show system internal l2fwder mac"
    ]
    confs = ["hostname RouterCiscoRev2", "int gi0/2", "des test script"]
    devices = get_cred("device.csv")
    # print(get_cred("device.csv"))
    date_from_sw = run_multi_connect(
        devices,
        "report.txt",
        show=shows
    )
    # run_multi_connect(get_cred('device.csv'), 'report.txt', conf=confs)

    vlans = {}
    for date in date_from_sw:
        # iter over devices
        for dev_key in date.keys():
            vlans[dev_key] = {}
            # iter over commands
            for cmd_key in date[dev_key].keys():
                for line in date[dev_key][cmd_key].split("\n"):
                    if line:
                        if line[0] == "*":
                            if line.split()[1] not in vlans.keys():
                                vlans[dev_key][str(line.split()[1])] = 0
                            vlans[dev_key][str(line.split()[1])] += 1
    pprint(vlans)
