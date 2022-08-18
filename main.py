from webdriver.webdriver_conf import webdriver_conf
from webdriver.updateWebdriver import updateWebdriver
from db_connect import db_push_tracker_stats
from tabulate import tabulate
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

    def readNames(self):
        self.mainDict = {}
        with open(self.plugDir + "names.txt", encoding='utf-8') as f:
            lines = [line.rstrip() for line in f]

        return lines[0]

    def cleanNames(self, namesstr: str):
        if namesstr != self.storage:
            self.storage = namesstr

            self.mainDict = dict([subString.split(':') for subString in namesstr.split(',')])

            for key, value in self.mainDict.items():
                try:
                    self.mainDict[key] = self.platformDict[value]
                except KeyError:
                    print(f'Unknown platform value in dictionary: {key} - {value}')

            return self.mainDict

    def handleData(self, dicty: dict):
        headings = ['Name', '1v1', '', '2v2', '', '3v3', '', 'Wins', 'Games', 'Reward level',
                    'Influencer', 'Premium', 'Sussy', 'Country', 'url']
        table = [headings]
        dbdump = []

        for name, platform in dicty.items():
            api_url = f'{self.api_base_url}/{platform}/{name}'
            gen_url = f'{self.gen_base_url}/{platform}/{name}/overview'
            rankdict = {}
            gendict = {}
            dbdump_dict = {}
            totalprint = []

            api_resp = webdriver_conf(api_url).split(';">')[1].split('</pre>')[0]
            data = json.loads(api_resp)
            #print(json.dumps(data, indent=4))

            for i in range(0, len(data['data']['segments'])):
                for x in range(1, 4):
                    if f'{x}v{x}' in data['data']['segments'][i]['metadata']['name']:
                        tier = data['data']['segments'][i]['stats']['tier']['metadata']['name']
                        div = data['data']['segments'][i]['stats']['division']['metadata']['name']
                        rankdict[f'{x}v{x}'] = f'{tier} {div}'
                        rankdict[f'{x}v{x}_winstreak'] = data['data']['segments'][i]['stats']['winStreak']['displayValue']
                        rankdict[f'{x}v{x}_games'] = data['data']['segments'][i]['stats']['matchesPlayed']['value']

            for x in range(1, 4):
                if f'{x}v{x}' not in rankdict.keys():
                    rankdict[f'{x}v{x}'] = 'NULL'
                    rankdict[f'{x}v{x}_winstreak'] = 'NULL'
                    rankdict[f'{x}v{x}_games'] = 'NULL'

            clr_name = data['data']['platformInfo']['platformUserHandle']
            gendict['wins'] = data['data']['segments'][0]['stats']['wins']['value']
            gendict['games_this_season'] = rankdict['1v1_games'] + rankdict['2v2_games'] + rankdict['3v3_games']
            gendict['rewardlevel'] = data['data']['segments'][0]['stats']['seasonRewardLevel']['metadata']['rankName']
            gendict['influencer'] = data['data']['userInfo']['isInfluencer']
            gendict['premium'] = data['data']['userInfo']['isPremium']
            gendict['sussy'] = data['data']['userInfo']['isSuspicious']
            gendict['country'] = data['data']['userInfo']['countryCode']
            gendict['url'] = gen_url

            sorted_rankdict = {k: v for k, v in sorted(rankdict.items())}
            #print(sorted_rankdict)

            dbdump_dict['name'] = clr_name
            dbdump_dict['platform'] = platform
            for key, value in sorted_rankdict.items():
                dbdump_dict[key] = value
            for key, value in gendict.items():
                dbdump_dict[key] = value

            totalprint.append(clr_name)
            for key, value in sorted_rankdict.items():
                if key in ['1v1', '1v1_winstreak', '2v2', '2v2_winstreak', '3v3', '3v3_winstreak']:
                    totalprint.append(f'{rankdict[key]}')
            for key, value in gendict.items():
                totalprint.append(gendict[key])

            table.append(totalprint)
            dbdump.append(dbdump_dict)

        print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
        push = db_push_tracker_stats(dbdump)
        if all(push):
            print('Succesful push')


        #return [dbdump]

    def main(self):
        updateWebdriver()
        while True:
            stringy = self.readNames()
            inDatadict = self.cleanNames(stringy)
            if inDatadict:
                self.handleData(inDatadict)
            sleep(15)


if __name__ == '__main__':
    init = rl_playerinfo()
    print(init.main())
