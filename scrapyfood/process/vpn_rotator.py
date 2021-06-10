import time
import subprocess


vpn_servers = ['sg455',
               'sg456',
               'sg457',
               'sg458',
               'sg459',
               'sg460',
               'sg461',
               'sg462',
               'sg463',
               'sg464',
               'sg465',
               'sg466',
               'sg467',
               'sg468',
               'sg469',
               'sg470',
               'sg471',
               'sg472',
               'sg473',
               'sg474',
               'sg475',
               'sg476',
               'sg477',
               'sg478',
               'sg479',
               'sg480',
               'sg481',
               'sg482',
               'sg483',
               'sg484',
               'sg485',
               'sg486',
               'sg487',
               'sg488',
               'sg489',
               'sg490',
               'sg491',
               'sg492',
               'sg493',
               'sg494',
               'sg495',
               'sg496',
               'sg497',
               'sg498',
               'sg499',
               'sg500',
               'sg501',
               'sg502',
               'sg503',
               'sg504',
               'sg505',
               'sg506',
               'sg507',
               'sg508']


vpn_process = subprocess.Popen(
    ['openpyn', '-s', vpn_servers[0]], stdin=subprocess.PIPE)

while True:
    for server in vpn_servers:
        time.sleep(200)
        vpn_process.kill()
        vpn_process = subprocess.Popen(
            ['openpyn', '-s', server], stdin=subprocess.PIPE)
