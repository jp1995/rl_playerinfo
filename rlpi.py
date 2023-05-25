from webdriver.curlInstaller import is_curl_installed, install_curl
from threaded_requests import threaded_requests
from db_connect import db_push_tracker_stats
from multiprocessing import Process, Queue
from web.formatTable import formatTable
from TCPserver import run_tcp_server
from logging_setup import log, logWipe
from web.app import run_webserver
from web.MMR import playlistDict
import atexit
import time
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
            self.useragentarr.append("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                     " Chrome/{}/0.0 Safari/537.36".format(i))
        self.playlistIDs = playlistDict
        self.rankDict = {}
        self.mmrOld = {}
        self.matchStorage = {}
        self.playlistStorage = ''
        self.matchCurrent = {}
        self.playlistCurrent = '69'
        self.mmrNew = {}
        self.api_resps = []

        self.playerCache = {}
        self.cacheExpiration = 1800

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
        log.info(f'Received: {data}')

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
            log.error('Plugin output is unexpected. Possible connection issue.')
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
        log.info('Table generated\n')

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
            log.info('MMR updated\n')

    """
    Appropriate error template is loaded and returned.
    """
    def error(self, errorType: str):
        error_mapping = {
            'API_down': 'error_templates/API_down.json',
            'API_server_error': 'error_templates/API_error.json',
            'API_unknown_player': 'error_templates/API_unknown.json'
        }
        log.error(f'API Error: {errorType}')
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
                        log.error(f'Unhandled API error, if possible create an issue on github.'
                                       f'\n {data["errors"][0]["message"]}')

            self.api_resps.append(data)

    """
    An API response is cached.
    """
    def placeIntoCache(self, uid, platform, resp):
        key = f'{uid}_{platform}'
        if key not in self.playerCache.keys() and platform is not None:
            self.playerCache[key] = [json.dumps(resp), time.time()]
            log.debug(f'Caching player {key}')

    """
    The cache is inspected, expired responses are discarded.
    """
    def cleanCache(self):
        current_time = time.time()
        exp_resps = []

        for key, [_, timestamp] in self.playerCache.items():
            if current_time - timestamp > self.cacheExpiration:
                exp_resps.append(key)

        if len(exp_resps) > 0:
            log.debug('Discarding expired items in cache')
            for key in exp_resps:
                del self.playerCache[key]

    """
    matchData is integrated into the responses. API responses are placed into cache.
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
                item['data']['gameInfo']['matchID'] = matchData['Match']['matchID']
                # Sometiems switch/xbl playername has different capitalisation from UID..?
                try:
                    item['data']['gameInfo']['team'] = matchData['Match']['players'][uid]['team']
                    self.placeIntoCache(uid, platform_slug, item)
                except KeyError:
                    log.debug('Hit player whose ingame name differs from their platformUserIdentifier.')
                    if platform_slug == 'switch' or platform_slug == 'xbl':
                        log.debug('Attempting switch/xbl lowercase workaround.')
                        item['data']['gameInfo']['team'] = matchData['Match']['players'][uid.lower()]['team']
                        self.placeIntoCache(uid.lower(), platform_slug, item)
                    else:
                        item['data']['gameInfo']['team'] = 0
                        log.warning('UID != matchData player, switch/xbl workaround failed, teams can be incorrect')
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
    API is only queried if player is not already cached or a bot.
    The bot templates and cached responses are appended to the resps.
    """
    def requests(self, matchData):
        urls, bots, cached = [], [], []

        for player in matchData['Match']['players']:
            platform_num = str(matchData['Match']['players'][player]['platform'])
            cache_key = f'{player}_{self.platformDict[platform_num]}'
            if platform_num == '0':
                bots.append(self.isBot())
                log.debug('Found bot, avoiding API query')
                continue
            elif cache_key in self.playerCache:
                cached.append(self.playerCache[cache_key][0])
                log.debug(f'Retrieving {cache_key} from cache')
                continue
            api_url = f'{self.api_base_url}/{self.platformDict[platform_num]}/{player}'
            urls.append(api_url)
            log.debug(f'Asking API for {api_url.split("/")[-1]}')

        resps = threaded_requests(urls, len(urls), self.useragentarr)
        resps.extend(cached)
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
    In the css, the table is divided in half, with the top being blue and bottom being red. Moving blue to top.
    """
    @staticmethod
    def sortPlayersByTeams(matchdicts: list, matchID: str):
        sorted_matchdicts = [{'Match': matchID}]
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
            errors = ['No API Response', 'API Server Error', 'Unknown to API', ' - AI']
            if any(error in resp['data']['platformInfo']['platformUserHandle'] for error in errors):
                continue
            platform = resp['data']['platformInfo']['platformSlug']
            gen_url = f'{self.gen_base_url}/{platform}/{uid}/overview'

            dbdump_dict['name'] = resp['data']['platformInfo']['platformUserHandle']
            dbdump_dict['platform'] = resp['data']['platformInfo']['platformSlug']

            dbdump_dict.update(self.createRankDict(resp))

            dbdump_dict['wins'] = resp['data']['segments'][0]['stats']['wins']['value']
            dbdump_dict['games_this_season'] = sum(self.rankDict[k] for k in ['1v1_games', '2v2_games', '3v3_games'])
            rewardlevel = resp['data']['segments'][0]['stats']['seasonRewardLevel']['metadata']['rankName']
            dbdump_dict['rewardlevel'] = rewardlevel if rewardlevel != 'None' else 'NULL'
            dbdump_dict['influencer'] = resp['data']['userInfo']['isInfluencer']
            dbdump_dict['premium'] = resp['data']['userInfo']['isPremium']
            dbdump_dict['sussy'] = str(resp['data']['userInfo']['isSuspicious']).replace('None', 'False')
            dbdump_dict['country'] = str(resp['data']['userInfo']['countryCode'])
            dbdump_dict['url'] = gen_url

            dbdump.append(dbdump_dict)

        db_push_tracker_stats(dbdump)
        log.info('Successful database push\n')

    """
    The list of lists that makes up the table is created.
    """
    def handleData(self, api_resps: list, matchID: str):
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
            rawtable['Games'] = sum(self.rankDict[k] for k in ['1v1_games', '2v2_games', '3v3_games'])
            rawtable['Rewardlevel'] = rewardlevel
            rawtable['Country'] = str(resp['data']['userInfo']['countryCode'])
            rawtable['Platform'] = resp['data']['platformInfo']['platformSlug']
            rawtable['socialURLs'] = socialURLs
            rawtable['Team'] = resp['data']['gameInfo']['team']
            rawtable['URL'] = gen_url

            formatted = formatTable(rawtable)
            table.append(formatted)

        sorted_table = self.sortPlayersByTeams(table, matchID)
        self.writeMatch(sorted_table)

    """
    The Flask server and TCP server are closed "gracefully".
    """
    def handleExit(self):
        self.webserver.kill()
        self.tcp_process.kill()
        log.info('Exiting...')

    """
    The main program loop.
    Uncomment the handleDBdata call, set up your own DB and edit db_connect.py for DB functionality.
    """
    def main(self):
        logWipe()
        if not is_curl_installed():
            install_curl()
        self.webserver.start()
        self.tcp_process.start()
        atexit.register(self.handleExit)
        minute = 0

        while True:
            if minute == 60:
                self.cleanCache()
                minute = 0

            self.api_resps.clear()
            self.sort()
            self.checkIfNewPlaylist()
            matchData = self.checkIfNewmatch()
            if matchData:
                if 'players' not in matchData['Match'] or matchData['Match']['players'] is None:
                    continue
                self.requests(matchData)
                matchID = matchData['Match'].get('matchID')
                self.handleData(self.api_resps, matchID)
                # if matchData['Match']['isRanked'] == 1:
                #     self.handleDBdata(self.api_resps)

            minute += 1
            time.sleep(1)


if __name__ == '__main__':
    init = rl_playerinfo()
    print(init.main())
