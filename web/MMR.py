import math


playlistDict = {'0': 'Casual', '1': 'Casual Duel', '2': 'Casual Doubles', '3': 'Casual Standard', '4': 'Chaos',
                '6': 'Private Match', '7': 'Season', '8': 'Exhibition', '9': 'Training', '10': 'Duel', '11': 'Doubles',
                '13': 'Standard', '15': 'Snow Day', '16': 'Rocket Labs', '17': 'Hoops', '18': 'Rumble',
                '22': 'Tournament', '23': 'Dropshot', '24': 'Local Match', '26': 'External Match', '27': 'Hoops',
                '28': 'Rumble', '29': 'Dropshot', '30': 'Snow Day', '31': 'Ghost Hunt', '32': 'Beach Ball',
                '33': 'Spike Rush', '34': 'Tournament', '35': 'Rocket Labs', '37': 'Dropshot Rumble',
                '38': 'Heatseeker', '41': 'Boomer Ball', '43': '2v2 Heatseeker', '44': 'Winter Breakaway',
                '46': 'Gridiron', '47': 'Super Cube', '48': 'Tactical Rumble', '49': 'Spring Loaded',
                '50': 'Speed Demon', '52': 'Gotham Rumble', '54': 'Knockout'}


def modMMRjson(jsonDict):

    for key in list(jsonDict["MMR"].keys()):
        playlist_name = playlistDict.get(key, None)
        if playlist_name:
            jsonDict["MMR"][playlist_name] = jsonDict["MMR"].pop(key)

    for key, value in jsonDict["MMR"].items():
        if math.copysign(1, value['delta']) == 1:
            jsonDict['MMR'][key]['delta'] = '+'+str(round(value['delta'], 1))
        else:
            jsonDict['MMR'][key]['delta'] = str(round(value['delta'], 1))
        if math.copysign(1, value['streak']) == 1:
            jsonDict['MMR'][key]['streak'] = '+'+str(value['streak'])
        else:
            jsonDict['MMR'][key]['streak'] = str(value['streak'])

    return jsonDict

