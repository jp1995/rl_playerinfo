

def formatTable(listy: list):
    outlist = []

    url = listy[-1]
    outlist.append(f'<a href="{url}">{listy[0]}</a>')

    icondict = {'NULL': '<img class="tier" src="../assets/unranked.png" alt="unranked"',
                'Bronze I': '<img class="tier" src="../assets/b1.png" alt="b1">',
                'Bronze II': '<img class="tier" src="../assets/b2.png" alt="b2">',
                'Bronze III': '<img class="tier" src="../assets/b3.png" alt="b3">',
                'Silver I': '<img class="tier" src="../assets/s1.png" alt="s1">',
                'Silver II': '<img class="tier" src="../assets/s2.png" alt="s2">',
                'Silver III': '<img class="tier" src="../assets/s3.png" alt="s3">',
                'Gold I': '<img class="tier" src="../assets/g1.png" alt="g1">',
                'Gold II': '<img class="tier" src="../assets/g2.png" alt="g2">',
                'Gold III': '<img class="tier" src="../assets/g3.png" alt="g3">',
                'Platinum I': '<img class="tier" src="../assets/p1.png" alt="p1">',
                'Platinum II': '<img class="tier" src="../assets/p2.png" alt="p2">',
                'Platinum III': '<img class="tier" src="../assets/p3.png" alt="p3">',
                'Diamond I': '<img class="tier" src="../assets/d1.png" alt="d1">',
                'Diamond II': '<img class="tier" src="../assets/d2.png" alt="d2">',
                'Diamond III': '<img class="tier" src="../assets/d3.png" alt="d3">',
                'Champion I': '<img class="tier" src="../assets/c1.png" alt="c1">',
                'Champion II': '<img class="tier" src="../assets/c2.png" alt="c2">',
                'Chamion III': '<img class="tier" src="../assets/c3.png" alt="c3">',
                'Grand Champion I': '<img class="tier" src="../assets/gc1.png" alt="gc1">',
                'Grand Champion II': '<img class="tier" src="../assets/gc2.png" alt="gc2">',
                'Grand Champion III': '<img class="tier" src="../assets/gc3.png" alt="gc3">',
                'Supersonic Legend': '<img class="tier" src="../assets/ssl.png" alt="ssl">'}

    del listy[0]
    del listy[-1]

    for item in listy:
        for key, value in icondict.items().__reversed__():
            if isinstance(item, str):
                if item == key.split(' ')[0] and item != 'NULL':
                    outlist.append(icondict[f'{key.split(" ")[0]} I'])
                    break
                if item.startswith(key) and item != 'NULL':
                    outlist.append(value+f'<span>{item.split(" ")[-1]}, {listy[listy.index(item)+1]}</span>')
                    listy.remove(item)
                    break
                if item.startswith(key):
                    outlist.append(value)
                    listy.remove(item)
                    break
                if item == key == 'NULL':
                    outlist.append(value)
                    break
        else:
            continue

    print(listy)
    # print(outlist)
    for item in listy:
        outlist.append(item)

    del outlist[10]
    outlist.insert(10, outlist[4])
    del outlist[4]
    del outlist[4]; del outlist[4]; del outlist[4]

    print(outlist)
    return outlist


def classify_table():
    pass
