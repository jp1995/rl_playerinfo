from webdriver.updateWebdriver import updateChromedriver
from webdriver.webdriver_conf import is_chrome_installed
from threaded_requests import threaded_requests
from db_connect import db_push_tracker_stats
from multiprocessing import Process, Queue
from web.formatTable import formatTable
from TCPserver import run_tcp_server
from tabulate import tabulate
from time import sleep
import subprocess
import atexit
import json
import os


class rl_playerinfo:
    def __init__(self):
        appdata = os.getenv('APPDATA')
        self.plugDir = f'{appdata}\\bakkesmod\\bakkesmod\\data\\MatchDataScraper\\'
        self.platformDict = {'0': 'unknown', '1': 'steam', '2': 'psn', '3': 'psn', '4': 'xbl',
                             '6': 'switch', '7': 'switch', '8': 'psynet', '11': 'epic'}
        self.playlistIDs = {'0': 'Casual', '1': 'Casual Duel', '2': 'Casual Doubles', '3': 'Casual Standard',
                            '4': 'Casual 4v4', '6': 'Private Match', '9': 'Flip Reset training', '10': 'Duel',
                            '11': 'Doubles', '13': 'Standard', '27': 'Hoops',
                            '28': 'Rumble', '29': 'Dropshot', '30': 'Snowday', '22': 'Tournament', '69': 'Main Menu'}
        self.soc_base_urls = {'twitch': 'https://twitch.tv/', 'reddit': 'https://www.reddit.com/user/',
                              'twitter': 'https://twitter.com/'}
        self.api_base_url = 'https://api.tracker.gg/api/v2/rocket-league/standard/profile'
        self.gen_base_url = 'https://rocketleague.tracker.network/rocket-league/profile'
        self.webserver = subprocess.Popen("python app.py", cwd='./web/', shell=True)
        self.matchStorage = {}
        self.playlistStorage = '69'
        self.matchCurrent = {}
        self.playlistCurrent = '69'
        self.mmrCurrent = {}
        self.api_resps = []

        self.q = Queue()
        self.tcp_process = Process(target=run_tcp_server, args=(self.q,))
        self.tcp_process.start()

    def sort(self):
        if not self.q.empty():
            data = self.q.get()
            print(f'Received: {data}')
            try:
                jdata = json.loads(data)
                if 'Match' in jdata.keys():
                    self.matchCurrent = jdata
                elif 'Playlist' in jdata.keys():
                    self.playlistCurrent = str(jdata['Playlist'])
                elif list(jdata.keys())[0].isnumeric():
                    self.mmrCurrent = jdata
                    self.writeMMR()
            except ValueError:
                return None

    @staticmethod
    def createEmptyTable():
        with open('web/table_base.html', 'r', encoding='utf-8') as tb:
            with open('web/table.html', 'w', encoding='utf-8') as t:
                base = tb.read()
                t.write(base)
        with open('web/mmr.txt', 'w') as create:
            pass

    def checkIfNewmatch(self):
        if self.matchCurrent != self.matchStorage:
            self.matchStorage = self.matchCurrent

            return self.matchCurrent

    def checkIfNewPlaylist(self):
        if self.playlistCurrent != self.playlistStorage:
            self.playlistStorage = self.playlistCurrent

            self.writePlaylist()

    def writeMMR(self):
        with open('web/mmr.txt', 'w+', encoding='utf-8') as f:
            now = f.readline()
            if now != self.mmrCurrent:
                f.write(json.dumps(self.mmrCurrent))

    @staticmethod
    def notFound(errorType: str):
        if errorType == 'API_down':
            with open('web/assets/API_down.json', 'r', encoding='utf-8') as f:
                json = f.read()
        elif errorType == 'API_error':
            with open('web/assets/API_error.json', 'r', encoding='utf-8') as f:
                json = f.read()
        elif errorType == 'AI':
            with open('web/assets/bot.json', 'r', encoding='utf-8') as f:
                json = f.read()
        elif errorType == 'API_unknown':
            with open('web/assets/API_unknown.json', 'r', encoding='utf-8') as f:
                json = f.read()
        return json

    @staticmethod
    def isBot(team: int):
        with open('web/assets/bot.json', 'r', encoding='utf-8') as f:
            j = f.read()
            jsonstr = json.loads(j)
            jsonstr['data']['gameInfo']['team'] == team
            jd = json.dumps(jsonstr)
        return jd

    def responses_check(self, resps: list):
        for item in resps:
            print(item)
            try:
                data = json.loads(item)
            except json.decoder.JSONDecodeError:
                print('Tracker network appears down')
                data = json.loads(self.notFound('API_down'))
                self.api_resps.append(data)
                continue
            if 'errors' in list(data.keys()):
                if 'unhandled exception' in data['errors'][0]['message']:
                    data = json.loads(self.notFound('API_error'))
                    print('API: An unhandled exception has occured in the system')
                elif 'platform is invalid' in data['errors'][0]['message']:
                    data = json.loads(self.notFound('AI'))
                    print('API: Player is likely AI')
                elif 'We could not find the player' in data['errors'][0]['message']:
                    data = json.loads(self.notFound('API_unknown'))
                    print('API: Player is likely very new')

            self.api_resps.append(data)

    def responses_mod(self, resps: list, matchData: dict):
        legit = []
        self.responses_check(resps)

        for item in self.api_resps:
            uid = item['data']['platformInfo']['platformUserIdentifier']
            item['data']['gameInfo'] = {}
            item['data']['gameInfo']['maxPlayers'] = matchData['Match']['maxPlayers']
            try:
                item['data']['gameInfo']['team'] = matchData['Match']['players'][uid]['team']
                legit.append(uid)
            except KeyError:
                pass

        for player in matchData['Match']['players']:
            for item in self.api_resps:
                handle = item['data']['platformInfo']['platformUserHandle']
                if player not in legit:
                    if handle == 'API: Server Error':
                        item['data']['platformInfo']['platformUserIdentifier'] = player
                        item['data']['platformInfo']['platformUserHandle'] = player + ' - API Server Error'
                        item['data']['gameInfo']['team'] = matchData['Match']['players'][player]['team']
                        item['data']['platformInfo']['platformSlug'] = self.platformDict[
                            str(matchData['Match']['players'][player]['platform'])]
                        break
                    elif handle == 'API: No Response':
                        item['data']['platformInfo']['platformUserIdentifier'] = player
                        item['data']['platformInfo']['platformUserHandle'] = player + ' - No API response'
                        item['data']['gameInfo']['team'] = matchData['Match']['players'][player]['team']
                        item['data']['platformInfo']['platformSlug'] = self.platformDict[
                            str(matchData['Match']['players'][player]['platform'])]
                        break
                    elif handle == 'API: Unknown player':
                        item['data']['platformInfo']['platformUserIdentifier'] = player
                        item['data']['platformInfo']['platformUserHandle'] = player + ' - Unknown to API'
                        item['data']['gameInfo']['team'] = matchData['Match']['players'][player]['team']
                        item['data']['platformInfo']['platformSlug'] = self.platformDict[
                            str(matchData['Match']['players'][player]['platform'])]
                        break
                    elif handle == 'AI':
                        item['data']['platformInfo']['platformUserIdentifier'] = player
                        item['data']['platformInfo']['platformUserHandle'] = player + ' - AI'
                        item['data']['gameInfo']['team'] = matchData['Match']['players'][player]['team']
                        item['data']['platformInfo']['platformSlug'] = self.platformDict[
                            str(matchData['Match']['players'][player]['platform'])]
                        break
                else:
                    break
            else:
                break

    def requests(self, matchData):
        urls = []
        bots = []

        for player in matchData['Match']['players']:
            platform_num = str(matchData['Match']['players'][player]['platform'])
            if platform_num == '0':
                team = matchData['Match']['players'][player]['team']
                bot = self.isBot(team)
                print(f'Bot {player} found, placed in team {team}')
                bots.append(bot)
                continue

            platform = self.platformDict[platform_num]
            api_url = f'{self.api_base_url}/{platform}/{player}'
            urls.append(api_url)
        print(urls)
        resps = threaded_requests(urls, len(urls))
        for i in bots:
            resps.append(i)

        self.responses_mod(resps, matchData)

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
    def sortPlayersByTeams(table: list):
        stable = sorted(table[1:], key=lambda x: int(x[-1]))
        for item in stable:
            del item[-1]
        sorted_table = [table[0]] + stable

        return sorted_table

    def getSocialURLs(self, listy: list):
        outl = []
        if listy:
            if len(listy) > 0:
                for d in listy:
                    if d['platformSlug'] in list(self.soc_base_urls.keys()):
                        url = self.soc_base_urls[d['platformSlug']]+d['platformUserHandle']
                        outl.append(url)
                return outl
            else:
                return ['-']
        else:
            return ['-']

    def writePlaylist(self):
        pid = self.playlistStorage

        with open('web/playlist.html', 'w', encoding='utf-8') as f:
            f.write("{% extends 'index.html' %}\n{% block playlist %}\n")
            if pid in self.playlistIDs.keys():
                f.write(f"Now playing: {self.playlistIDs[pid]}")
            else:
                f.write("Now playing: Something interesting...")
            f.write("\n{% endblock %}")

    @staticmethod
    def writeTable(listy: list):
        with open('web/table.html', 'w', encoding='utf-8') as f:
            f.write("{% extends 'playlist.html' %}\n{% block head %}\n{% endblock %}\n{% block body %}\n")
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
        print('Successful push\n')

    def handleData(self, api_resps: list):
        table = [['Name', '1v1', '2v2', '3v3', 'Wins',
                  '<p title="Competitive games this season">Games <sup>*</sup></p>',
                 'Reward level', 'Country', 'Platform']]

        for resp in api_resps:
            uid = resp['data']['platformInfo']['platformUserIdentifier']
            platform = resp['data']['platformInfo']['platformSlug']
            gen_url = f'{self.gen_base_url}/{platform}/{uid}/overview'
            totalprint = []

            rankdict = self.rankDict(resp)
            
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
            totalprint.append(str(resp['data']['userInfo']['countryCode']))
            totalprint.append(resp['data']['platformInfo']['platformSlug'])
            socialURLs = self.getSocialURLs(resp['data']['userInfo']['socialAccounts'])
            totalprint.append(socialURLs)
            totalprint.append(resp['data']['gameInfo']['team'])
            totalprint.append(gen_url)

            formatted = formatTable(totalprint)
            table.append(formatted)

        sorted_table = self.sortPlayersByTeams(table)

        self.writeTable(sorted_table)

    def handleExit(self):
        print('Closing webserver gracefully')
        self.webserver.kill()
        self.tcp_process.kill()

    def main(self):
        if is_chrome_installed():
            updateChromedriver()
        self.createEmptyTable()
        atexit.register(self.handleExit)
        while True:
            self.api_resps.clear()
            self.sort()
            self.checkIfNewPlaylist()
            matchData = self.checkIfNewmatch()
            if matchData:
                if 'players' not in matchData['Match']:
                    continue
                elif matchData['Match']['players'] is None:
                    continue
                self.requests(matchData)
                # If you want database functionality, uncomment and set up your own db + edit db_connect.py
                # if gameInfo['Match']['isRanked'] == 1:
                #     self.handleDBdata(self.api_resps)
                self.handleData(self.api_resps)
            sleep(2)


if __name__ == '__main__':
    init = rl_playerinfo()
    print(init.main())
