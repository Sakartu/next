from db import db
import os

def find_unlisted(conf):
    listed = map(lambda x : x.name, db.all_shows(conf))
    basedir = os.path.expanduser(conf['show_path'])
    all_shows = filter(lambda x : os.path.isdir(os.path.join(basedir, x)), os.listdir(basedir))
    return list(set(all_shows) - set(listed))

def find_next_ep(conf, show):
    next_season = show.season
    next_ep = show.ep + 1
    ep = db.find_ep(conf, show.sid, next_season, next_ep)
    if ep == None: #maybe forward to next season?
        next_season = show.season + 1
        next_ep = 1
        ep = db.find_ep(conf, show.sid, next_season, next_ep)
    return ep

def update_eps(conf):
    pass


