import os
import re
import requests
import shutil
from time import sleep
from bs4 import BeautifulSoup
from webdriver.webdriver_conf import webdriver_conf, webdriver_update


class liveRLdata:
    def __init__(self):
        appdata = os.getenv('APPDATA')
        self.plugDir = f'{appdata}\\bakkesmod\\bakkesmod\\data\\PlayerNames\\'
        self.mainDict = {}
        self.platformDict = {'1': 'steam', '2': 'psn', '3': 'psn', '4': 'xbl',
                             '6': 'switch', '7': 'switch', '8': 'psynet', '11': 'epic'}
        self.base_url = 'https://rocketleague.tracker.network/rocket-league/profile'
        self.storage = ''

    def updateWebdriver(self):
        checkv = webdriver_update()
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
                sleep(15)
                os.rename('webdriver/chromedriver.exe', 'webdriver/chromedriver_old.exe')

                shutil.unpack_archive(f'webdriver/{zipname}', 'webdriver')
                print('Cleaning up...')
                os.remove(f'webdriver/{zipname}')
                os.remove('webdriver/chromedriver_old.exe')
                print('Webdriver update successful!')
                self.updateWebdriver()
        else:
            return

    def readDatafile(self):
        self.mainDict = {}
        with open(self.plugDir+"names.txt", encoding='utf-8') as f:
            lines = [line.rstrip() for line in f]

        return lines[0]

    def transformData(self, namesstr: str):
        if namesstr != self.storage:
            self.storage = namesstr

            self.mainDict = dict([subString.split(':') for subString in namesstr.split(',')])

            for key, value in self.mainDict.items():
                try:
                    self.mainDict[key] = self.platformDict[value]
                except KeyError:
                    print(f'Unknown platform value in dictionary: {key} - {value}')

            return self.mainDict

    def request(self, dicty: dict):
        for name, platform in dicty.items():
            url = f'{self.base_url}/{platform}/{name}/overview'
            resp = requests.get(url, timeout=None)
            print(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            print(soup.body.get_text().strip())

    def main(self):
        self.updateWebdriver()
        while True:
            stringy = self.readDatafile()
            inDatadict = self.transformData(stringy)
            if inDatadict:
                print(inDatadict)
                # self.request(inDatadict)


if __name__ == '__main__':
    test = liveRLdata()
    while True:
        print(test.main())
        sleep(15)


