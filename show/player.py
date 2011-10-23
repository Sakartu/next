from util import constants
from util.constants import Keys
from show import admin
from db import db
import os
import sys
import re
import time
import subprocess

def play_next(conf, show):
    cmd_line = conf[Keys.PLAYER_CMD]
    ep_path = build_ep_path(conf, show)
    if not ep_path:
        print u'Could not find s{S:02d}e{E:02d} for {name}!'.format(S=show.season, E=show.ep, name=show.name)
        return
    command = cmd_line.split(' ') + [ep_path]
    #play the show
    print u'Starting show "{0}"!'.format(ep_path)
    try:
        subprocess.call(command)
    except KeyboardInterrupt:
        sys.stdout.flush()
        time.sleep(1) #give the movie player some time to clean up
    #update the db
    print u'Should I update the database for you?'
    answer = raw_input(u'Update [yes]? ')
    if u'y' in answer.lower() or answer == '':
        next_ep = admin.find_next_ep(conf, show)
        if next_ep:
            db.change_show(conf, show.sid, next_ep.season, next_ep.epnum)
        else:
            print u'No information about new eps yet, try updating later!'
            db.mark_finished(conf, show.sid)
        print u'Player stopped, database updated.'
    else:
        print u'Database unmodified.'

def build_ep_path(conf, show):
    # we search for an ep in the default shows folder and in each folder named
    # in the locations db
    path = None
     
    bases = [os.path.join(conf[Keys.SHOW_PATH], show.name)]
    bases.extend(db.find_locations(conf, show.sid))
    bases = map(os.path.expanduser, bases)
    bases = map(os.path.expandvars, bases)

    for base in bases: #search each base for the wanted ep
        if not os.path.exists(base):
            continue
        path = base[:]
        #see which seasons there are and pick the right one
        for season in os.listdir(base):
            if str(show.season) in season and os.path.isdir(os.path.join(path,
                season)):
                path = os.path.join(path, season)

        if path == base: #no season found
            continue

        rexes = [re.compile(x.format(season=show.season, ep=show.ep) + ext) for
                x in constants.SHOW_REGEXES for ext in constants.VIDEO_EXTS] 
        for ep in os.listdir(path):
            for rex in rexes:
                m = rex.match(ep)
                if m:
                    path = os.path.join(path, ep)
                    return path

    return None #if no ep could be found in any of the bases

