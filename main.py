import os
from time import sleep


class liveRLdata:
    def __init__(self):
        appdata = os.getenv('APPDATA')
        self.plugDir = f'{appdata}\\bakkesmod\\bakkesmod\\data\\PlayerNames\\'
        self.mainDict = {}
        self.platformDict = {'1': 'steam', '2': 'psn', '3': 'psn', '4': 'xbl',
                             '6': 'switch', '7': 'switch', '8': 'psynet', '11': 'epic'}
        self.base_url = 'https://rocketleague.tracker.network/rocket-league/profile/'
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
        return None

    def request(self):
        pass

    def main(self):
        while True:
            stringy = self.readDatafile()
            ready = self.transformData(stringy)
            if ready:
                return ready


if __name__ == '__main__':
    test = liveRLdata()
    while True:
        print(test.main())
        sleep(15)


