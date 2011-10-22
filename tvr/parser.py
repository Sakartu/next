from tvrage import feeds
from xml.etree import ElementTree as ET
from tvrep import Episode
from util.constants import TVRage as tvrpath

def fuzzy_search(show_name):
    tree = ET.ElementTree(feeds.search(show_name))
    names = tree.findall(tvrpath.SEARCH_NAME)
    ids = tree.findall(tvrpath.SEARCH_ID)
    results = map(lambda (x, y) : (x.text, y.text), zip(names, ids))
    return results

def get_all_eps(sid):
    tree = ET.ElementTree(feeds.episode_list(sid))
    showname = tree.find(tvrpath.EPLIST_NAME).text
    results = []
    seasons = map(ET.ElementTree, tree.findall(tvrpath.EPLIST_SEASON))
    for season in seasons:
        seasonnum = season.getroot().get(tvrpath.EPLIST_SEASONNUM)
        eps = map(ET.ElementTree, season.findall(tvrpath.EPLIST_EPISODE))
        for ep in eps:
            epnum = ep.find(tvrpath.EPLIST_EPNUM).text
            airdate = ep.find(tvrpath.EPLIST_AIRDATE).text
            title = ep.find(tvrpath.EPLIST_TITLE).text
            results.append(Episode(sid, showname, seasonnum, epnum, airdate, title))
    return results

