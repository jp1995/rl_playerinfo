from webdriver.webdriver_conf import webdriver_conf
from webdriver.updateWebdriver import updateWebdriver
from time import sleep
import json
import os


class rl_playerinfo:
    def __init__(self):
        appdata = os.getenv('APPDATA')
        self.plugDir = f'{appdata}\\bakkesmod\\bakkesmod\\data\\PlayerNames\\'
        self.mainDict = {}
        self.platformDict = {'1': 'steam', '2': 'psn', '3': 'psn', '4': 'xbl',
                             '6': 'switch', '7': 'switch', '8': 'psynet', '11': 'epic'}
        self.api_base_url = 'https://api.tracker.gg/api/v2/rocket-league/standard/profile'
        self.gen_base_url = 'https://rocketleague.tracker.network/rocket-league/profile'
        self.storage = ''

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
        print(dicty)
        for name, platform in dicty.items():
            api_url = f'{self.api_base_url}/{platform}/{name}'
            gen_url = f'{self.gen_base_url}/{platform}/{name}/overview'

            api_resp = webdriver_conf(api_url).split(';">')[1].split('</pre>')[0]
            data = json.loads(api_resp)

            print(json.dumps(data, indent=4))

            clr_name = data['data']['platformInfo']['platformUserHandle']

            # if 'Ranked Duel 1v1' in data['data']['segments'][1]:
            #     ones_tier = data['data']['segments'][1]['stats']['tier']['metadata']['name']
            #     ones_div = data['data']['segments'][1]['stats']['division']['metadata']['name']
            #     twos_tier = data['data']['segments'][2]['stats']['tier']['metadata']['name']
            #     twos_div = data['data']['segments'][2]['stats']['division']['metadata']['name']
            #     threes_tier = data['data']['segments'][3]['stats']['tier']['metadata']['name']
            #     threes_div = data['data']['segments'][3]['stats']['division']['metadata']['name']
            # else:
            #     ones_tier = data['data']['segments'][2]['stats']['tier']['metadata']['name']
            #     ones_div = data['data']['segments'][2]['stats']['division']['metadata']['name']
            #     twos_tier = data['data']['segments'][3]['stats']['tier']['metadata']['name']
            #     twos_div = data['data']['segments'][3]['stats']['division']['metadata']['name']
            #     threes_tier = data['data']['segments'][4]['stats']['tier']['metadata']['name']
            #     threes_div = data['data']['segments'][4]['stats']['division']['metadata']['name']

            ranks = []
            for i in range(0, 3):
                if 'Ranked Duel 1v1' in data['data']['segments'][i]:
                    print('drue')
                    tier = data['data']['segments'][i]['stats']['tier']['metadata']['name']
                    div = data['data']['segments'][i]['stats']['division']['metadata']['name']
                    ranks.append(f'{tier} {div}')
                else:
                    print('false')
                    tier = data['data']['segments'][i+1]['stats']['tier']['metadata']['name']
                    div = data['data']['segments'][i+1]['stats']['division']['metadata']['name']
                    ranks.append(f'{tier} {div}')




            wins = data['data']['segments'][0]['stats']['wins']['value']
            sussy = data['data']['userInfo']['isSuspicious']
            print(f'{clr_name} -- 1v1: {ranks[0]}   |   2v2: {ranks[1]}   |   '
                  f'3v3: {ranks[2]}   |   Wins: {wins}, Sussy: {sussy}, {gen_url}')

    def main(self):
        updateWebdriver()
        while True:
            stringy = self.readDatafile()
            inDatadict = self.transformData(stringy)
            if inDatadict:
                self.request(inDatadict)
            sleep(15)


if __name__ == '__main__':
    init = rl_playerinfo()
    print(init.main())



