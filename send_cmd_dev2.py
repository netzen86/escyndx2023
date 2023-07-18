from csv import DictReader
from concurrent.futures import ThreadPoolExecutor as te
from itertools import repeat
from netmiko import ConnectHandler as ch


def get_cred(filename):
    result = []
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = DictReader(csvfile)
        for row in reader:
            result.append(dict(row))
    return result


def send_commands(device, show=None, conf=None):
    result = ''
    cmd_output = []
    with ch(**device) as connection:
        connection.enable()
        if show:
            prompt = connection.find_prompt()
            for cmd in show:
                if isinstance(cmd, list):
                    cmd_output.append(connection.send_multiline(cmd))
                else:
                    out = connection.send_command(cmd)
                    cmd_output.append(f'{prompt}{cmd}\n{out}\n')
            result = '\n'.join(cmd_output)
        if conf:
            result = f'{connection.send_config_set(conf)}'
    return result


def run_multi_connect(device, filename, show=None, conf=None, limit=3):
    if show and conf:
        raise ValueError('shoice least one arg')
    with te(max_workers=limit) as runner:
        result = runner.map(send_commands, device, repeat(show), repeat(conf))
    with open(filename, 'w', encoding='utf-8') as report:
        report.writelines(result)


if __name__ == '__main__':
    shows = ['show ver', 'show ip int b', 'show inv', [['copy scp://netzen:nihilant@10.0.0.58/test.log flash://test.log', r"]?"], ['\n', '']], 'show snmp mib ifmib ifindex gi 0/1']
    confs = ['hostname RouterCiscoRev2', 'int gi0/2', 'des test script']
    run_multi_connect(get_cred('device.csv'), 'report.txt', show=shows)
    # run_multi_connect(get_cred('device.csv'), 'report.txt', conf=confs)
