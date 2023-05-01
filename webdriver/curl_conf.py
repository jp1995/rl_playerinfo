from urllib import parse
import subprocess
import random


def curl_conf(url, useragentarray):

    encoded_url = parse.quote(url, safe=':/')
    referer = 'https://rocketleague.tracker.network/'
    curl_command = ['webdriver/Curl/bin/curl.exe', encoded_url, '-H', f'User-Agent: {random.choice(useragentarray)}', '-H', f'Referer: {referer}']
    result = subprocess.run(curl_command, capture_output=True, text=True, encoding='utf-8')
    if '% Total' not in result.stderr:
        print(f'ERROR: {result.stderr}')
    return result.stdout
