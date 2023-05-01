from urllib import parse
import subprocess
import random
import os


def curl_conf(url, useragentarray):

    encoded_url = parse.quote(url, safe=':/')
    referer = 'https://rocketleague.tracker.network/'

    if os.path.isfile('webdriver/Curl/bin/curl.exe'):
        executable = 'webdriver/Curl/bin/curl.exe'
    else:
        executable = 'curl'

    curl_command = [executable, encoded_url, '-H', f'User-Agent: {random.choice(useragentarray)}', '-H', f'Referer: {referer}']
    result = subprocess.run(curl_command, capture_output=True, text=True, encoding='utf-8')
    if '% Total' not in result.stderr:
        print(f'ERROR: {result.stderr}')
    return result.stdout
