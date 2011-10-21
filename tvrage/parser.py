from tvrage import feeds as feeds
from xml.etree import ElementTree as ET
from tvrep import Episode
from ..util.constants.TVRage import *

def fuzzy_search(show_name):
   tree = ET.ElementTree(feeds.search(show_name))
   names = tree.findall(SEARCH_NAME)
   ids = tree.findall(SEARCH_ID)
   results = zip(map(lambda (x, y) : (x.text, y.text), names, ids))
   return results

def get_all_eps(sid):
    tree = ET.ElementTree(feeds.episode_list(sid))
    showname = tree.find().text
    seasons = tree.findall(EPLIST_SEASONNUM)
    epnums = tree.findall(EPLIST_EPNUM)
    airdates = tree.findall(EPLIST_AIRDATE)
    titles = tree.findall(EPLIST_TITLE)
    return map(lambda (w, x, y, z) : Episode(showname, w.text, x.text, y.text, z.text), zip(seasons, epnums, airdates, titles))


print get_all_eps('3332')



   
