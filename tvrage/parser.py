from tvrage import feeds as feeds
from xml.etree import ElementTree as ET
from tvrep import Episode
import util.constants.TVRage as tvrpath

def fuzzy_search(show_name):
   tree = ET.ElementTree(feeds.search(show_name))
   names = tree.findall(tvrpath.SEARCH_NAME)
   ids = tree.findall(tvrpath.SEARCH_ID)
   results = zip(map(lambda (x, y) : (x.text, y.text), names, ids))
   return results

def get_all_eps(sid):
    tree = ET.ElementTree(feeds.episode_list(sid))
    showname = tree.find().text
    seasons = tree.findall(tvrpath.EPLIST_SEASONNUM)
    epnums = tree.findall(tvrpath.EPLIST_EPNUM)
    airdates = tree.findall(tvrpath.EPLIST_AIRDATE)
    titles = tree.findall(tvrpath.EPLIST_TITLE)
    all_info = zip(seasons, epnums, airdates, titles)
    return map(lambda (w, x, y, z) : Episode(showname, w.text, x.text, y.text, z.text), all_info)
