from webdriver.webdriver_conf import webdriver_getversion
import requests
import shutil
import os
import re


def updateWebdriver():
    checkv = webdriver_getversion()
    url = 'https://chromedriver.chromium.org/downloads'
    zipurl = 'https://chromedriver.storage.googleapis.com/'
    zipname = 'chromedriver_win32.zip'

    if not checkv[0]:
        print('Attempting to update webdriver')
        resp = requests.get(url)
        findurl = re.findall(rf"ChromeDriver {checkv[1]}.+?(?=</a>|</strong>)", resp.text)

        if len(findurl) > 0:
            dlver = findurl[0].split(' ')[1]
            zipurl += f'{dlver}/{zipname}'
            dlzip = requests.get(zipurl)

            with open(f'webdriver/{zipname}', 'wb') as out_file:
                out_file.write(dlzip.content)
            print(f'Downloaded new webdriver, version {dlver}, unpacking...')
            os.rename('webdriver/chromedriver.exe', 'webdriver/chromedriver_old.exe')

            shutil.unpack_archive(f'webdriver/{zipname}', 'webdriver')
            print('Cleaning up...')
            os.remove(f'webdriver/{zipname}')
            os.remove('webdriver/chromedriver_old.exe')
            print('Webdriver update successful!')
            updateWebdriver()
    else:
        return
