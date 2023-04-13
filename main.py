from webdriver.updateWebdriver import updateChromedriver
from webdriver.webdriver_conf import is_chrome_installed
from threaded_requests import threaded_requests
from db_connect import db_push_tracker_stats
from multiprocessing import Process, Queue
from web.formatTable import formatTable
from web.MMR import playlistDict
from TCPserver import run_tcp_server
from tabulate import tabulate
from time import sleep
import subprocess
import atexit
import json


class rl_playerinfo:
    def __init__(self):
        self.platformDict = {'0': 'unknown', '1': 'steam', '2': 'psn', '3': 'psn', '4': 'xbl',
                             '6': 'switch', '7': 'switch', '8': 'psynet', '11': 'epic'}
        self.playlistIDs = playlistDict
        self.soc_base_urls = {'twitch': 'https://twitch.tv/', 'reddit': 'https://www.reddit.com/user/',
                              'twitter': 'https://twitter.com/'}
        self.api_base_url = 'https://api.tracker.gg/api/v2/rocket-league/standard/profile'
        self.gen_base_url = 'https://rocketleague.tracker.network/rocket-league/profile'
        self.webserver = subprocess.Popen("python app.py", cwd='./web/', shell=True)
        self.rankDict = {}
        self.matchStorage = {}
        self.playlistStorage = '69'
        self.matchCurrent = {}
        self.playlistCurrent = '69'
        self.mmrNew = {}
        self.api_resps = []

        self.q = Queue()
        self.tcp_process = Process(target=run_tcp_server, args=(self.q,))
        self.tcp_process.start()

    """
    Plugin output is pulled from the TCP server queue and inserted into class variables.
    """
    def sort(self):
        if self.q.empty():
            return None
        data = self.q.get()
        print(f'Received: {data}')

        try:
            jdata = json.loads(data)
            if 'Match' in jdata.keys():
                self.matchCurrent = jdata
            elif 'Playlist' in jdata.keys():
                self.playlistCurrent = str(jdata['Playlist'])
            elif all(key.isnumeric() for key in jdata.keys()):
                self.mmrNew = jdata
                self.writeMMR()
        except json.JSONDecodeError:
            print('Something broke really bad? Uhh try restarting... everything? Or not.')
            return None

    """
    On script start the empty `Awaiting Session` table is loaded into table.html. mmr.txt is created or emptied.
    """
    @staticmethod
    def createEmptyTable():
        with open('web/table_base.html', 'r', encoding='utf-8') as tb:
            with open('web/table.html', 'w', encoding='utf-8') as t:
                base = tb.read()
                t.write(base)
        with open('web/mmr.txt', 'w') as create:
            pass

    """
    This really only checks for differences, it will also run in casual games when someone leaves/joins.
    """
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
            mmrOld = f.readline()
            if mmrOld != self.mmrNew:
                f.write(json.dumps(self.mmrNew))

    """
    Appropriate error template is loaded and returned.
    """
    @staticmethod
    def error(errorType: str):
        error_mapping = {
            'API_down': 'error_templates/API_down.json',
            'API_server_error': 'error_templates/API_error.json',
            'API_unknown_player': 'error_templates/API_unknown.json'
        }
        print(f'API Error: {errorType}')
        with open(error_mapping[errorType], 'r', encoding='utf-8') as f:
            json = f.read()
        return json

    @staticmethod
    def isBot():
        with open('error_templates/bot.json', 'r', encoding='utf-8') as f:
            j = f.read()
        return j

    """
    Basic json validation, error handling with the error function.
    """
    def responses_check(self, resps: list):
        for item in resps:
            try:
                data = json.loads(item)
            except json.decoder.JSONDecodeError:
                data = json.loads(self.error('API_down'))
            else:
                if 'errors' in data and data['errors']:
                    if 'unhandled exception' in data['errors'][0]['message']:
                        data = json.loads(self.error('API_server_error'))
                    elif 'We could not find the player' in data['errors'][0]['message']:
                        data = json.loads(self.error('API_unknown_player'))
                    else:
                        print(f'New error, if possible create an issue on github.\n {data["errors"][0]["message"]}')

            self.api_resps.append(data)

    """
    matchData is integrated into the responses.
    In case of an API error or bot, displayed clearly with the relvant name and platform.
    Problem: unnecessary iterations in the nested loop. Fix?
    """
    def responses_mod(self, resps: list, matchData: dict):
        valid_players = []
        errorhandles = ['Unknown to API', 'API Server Error', 'No API Response', 'AI']
        self.responses_check(resps)

        for item in self.api_resps:
            for player in matchData['Match']['players']:
                uid = item['data']['platformInfo']['platformUserIdentifier']
                platform_slug = item['data']['platformInfo'].get('platformSlug', None)
                if platform_slug is not None:
                    item['data']['gameInfo'] = {}
                    item['data']['gameInfo']['team'] = matchData['Match']['players'][uid]['team']
                    valid_players.append(uid)
                    continue

                handle = item['data']['platformInfo']['platformUserHandle']
                if player not in valid_players and handle in errorhandles:
                    item['data']['platformInfo']['platformUserIdentifier'] = player
                    item['data']['platformInfo']['platformUserHandle'] = player + ' - ' + handle
                    item['data']['gameInfo']['team'] = matchData['Match']['players'][player]['team']
                    item['data']['platformInfo']['platformSlug'] = self.platformDict[
                        str(matchData['Match']['players'][player]['platform'])]
                    continue

    """
    API is only queried if player is not a bot. Afterwards, the bot templates (if any) are appended to the responses.
    """
    def requests(self, matchData):
        urls, bots = [], []

        for player in matchData['Match']['players']:
            platform_num = str(matchData['Match']['players'][player]['platform'])
            if platform_num == '0':
                bots.append(self.isBot())
                continue
            api_url = f'{self.api_base_url}/{self.platformDict[platform_num]}/{player}'
            urls.append(api_url)

        resps = threaded_requests(urls, len(urls))
        resps.extend(bots)
        self.responses_mod(resps, matchData)

    """
    The ranks of the three main playlists are turned into a more usable format. Missing ranks are handled.
    """
    @staticmethod
    def createRankDict(resp: dict):
        rankdict = {}

        for x in range(1, 4):
            segment_name = f'{x}v{x}'
            for segment in resp['data']['segments']:
                if segment_name in segment['metadata']['name']:
                    tier = segment['stats']['tier']['metadata']['name']
                    div = segment['stats']['division']['metadata']['name'] or 'I'

                    rankdict[segment_name] = f'{tier} {div}'
                    rankdict[f'{segment_name}_winstreak'] = int(segment['stats']['winStreak']['displayValue'])
                    rankdict[f'{segment_name}_games'] = int(segment['stats']['matchesPlayed']['value'])

            if segment_name not in rankdict.keys():
                rankdict[segment_name] = 'NULL'
                rankdict[f'{segment_name}_winstreak'] = 0
                rankdict[f'{segment_name}_games'] = 0

        sorted_rankdict = {k: v for k, v in sorted(rankdict.items())}
        return sorted_rankdict

    """
    The table is divided in half in the css, with the top half being blue and bottom half being red. Moving blue to top.
    """
    @staticmethod
    def sortPlayersByTeams(table: list):
        stable = sorted(table[1:], key=lambda x: int(x[-1]))
        for item in stable:
            del item[-1]
        sorted_table = [table[0]] + stable

        return sorted_table

    def getSocialURLs(self, listy: list):
        if listy:
            outl = []
            for d in listy:
                if d['platformSlug'] in self.soc_base_urls:
                    url = self.soc_base_urls[d['platformSlug']] + d['platformUserHandle']
                    outl.append(url)
            return outl
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

    """
    Yes, theoretically someone could sql inject into your local db here, with tablefmt='unsafehtml'.
    Need to write a function that checks names. Or total rewrite of the table creation, without tabulate.
    """
    @staticmethod
    def writeTable(listy: list):
        with open('web/table.html', 'w', encoding='utf-8') as f:
            f.write("{% extends 'playlist.html' %}\n{% block head %}\n{% endblock %}\n{% block body %}\n")
            f.write(tabulate(listy, headers='firstrow', tablefmt='unsafehtml', colalign='center', numalign='center'))
            f.write("\n{% endblock %}")
        print('Table generated')

    """
    Data to be inserted into the database is collected.
    """
    def handleDBdata(self, api_resps: list):
        dbdump = []
        for resp in api_resps:
            dbdump_dict = {}
            uid = resp['data']['platformInfo']['platformUserIdentifier']
            platform = resp['data']['platformInfo']['platformSlug']
            gen_url = f'{self.gen_base_url}/{platform}/{uid}/overview'

            dbdump_dict['name'] = resp['data']['platformInfo']['platformUserHandle']
            dbdump_dict['platform'] = resp['data']['platformInfo']['platformSlug']

            dbdump_dict.update(self.rankDict)

            dbdump_dict['wins'] = resp['data']['segments'][0]['stats']['wins']['value']
            dbdump_dict['games_this_season'] = self.rankDict['1v1_games'] + self.rankDict['2v2_games'] + self.rankDict['3v3_games']
            rewardlevel = resp['data']['segments'][0]['stats']['seasonRewardLevel']['metadata']['rankName']
            dbdump_dict['rewardlevel'] = rewardlevel if rewardlevel != 'None' else 'NULL'
            dbdump_dict['influencer'] = resp['data']['userInfo']['isInfluencer']
            dbdump_dict['premium'] = resp['data']['userInfo']['isPremium']
            dbdump_dict['sussy'] = str(resp['data']['userInfo']['isSuspicious']).replace('None', 'False')
            dbdump_dict['country'] = str(resp['data']['userInfo']['countryCode'])
            dbdump_dict['url'] = gen_url

            dbdump.append(dbdump_dict)

        db_push_tracker_stats(dbdump)
        print('Successful push\n')

    """
    The list of lists that makes up the table is created.
    """
    def handleData(self, api_resps: list):
        table = [['Name', '1v1', '2v2', '3v3', 'Wins',
                  '<p title="Competitive games this season">Games <sup>*</sup></p>',
                  'Reward level', 'Country', 'Platform']]

        for resp in api_resps:
            uid = resp['data']['platformInfo']['platformUserIdentifier']
            platform = resp['data']['platformInfo']['platformSlug']
            gen_url = f'{self.gen_base_url}/{platform}/{uid}/overview'
            totalprint = []

            self.rankDict = self.createRankDict(resp)

            totalprint.append(resp['data']['platformInfo']['platformUserHandle'])
            for key, value in self.rankDict.items():
                if key not in ['1v1_games', '2v2_games', '3v3_games']:
                    totalprint.append(f'{value}')
            totalprint.append(resp['data']['segments'][0]['stats']['wins']['value'])
            totalprint.append(self.rankDict['1v1_games'] + self.rankDict['2v2_games'] + self.rankDict['3v3_games'])
            rewardlevel = resp['data']['segments'][0]['stats']['seasonRewardLevel']['metadata']['rankName']
            rewardlevel = rewardlevel if rewardlevel != 'None' else 'NULL RR'
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

    """
    The Flask server and TCP server are closed gracefully.
    """
    def handleExit(self):
        self.webserver.kill()
        self.tcp_process.kill()
        print('Exiting...')

    """
    The main program loop.
    Uncomment the handleDBdata call, set up your own DB and edit db_connect.py for DB functionality.
    """
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
                if 'players' not in matchData['Match'] or matchData['Match']['players'] is None:
                    continue
                self.requests(matchData)
                self.handleData(self.api_resps)
                # if gameInfo['Match']['isRanked'] == 1:
                #     self.handleDBdata(self.api_resps)

            sleep(2)


if __name__ == '__main__':
    init = rl_playerinfo()
    print(init.main())
