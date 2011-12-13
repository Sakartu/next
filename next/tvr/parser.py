from tvrage import feeds
from xml.etree import ElementTree as ET
from tvrep import Episode
from next.util.constants import TVRage as tvrpath

def fuzzy_search(show_name):
    '''
    This method searches the TVRage database for a given showname. The search is
    fuzzy, so looking for "doctor" will return Doctor Who (2005) as well. The
    result is a list of (name, sid) tuples.
    '''
    tree = ET.ElementTree(feeds.search(show_name))
    names = tree.findall(tvrpath.SEARCH_NAME)
    ids = tree.findall(tvrpath.SEARCH_ID)
    statuses = tree.findall(tvrpath.SEARCH_STATUS)
    results = map(lambda (x, y, z) : (x.text, y.text, z.text), zip(names, ids, statuses))
    return results

def get_all_eps(sid):
    '''
    This method parses episode list from the TVRage database for a given sid and
    returns an Episode object for each episode in the list
    '''
    tree = ET.ElementTree(feeds.episode_list(sid))
    showname = tree.find(tvrpath.EPLIST_NAME).text
    results = []
    seasons = map(ET.ElementTree, tree.findall(tvrpath.EPLIST_SEASON))
    for season in seasons:
        seasonnum = season.getroot().get(tvrpath.EPLIST_SEASONNUM)
        eps = map(ET.ElementTree, season.findall(tvrpath.EPLIST_EPISODE))
        for ep in eps:
            epnum = ep.find(tvrpath.EPLIST_EPNUM).text
            title = ep.find(tvrpath.EPLIST_TITLE).text
            airdate = ep.find(tvrpath.EPLIST_AIRDATE).text
            results.append(Episode(sid, showname, seasonnum, epnum, title, airdate))
    return results

def get_status(sid):
    tree = ET.ElementTree(feeds.showinfo(sid))
    try:
        return tree.find(tvrpath.STATUS_STATUS).text
    except:
        return "Unknown"
