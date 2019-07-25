#!/usr/bin/env python

import json
import requests

# Disables InsecureRequestWarning for self-signed certificates
requests.packages.urllib3.disable_warnings()

def command_api(host, username, password, commands, action='process'):
    ''' 
    :param host: IPv4 address of API endpoint
    :param username: API account username
    :param password: API account password
    :param commands: CLI commands enclosed in brackets ['cmd1', 'cmd2']
    :return: By default returns response in dictionary or can return string
    in human readable format 
    '''
    # Composes full URI and session parameters
    uri = 'https://{}/command-api'.format(host)
    session = requests.session()
    session.auth = (username, password)
    session.verify = False
    
    # Creates payload
    payload = {
        'jsonrpc': '2.0',
        'method': 'runCmds',
        'params': {
            'format': 'json',
            'timestamps': False,
            'autoComplete': True,
            'cmds': [
                ''
                ],
            'version': 1
            },
        'id': 'CaptainApi'
        }
    payload['params']['cmds'] = commands

    # Converts the paylod with json and saves return values 
    response = session.request('post', uri, data=json.dumps(payload))
    
    # Provides an option to switch the default action
    if action == 'display':
        # Returns a human readable string of data
        return json.dumps(response.json(), indent=3)
    if action == 'process':
        # Returns a dictionary for further processing
        return json.loads(response.text)


devices = ['192.168.56.101', '192.168.56.102', '192.168.56.103']

print('{:20}{:15}{:15}{:15}{:15}{:20}{:20}{:20}'.format(
    'Hostname', 
    'Status', 
    'Model', 
    'Software',
    'Architecture', 
    'IP Address',
    'MAC Address',
    'Serial Number'))
print('-'*135)



for device in devices:

    show_hostname = command_api(host=device, username='api', password='api', commands=['show hostname'])
    show_version = command_api(host=device, username='api', password='api', commands=['show version'])
    show_ip_int_mgmt = command_api(host=device, username='api', password='api', commands=['show ip interface management1'])


    result = {}
    result['status'] = 'OK'

    result['hostname'] = show_hostname['result'][0]['hostname']

    result['modelName'] = show_version['result'][0]['modelName']
    result['version'] = show_version['result'][0]['version']
    result['systemMacAddress'] = show_version['result'][0]['systemMacAddress']
    result['serialNumber'] = show_version['result'][0]['serialNumber']
    result['architecture'] = show_version['result'][0]['architecture']

    result['address'] = show_ip_int_mgmt['result'][0]['interfaces']['Management1']['interfaceAddress']['primaryIp']['address']

    print('{:20}{:15}{:15}{:15}{:15}{:20}{:20}{:20}'.format(
        result['hostname'], 
        result['status'], 
        result['modelName'], 
        result['version'],
        result['architecture'], 
        result['address'],
        result['systemMacAddress'],
        result['serialNumber']))


