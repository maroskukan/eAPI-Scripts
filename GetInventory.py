#!/usr/bin/env python

import ipaddress
import json
import requests
from threading import Thread, active_count
from config import read_config
import time

# Disables InsecureRequestWarning for self-signed certificates
requests.packages.urllib3.disable_warnings()

def verifyHostApi(host, apiHosts):
    '''
    :param host: IPv4 host that will be checked if it runs Web API
    :return: Does not return anything, it endpoint is enabled for API
    it will append it to global list of apiHosts. 
    '''
    try:
        request = requests.get('https://{}/explorer.html'.format(host), verify=False, timeout=3.0)
        # Only host that returns status code 200 OK is appended to apiHost list
        if request.status_code == 200:
            apiHosts.append(host)
    except (requests.Timeout, requests.ConnectionError):
            pass


def verifyNetApi(mgmtNet):
    '''
    param mgmtNet: ipaddress.ip_network object e.g 192.168.56.0/24
    return: returns a sorted list of valid IPv4 API endpoints
    '''
    # Creates a list of IP address from mgmtNet parameter
    mgmtHosts = [host for host in mgmtNet.hosts()]
    # Creates an empty apiHost list, which will be populated by verifyHostApi function
    apiHosts = []
    for host in mgmtHosts:
        t = Thread(target=verifyHostApi, args=(host, apiHosts))
        t.start()
        # Wait until the number of active threads is below 256
        while active_count() > 255:
            time.sleep(1)
    # Sort the apiHost list in ascending order and return it
    apiHosts.sort()
    return apiHosts


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



def main():
    # Loading external device credentials
    credentials = read_config(section='network-api')

    # Asks user for subnet range in CIDR format
    while True:
        try:
            devices = verifyNetApi(ipaddress.ip_network(input('Enter subnet in CIDR format: ')))
            break
        except:
            print('Enter a valid IP subnet. Try again.')
    
    if not devices:
        print('\nNo devices running eAPI found.')
    else:

        # Printing the result header
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

        # Printing the result data each line corresponds to single device

        for device in devices:
            # Devices list contains only IPv4 addresses that responded to GET Request in verifyHostApi()
            commands = ['show hostname', 'show version', 'show ip interface management1']
            # Response dicionary uses command as key and response as value
            response = {}
            for command in commands:
                response[command.replace(" ", "_")] = command_api(host=device, username=credentials['user'], password=credentials['password'], commands=[command])
            
            # Filering the interesting values from response into a result dictionary
            # result dictionary data are cleared out on every iteration of this loop
            result = {}
            result['status'] = 'OK'
            result['hostname'] = response['show_hostname']['result'][0]['hostname']
            result['modelName'] = response['show_version']['result'][0]['modelName']
            result['version'] = response['show_version']['result'][0]['version']
            result['systemMacAddress'] = response['show_version']['result'][0]['systemMacAddress']
            result['serialNumber'] = response['show_version']['result'][0]['serialNumber']
            result['architecture'] = response['show_version']['result'][0]['architecture']

            result['address'] = response['show_ip_interface_management1']['result'][0]['interfaces']['Management1']['interfaceAddress']['primaryIp']['address']

            # Formatting and printing the data
            print('{:20}{:15}{:15}{:15}{:15}{:20}{:20}{:20}'.format(
                result['hostname'], 
                result['status'], 
                result['modelName'], 
                result['version'],
                result['architecture'], 
                result['address'],
                result['systemMacAddress'],
                result['serialNumber']))


if __name__ == '__main__':
    main()
