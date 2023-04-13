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
social_icons = {'twitter': 'assets/icons/twitter.svg', 'twitch': 'assets/icons/twitch.svg', 'reddit': 'assets/icons/reddit.svg'}


def formatTable(listy: list):
    print(listy)
    outlist = []
    url = listy[-1]
    urllink = f'<div class="namecontainer"><a href="{url}" class="nameurl">{listy[0]}</a><div class="socialscontainer">'

    for social in listy[-3]:
        for key, value in social_icons.items():
            if key in social:
                soclink = f'<a href="{social}"><img class="social" src="{value}" alt="{key}"></a>'
                urllink += soclink

    urllink += '</div></div>'
    outlist.append(urllink)

    del listy[0]
    del listy[-1]
    del listy[-2]

    for item in listy:
        for key, value in icondict.items().__reversed__():
            if isinstance(item, str):
                if item == key == 'NULL':
                    outlist.append(value+f'<span>I, {listy[listy.index(item)+1]}</span>')
                    listy.remove(item)
                    break
                if item == 'NULL RR':
                    outlist.append(icondict['NULL'])
                    break
                if item == key.replace(' I', '').replace(' II', '').replace(' III', ''):
                    outlist.append(icondict[f'{key.split(" ")[0]} I'])
                    break
                if item.startswith(key) and item != 'NULL':
                    outlist.append(value+f'<span>{item.split(" ")[-1]}, {listy[listy.index(item)+1]}</span>')
                    listy.remove(item)
                    break
        else:
            continue

    # Exclude already used winstreak items
    outlist.extend(listy[3:])
    # Replace reward level string with icon
    outlist[7:8] = [outlist[4]]
    outlist[4:5] = []

    flag = outlist[7].lower()
    flaglink = f'<img class="flag" src="https://flagicons.lipis.dev/flags/4x3/{flag}.svg" alt="{flag}" title="{flag}">'
    if flag != 'none':
        outlist = outlist[:7]+[flaglink]+outlist[8:]
    else:
        outlist = outlist[:7] + ['-'] + outlist[8:]

    platform = outlist[8]
    platlink = f'<img class="platform" src="assets/icons/{platform}.svg" alt="{platform}" title="{platform}">'
    if platform in platforms:
        outlist = outlist[:8] + [platlink] + outlist[9:]

    return outlist
