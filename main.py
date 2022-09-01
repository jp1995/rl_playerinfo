from webdriver.updateWebdriver import updateWebdriver
from threaded_requests import threaded_requests
from db_connect import db_push_tracker_stats
from web.formatTable import formatTable
from tabulate import tabulate
from time import sleep
import subprocess
import atexit
import socket
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
        self.webserver = subprocess.Popen("python app.py", cwd='./web/', shell=True)
        self.api_resps = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def wipeNames(self):
        with open(self.plugDir + 'names.txt', 'w'):
            pass
        with open('web/table_base.html', 'r', encoding='utf-8') as tb:
            with open('web/table.html', 'w', encoding='utf-8') as t:
                base = tb.read()
                t.write(base)

    def readNames(self):
        self.mainDict = {}
        with open(self.plugDir + "names.txt", encoding='utf-8') as f:
            lines = [line.rstrip() for line in f]

        try:
            return lines[0]
        except IndexError:
            return ''

    def checkIfNewNames(self):
        strjson = self.readNames()

        if strjson != self.storage:
            self.storage = strjson

            return strjson

    @staticmethod
    def notFound():
        with open('web/not_found.json', 'r', encoding='utf-8') as f:
            json = f.read()
        return json

    def responses_check(self, resps: list):
        for item in resps:
            try:
                data = json.loads(item)
            except json.decoder.JSONDecodeError:
                print('Tracker network appears down')
                continue
            if 'data' not in data:
                print(f"Something broke.\nPossibly hit a smurf so new the API doesn't even know about them")
                data = json.loads(self.notFound())

            self.api_resps.append(data)

    def responses_mod(self, resps: list, strjson: str):
        legit = []
        gamedata = json.loads(strjson)

        self.responses_check(resps)

        for item in self.api_resps:
            uid = item['data']['platformInfo']['platformUserIdentifier']
            item['data']['gameInfo'] = {}
            item['data']['gameInfo']['maxPlayers'] = gamedata['Match']['maxPlayers']
            try:
                item['data']['gameInfo']['team'] = gamedata['Match']['players'][uid]['team']
                legit.append(uid)
            except KeyError:
                item['data']['gameInfo']['team'] = 0

        for player in gamedata['Match']['players']:
            for item in self.api_resps:
                handle = item['data']['platformInfo']['platformUserHandle']
                if player not in legit and handle == 'Player not found':
                    item['data']['platformInfo']['platformUserIdentifier'] = player
                    item['data']['platformInfo']['platformUserHandle'] = player + ' - No API response'
                    item['data']['platformInfo']['platformSlug'] = self.platformDict[str(gamedata['Match']['players'][player]['platform'])]

    def requests(self, strjson):
        urls = []

        gamedata = json.loads(strjson)
        for player in gamedata['Match']['players']:
            name = player
            platform_num = str(gamedata['Match']['players'][name]['platform'])
            platform = self.platformDict[platform_num]
            api_url = f'{self.api_base_url}/{platform}/{name}'
            urls.append(api_url)

        resps = threaded_requests(urls, len(urls))
        self.responses_mod(resps, strjson)

    @staticmethod
    def rankDict(resp: dict):
        rankdict = {}

        for i in range(0, len(resp['data']['segments'])):
            for x in range(1, 4):
                if f'{x}v{x}' in resp['data']['segments'][i]['metadata']['name']:
                    tier = resp['data']['segments'][i]['stats']['tier']['metadata']['name']
                    div = resp['data']['segments'][i]['stats']['division']['metadata']['name']
                    if div == 'NULL':
                        div = 'I'

                    rankdict[f'{x}v{x}'] = f'{tier} {div}'
                    rankdict[f'{x}v{x}_winstreak'] = int(resp['data']['segments'][i]['stats']['winStreak']['displayValue'])
                    rankdict[f'{x}v{x}_games'] = int(resp['data']['segments'][i]['stats']['matchesPlayed']['value'])

        for x in range(1, 4):
            if f'{x}v{x}' not in rankdict.keys():
                rankdict[f'{x}v{x}'] = 'NULL'
                rankdict[f'{x}v{x}_winstreak'] = 0
                rankdict[f'{x}v{x}_games'] = 0

        sorted_rankdict = {k: v for k, v in sorted(rankdict.items())}
        return sorted_rankdict

    @staticmethod
    def hideSpecCols(table: list):
        infl = []
        prem = []
        suss = []
        for row in table[1:]:
            infl.append(row[7])
            prem.append(row[8])
            suss.append(row[9])

        if 'True' not in infl:
            idx = table[0].index('Influencer')
            [row.pop(idx) for row in table]
        if 'True' not in prem:
            idx = table[0].index('Premium')
            [row.pop(idx) for row in table]
        if 'True' not in suss:
            idx = table[0].index('Sussy')
            [row.pop(idx) for row in table]

        return table

    @staticmethod
    def sortPlayersByTeams(table: list):
        stable = sorted(table[1:], key=lambda x: int(x[-1]))
        for item in stable:
            del item[-1]
        sorted_table = [table[0]] + stable

        return sorted_table

    @staticmethod
    def writeTable(listy: list):
        with open('web/table.html', 'w', encoding='utf-8') as f:
            f.write("{% extends 'index.html' %}\n{% block head %}\n{% endblock %}\n{% block body %}\n")
            f.write(tabulate(listy, headers='firstrow', tablefmt='unsafehtml', colalign='center', numalign='center'))
            f.write("\n{% endblock %}")
        print('Table generated')

    def handleDBdata(self, api_resps: list):
        dbdump = []
        for resp in api_resps:
            dbdump_dict = {}
            uid = resp['data']['platformInfo']['platformUserIdentifier']
            platform = resp['data']['platformInfo']['platformSlug']
            gen_url = f'{self.gen_base_url}/{platform}/{uid}/overview'

            dbdump_dict['name'] = resp['data']['platformInfo']['platformUserHandle']
            dbdump_dict['platform'] = resp['data']['platformInfo']['platformSlug']

            rankdict = self.rankDict(resp)
            for key, value in rankdict.items():
                dbdump_dict[key] = value

            dbdump_dict['wins'] = resp['data']['segments'][0]['stats']['wins']['value']
            dbdump_dict['games_this_season'] = rankdict['1v1_games'] + rankdict['2v2_games'] + rankdict['3v3_games']
            dbdump_dict['rewardlevel'] = resp['data']['segments'][0]['stats']['seasonRewardLevel']['metadata'][
                'rankName']
            if dbdump_dict['rewardlevel'] == 'None':
                dbdump_dict['rewardlevel'] = 'NULL'
            dbdump_dict['influencer'] = resp['data']['userInfo']['isInfluencer']
            dbdump_dict['premium'] = resp['data']['userInfo']['isPremium']
            dbdump_dict['sussy'] = str(resp['data']['userInfo']['isSuspicious']).replace('None', 'False')
            dbdump_dict['country'] = str(resp['data']['userInfo']['countryCode'])
            dbdump_dict['url'] = gen_url

            dbdump.append(dbdump_dict)

        db_push_tracker_stats(dbdump)
        print('Successful push')

    def handleData(self, api_resps: list):
        table = [['Name', '1v1', '2v2', '3v3', 'Wins',
                  '<p title="Competitive games this season">Games <sup>*</sup></p>',
                 'Reward level', 'Influencer', 'Premium', 'Sussy', 'Country', 'Platform']]

        for resp in api_resps:
            uid = resp['data']['platformInfo']['platformUserIdentifier']
            platform = resp['data']['platformInfo']['platformSlug']
            gen_url = f'{self.gen_base_url}/{platform}/{uid}/overview'
            totalprint = []

            rankdict = self.rankDict(resp)
            # print(json.dumps(resp, indent=4))
            # quit()
            totalprint.append(resp['data']['platformInfo']['platformUserHandle'])
            for key, value in rankdict.items():
                if key not in ['1v1_games', '2v2_games', '3v3_games']:
                    totalprint.append(f'{rankdict[key]}')
            totalprint.append(resp['data']['segments'][0]['stats']['wins']['value'])
            totalprint.append(rankdict['1v1_games'] + rankdict['2v2_games'] + rankdict['3v3_games'])
            rewardlevel = resp['data']['segments'][0]['stats']['seasonRewardLevel']['metadata']['rankName']
            if rewardlevel == 'None':
                rewardlevel = 'NULL RR'
            totalprint.append(rewardlevel)
            totalprint.append(resp['data']['userInfo']['isInfluencer'])
            totalprint.append(resp['data']['userInfo']['isPremium'])
            totalprint.append(str(resp['data']['userInfo']['isSuspicious']).replace('None', 'False'))
            totalprint.append(str(resp['data']['userInfo']['countryCode']))
            totalprint.append(resp['data']['platformInfo']['platformSlug'])
            totalprint.append(resp['data']['gameInfo']['team'])
            totalprint.append(gen_url)

            formatted = formatTable(totalprint)
            table.append(formatted)

        table = self.hideSpecCols(table)
        sorted_table = self.sortPlayersByTeams(table)

        self.writeTable(sorted_table)

    def handleExit(self):
        print('Closing webserver gracefully')
        self.webserver.kill()

    def main(self):
        updateWebdriver()
        self.wipeNames()
        atexit.register(self.handleExit)
        while True:
            self.api_resps.clear()
            strjson = self.checkIfNewNames()
            if strjson:
                self.requests(strjson)
                # If you want database functionality, uncomment and setup your own db + edit db_connect.py
                # self.handleDBdata(self.api_resps)
                self.handleData(self.api_resps)
            sleep(15)


if __name__ == '__main__':
    init = rl_playerinfo()
    print(init.main())
