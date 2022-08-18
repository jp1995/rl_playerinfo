

def getRankicons(dicty: dict):
    out = {}
    icondict = {'NULL': '<img class="tier" src="../assets/unranked.png" alt="unranked" width="42" height="42">',
                'Bronze I': '<img class="tier" src="../assets/b1.png" alt="b1" width="42" height="42">',
                'Bronze II': '<img class="tier" src="../assets/b2.png" alt="b2" width="42" height="42">',
                'Bronze III': '<img class="tier" src="../assets/b3.png" alt="b3" width="42" height="42">',
                'Silver I': '<img class="tier" src="../assets/s1.png" alt="s1" width="42" height="42">',
                'Silver II': '<img class="tier" src="../assets/s2.png" alt="s2" width="42" height="42">',
                'Silver III': '<img class="tier" src="../assets/s3.png" alt="s3" width="42" height="42">',
                'Gold I': '<img class="tier" src="../assets/g1.png" alt="g1" width="42" height="42">',
                'Gold II': '<img class="tier" src="../assets/g2.png" alt="g2" width="42" height="42">',
                'Gold III': '<img class="tier" src="../assets/g3.png" alt="g3" width="42" height="42">',
                'Platinum I': '<img class="tier" src="../assets/p1.png" alt="p1" width="42" height="42">',
                'Platinum II': '<img class="tier" src="../assets/p2.png" alt="p2" width="42" height="42">',
                'Platinum III': '<img class="tier" src="../assets/p3.png" alt="p3" width="42" height="42">',
                'Diamond I': '<img class="tier" src="../assets/d1.png" alt="d1" width="42" height="42">',
                'Diamond II': '<img class="tier" src="../assets/d2.png" alt="d2" width="42" height="42">',
                'Diamond III': '<img class="tier" src="../assets/d3.png" alt="d3" width="42" height="42">',
                'Champion I': '<img class="tier" src="../assets/c1.png" alt="c1" width="42" height="42">',
                'Champion II': '<img class="tier" src="../assets/c2.png" alt="c2" width="42" height="42">',
                'Chamion III': '<img class="tier" src="../assets/c3.png" alt="c3" width="42" height="42">',
                'Grand Champion I': '<img class="tier" src="../assets/gc1.png" alt="gc1" width="42" height="42">',
                'Grand Champion II': '<img class="tier" src="../assets/gc2.png" alt="gc2" width="42" height="42">',
                'Grand Champion III': '<img class="tier" src="../assets/gc3.png" alt="gc3" width="42" height="42">',
                'Supersonic Legend': '<img class="tier" src="../assets/ssl.png" alt="ssl" width="42" height="42">'}

    for ikey, ivalue in dicty.items():
        for okey, ovalue in icondict.items():
            if isinstance(ivalue, str):
                if ivalue.startswith(okey):
                    # I'm somewhat confused why this works but ... seems good.
                    out[ikey] = icondict[okey]
            else:
                out[ikey] = ivalue

    return out
