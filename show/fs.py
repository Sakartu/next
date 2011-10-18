from db import db
import os
import re
from util import constants

def find_unlisted(conf):
    listed = db.all_shows(conf)
    basedir = os.path.expanduser(conf['show_path'])
    all_shows = filter(lambda x : os.path.isdir(os.path.join(basedir, x)), os.listdir(basedir))
    return list(set(all_shows) - set(listed))

def find_seasons(conf, showname):
    local = os.listdir(os.path.join(os.path.expanduser(conf['show_path']), showname))
    result = {}
    for s in local:
        numbers = map(int, re.findall(r'\d+', s))
        if numbers:
            result[max(numbers)] = s
    return result

def find_eps(conf, showname, seasons, season):
    local = os.listdir(os.path.join(os.path.expanduser(conf['show_path']), showname, seasons[season]))
    result = {}
    rexes = [re.compile(x.format(season=season, ep=r'\d*') + ext) for x in constants.SHOW_REGEXES for ext in constants.VIDEO_EXTS] 
    for s in local:
        for rex in rexes:
            m = rex.match(s)
            if m:
                result[int(m.group('ep'))] = s
    return result
