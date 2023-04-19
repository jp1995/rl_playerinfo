from webdriver.updateWebdriver import updateChromedriver
from webdriver.webdriver_conf import is_chrome_installed
from threaded_requests import threaded_requests
from db_connect import db_push_tracker_stats
from multiprocessing import Process, Queue
from web.formatTable import formatTable
from TCPserver import run_tcp_server
from web.app import run_webserver
from web.MMR import playlistDict
from time import sleep
import atexit
import json


class rl_playerinfo:
    def __init__(self):
        self.useragentarr = []
        self.platformDict = {'0': 'unknown', '1': 'steam', '2': 'psn', '3': 'psn', '4': 'xbl',
                             '6': 'switch', '7': 'switch', '8': 'psynet', '11': 'epic'}
        self.soc_base_urls = {'twitch': 'https://twitch.tv/', 'reddit': 'https://www.reddit.com/user/',
                              'twitter': 'https://twitter.com/'}
        self.api_base_url = 'https://api.tracker.gg/api/v2/rocket-league/standard/profile'
        self.gen_base_url = 'https://rocketleague.tracker.network/rocket-league/profile'
        for i in range(111, 81, -1):
            self.useragentarr.append("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}/0.0 Safari/537.36".format(i))
        self.playlistIDs = playlistDict
        self.rankDict = {}
        self.mmrOld = {}
        self.matchStorage = {}
        self.playlistStorage = ''
        self.matchCurrent = {}
        self.playlistCurrent = '69'
        self.mmrNew = {}
        self.api_resps = []

        self.q = Queue()
        self.tcp_process = Process(target=run_tcp_server, args=(self.q,))
        self.mmrq = Queue()
        self.matchq = Queue()
        self.playlistq = Queue()
        self.webserver = Process(target=run_webserver, args=(self.mmrq, self.matchq, self.playlistq,))

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
    This really only checks for differences, it will also run in casual games when someone leaves/joins.
    """
    def checkIfNewmatch(self):
        if self.matchCurrent != self.matchStorage:
            self.matchStorage = self.matchCurrent

            return self.matchCurrent

    def writeMatch(self, listy: list):
        self.matchq.put(listy)
        print('Table generated\n')

    def checkIfNewPlaylist(self):
        if self.playlistCurrent != self.playlistStorage:
            self.playlistStorage = self.playlistCurrent

            self.writePlaylist()

    def writePlaylist(self):
        pid = self.playlistStorage
        if pid in self.playlistIDs.keys():
            self.playlistq.put(self.playlistIDs[pid])
        else:
            self.playlistq.put('Now playing: Something interesting...')

    def writeMMR(self):
        if self.mmrOld != self.mmrNew:
            self.mmrOld = self.mmrNew
            self.mmrq.put(json.dumps(self.mmrNew))
            print('MMR updated')

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
    The two loops could be combined, but it seems to create problems with really annoying workarounds.
    """
    def responses_mod(self, resps: list, matchData: dict):
        valid_players = []
        errorhandles = ['Unknown to API', 'API Server Error', 'No API Response', 'AI']
        self.responses_check(resps)

        # First the clean responses are found
        for item in self.api_resps:
            uid = item['data']['platformInfo'].get('platformUserIdentifier', None)
            platform_slug = item['data']['platformInfo'].get('platformSlug', None)
            if platform_slug is not None:
                item['data']['gameInfo'] = {}
                # Sometiems switch/xbl playername has different capitalisation from UID..?
                try:
                    item['data']['gameInfo']['team'] = matchData['Match']['players'][uid]['team']
                except KeyError:
                    if platform_slug == 'switch' or platform_slug == 'xbl':
                        item['data']['gameInfo']['team'] = matchData['Match']['players'][uid.lower()]['team']
                    else:
                        item['data']['gameInfo']['team'] = 0
                        print('UID != matchData player, switch/xbl workaround did not work, teams can be incorrect')
                valid_players.append(uid)

        # And then errors are handled.
        for player in matchData['Match']['players']:
            for item in self.api_resps:
                handle = item['data']['platformInfo']['platformUserHandle']
                if player not in valid_players and handle in errorhandles:
                    item['data']['platformInfo']['platformUserIdentifier'] = player
                    item['data']['platformInfo']['platformUserHandle'] = player + ' - ' + handle
                    item['data']['gameInfo']['team'] = matchData['Match']['players'][player]['team']
                    item['data']['platformInfo']['platformSlug'] = self.platformDict[
                        str(matchData['Match']['players'][player]['platform'])]
                    break

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

        resps = threaded_requests(urls, len(urls), self.useragentarr)
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
    In the css, the table is divided in half, with the top half being blue and bottom half being red. Moving blue to top.
    """
    @staticmethod
    def sortPlayersByTeams(matchdicts: list):
        sorted_matchdicts = ['Match']
        sorted_matchdicts.extend(sorted(matchdicts, key=lambda x: x['Team']))
        return sorted_matchdicts

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
        table = []

        for resp in api_resps:
            uid = resp['data']['platformInfo']['platformUserIdentifier']
            platform = resp['data']['platformInfo']['platformSlug']
            gen_url = f'{self.gen_base_url}/{platform}/{uid}/overview'

            rawtable = {}
            rewardlevel = resp['data']['segments'][0]['stats']['seasonRewardLevel']['metadata']['rankName']
            rewardlevel = rewardlevel if rewardlevel != 'None' else 'NULL RR'
            self.rankDict = self.createRankDict(resp)
            socialURLs = self.getSocialURLs(resp['data']['userInfo']['socialAccounts'])

            rawtable['Handle'] = resp['data']['platformInfo']['platformUserHandle']
            for key, value in self.rankDict.items():
                if key not in ['1v1_games', '2v2_games', '3v3_games']:
                    rawtable[key] = f'{value}'
            rawtable['Wins'] = resp['data']['segments'][0]['stats']['wins']['value']
            rawtable['Games'] = self.rankDict['1v1_games'] + self.rankDict['2v2_games'] + self.rankDict['3v3_games']
            rawtable['Rewardlevel'] = rewardlevel
            rawtable['Country'] = str(resp['data']['userInfo']['countryCode'])
            rawtable['Platform'] = resp['data']['platformInfo']['platformSlug']
            rawtable['socialURLs'] = socialURLs
            rawtable['Team'] = resp['data']['gameInfo']['team']
            rawtable['URL'] = gen_url

            formatted = formatTable(rawtable)
            table.append(formatted)

        sorted_table = self.sortPlayersByTeams(table)
        self.writeMatch(sorted_table)

    """
    The Flask server and TCP server are closed "gracefully".
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
        self.webserver.start()
        self.tcp_process.start()
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
