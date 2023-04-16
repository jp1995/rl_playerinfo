from selenium import webdriver
import requests
import shutil
import os
import re


def chromedriver_getversion():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options, executable_path=r'webdriver/chromedriver.exe')

    bVersion = driver.capabilities['browserVersion'].split('.')[0]
    dVersion = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0].split('.')[0]
    driver.quit()
    if bVersion != dVersion:
        print(f'Major version mismatch\n'
              f'Chromedriver version {dVersion}\n'
              f'Chrome version {bVersion}\n')
        return [False, bVersion]
    else:
        return [True]


def updateChromedriver():
    checkv = chromedriver_getversion()
    url = 'https://chromedriver.chromium.org/downloads'
    zipurl = 'https://chromedriver.storage.googleapis.com/'
    zipname = 'chromedriver_win32.zip'

    if not checkv[0]:
        print('Attempting to update webdriver')
        resp = requests.get(url)
        findurl = re.findall(rf"ChromeDriver {checkv[1]}.+?(?=</a>|</strong>)", resp.text)

        if len(findurl) > 0:
            dlver = findurl[0].split(' ')[1].split('</span')[0]
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
            os.remove('webdriver/LICENSE.chromedriver')
            print('Webdriver update successful!')
            updateChromedriver()
    else:
        return
