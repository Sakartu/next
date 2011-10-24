from db import db
from tvr import parser
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
    #first we check tvr to see if there are any updates for our shows
    all_shows = db.all_shows(conf)
    try:
        for show in all_shows:
            all_eps = parser.get_all_eps(show.sid)
            db.store_tvr_eps(conf, all_eps)
    except:#probably no internet connection
        print "Could not connect to TVRage, aborting update!"
        return

    process_maybe_finished(conf, all_shows)

def process_maybe_finished(conf, all_shows):
    for show in all_shows:
        if show.maybe_finished:
            next_ep = find_next_ep(show)
            if next_ep:
                db.change_show(conf, show.sid, next_ep.season, next_ep.epnum)
                db.mark_not_maybe_finished(conf, show.sid)

    


    


