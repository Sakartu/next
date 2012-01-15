from next.db import db
from next.tvr import parser
import next.util.util as util
import os
import re

def find_unlisted(conf):
    '''
    This method searches in your shows folder for shows that aren't in the
    database yet
    '''
    listed = map(lambda x : x.name, db.all_shows(conf))
    basedir = os.path.expanduser(conf['show_path'])
    try:
        all_shows = [ d for d in os.listdir(basedir) if os.path.isdir(os.path.join(basedir, d)) ]
    except OSError:
        print "Could not list directory {0}".format(basedir)
        all_shows = []

    has_match = lambda s: any(x for x in listed if util.shows_match(s, x))
    return [ s for s in all_shows if not has_match(s) ]

def find_next_ep(conf, show):
    '''
    This method tries to determine which ep is next for the given show.
    '''
    next_season = show.season
    next_ep = show.ep + 1
    ep = db.find_ep(conf, show.sid, next_season, next_ep)
    if ep == None: # maybe forward to next season?
        next_season = show.season + 1
        next_ep = 1
        ep = db.find_ep(conf, show.sid, next_season, next_ep)
    return ep

def update_eps(conf):
    '''
    This method updates the eplist for a given show using the TVRage database
    '''
    # first we check tvr to see if there are any updates for our shows
    print "Updating TVRage episode database",
    all_shows = db.all_shows(conf)
    try:
        for show in all_shows:
            print '.',
            status = parser.get_status(show.sid)
            all_eps = parser.get_all_eps(show.sid)
            db.change_status(conf, show.sid, status)
            db.store_tvr_eps(conf, all_eps)
    except: # probably no internet connection
        print "Could not connect to TVRage, aborting update!"
        return

    process_maybe_finished(conf, all_shows)
    print "done."

def process_maybe_finished(conf, all_shows):
    '''
    This method walks over all the shows that are marked maybe_finished, to find
    out if they're really finished or if the database was just outdated. If a
    new ep can be found for the given show, this is set as the current ep and
    the maybe_finished mark is removed
    '''
    for show in all_shows:
        if show.maybe_finished:
            next_ep = find_next_ep(conf, show)
            if next_ep:
                db.change_show(conf, show.sid, next_ep.season, next_ep.epnum)
                db.mark_not_maybe_finished(conf, show.sid)



