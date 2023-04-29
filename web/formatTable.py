icondict = {'NULL': '<img class="tier" src="../assets/icons/unranked.png" alt="unranked" title="Unranked">',
            'Unranked': '<img class="tier" src="../assets/icons/unranked.png" alt="unranked" title="Unranked">',
            'Bronze I': '<img class="tier" src="../assets/icons/b1.png" alt="b1" title="Bronze I">',
            'Bronze II': '<img class="tier" src="../assets/icons/b2.png" alt="b2" title="Bronze II">',
            'Bronze III': '<img class="tier" src="../assets/icons/b3.png" alt="b3" title="Bronze III">',
            'Silver I': '<img class="tier" src="../assets/icons/s1.png" alt="s1" title="Silver I">',
            'Silver II': '<img class="tier" src="../assets/icons/s2.png" alt="s2" title="Silver II">',
            'Silver III': '<img class="tier" src="../assets/icons/s3.png" alt="s3" title="Silver III">',
            'Gold I': '<img class="tier" src="../assets/icons/g1.png" alt="g1" title="Gold I">',
            'Gold II': '<img class="tier" src="../assets/icons/g2.png" alt="g2" title="Gold II">',
            'Gold III': '<img class="tier" src="../assets/icons/g3.png" alt="g3" title="Gold III">',
            'Platinum I': '<img class="tier" src="../assets/icons/p1.png" alt="p1" title="Platinum I">',
            'Platinum II': '<img class="tier" src="../assets/icons/p2.png" alt="p2" title="Platinum II">',
            'Platinum III': '<img class="tier" src="../assets/icons/p3.png" alt="p3" title="Platinum III">',
            'Diamond I': '<img class="tier" src="../assets/icons/d1.png" alt="d1" title="Diamond I">',
            'Diamond II': '<img class="tier" src="../assets/icons/d2.png" alt="d2" title="Diamond II">',
            'Diamond III': '<img class="tier" src="../assets/icons/d3.png" alt="d3" title="Diamond III">',
            'Champion I': '<img class="tier" src="../assets/icons/c1.png" alt="c1" title="Champion I">',
            'Champion II': '<img class="tier" src="../assets/icons/c2.png" alt="c2" title="Champion II">',
            'Champion III': '<img class="tier" src="../assets/icons/c3.png" alt="c3" title="Champion III">',
            'Grand Champion I': '<img class="tier" src="../assets/icons/gc1.png" alt="gc1" title="Grand Champion I">',
            'Grand Champion II': '<img class="tier" src="../assets/icons/gc2.png" alt="gc2" title="Grand Champion II">',
            'Grand Champion III': '<img class="tier" src="../assets/icons/gc3.png" alt="gc3" title="Grand Champion III">',
            'Supersonic Legend': '<img class="tier" src="../assets/icons/ssl.png" alt="ssl" title="Supersonic Legend">',
            'Grand I': '<img class="tier" src="../assets/icons/gc1.png" alt="gc1">',
            'Supersonic I': '<img class="tier" src="../assets/icons/gc1.png" alt="gc1">'}

platforms = ['unknown', 'steam', 'xbl', 'psn', 'switch', 'epic']
social_icons = {'twitter': 'assets/icons/twitter.svg', 'twitch': 'assets/icons/twitch.svg',
                'reddit': 'assets/icons/reddit.svg'}


def formatTable(rawMatch: dict):
    formattedMatch = {}
    url = rawMatch['URL']
    handleLink = f'<div class="namecontainer">' \
                 f'<a href="{url}" class="nameurl">{rawMatch["Handle"]}</a>' \
                 f'<div class="socialscontainer">'

    for social in rawMatch['socialURLs']:
        for key, value in social_icons.items():
            if key in social:
                soclink = f'<a href="{social}"><img class="social" src="{value}" alt="{key}"></a>'
                handleLink += soclink

    handleLink += '</div></div>'
    formattedMatch['handleLink'] = handleLink

    for rawkey in ['1v1', '2v2', '3v3', 'Rewardlevel']:
        rank = rawMatch.get(rawkey)
        if rawkey == 'Rewardlevel':
            if rawMatch[rawkey] == 'NULL RR':
                formattedMatch[rawkey] = icondict['NULL']
            else:
                formattedMatch[rawkey] = icondict[f'{rank} I']
        elif rawMatch[rawkey] == 'NULL' and rawkey != 'Rewardlevel':
            formattedMatch[rawkey] = icondict[rank] + f'<span>I, {rawMatch[f"{rawkey}_winstreak"]}</span>'
        elif rawMatch[rawkey] != 'NULL' and rawkey != 'Rewardlevel' and 'Division' in rank:
            rankNoDiv = rank.split('Division')[0].strip()
            div = rank.split('Division')[1].strip()
            formattedMatch[rawkey] = icondict[rankNoDiv] + f'<span>{div}, {rawMatch[f"{rawkey}_winstreak"]}</span>'

    for key in ['Wins', 'Games', 'Team']:
        formattedMatch[key] = rawMatch[key]

    flag = rawMatch['Country'].lower()
    flaglink = f'<img class="flag" src="https://flagicons.lipis.dev/flags/4x3/{flag}.svg" alt="{flag}" title="{flag}">'
    if flag != 'none':
        formattedMatch['Country'] = flaglink
    else:
        formattedMatch['Country'] = '-'

    platform = rawMatch['Platform']
    platlink = f'<img class="platform" src="assets/icons/{platform}.svg" alt="{platform}" title="{platform}">'
    if platform in platforms:
        formattedMatch['Platform'] = platlink

    return formattedMatch
