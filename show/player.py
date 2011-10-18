from util import constants
from db import db
import os
import sys
import re
import time
import subprocess

def play_next(conf, show):
    cmd_line = conf[constants.Keys.PLAYER_CMD]
    shows_base = conf[constants.Keys.SHOW_PATH]
    ep_path = build_ep_path(shows_base, show)
    command = cmd_line.split(' ') + [ep_path]
    #play the show
    print "Starting show '{0}'!".format(ep_path)
    try:
        subprocess.call(command)
    except KeyboardInterrupt:
        sys.stdout.flush()
        time.sleep(1) #give the movie player some time to clean up
    #update the db
    db.change_show(conf, show.name, show.season, show.ep + 1)
    print "Player stopped, database updated."

def build_ep_path(base, show):
    result = os.path.join(os.path.expanduser(base), show.name)
    seasons = os.listdir(result)
    
    #see which seasons there are and pick the right one
    for season in seasons:
        if str(show.season) in season:
            result = os.path.join(result, season)

    eps = os.listdir(result)
    #build a list of regexes using the given show season and ep
    rexes = [re.compile(x.format(season=show.season, ep=show.ep) + ext) for x in constants.SHOW_REGEXES for ext in constants.VIDEO_EXTS] 
    for ep in eps:
        for rex in rexes:
            m = rex.match(ep)
            if m:
                result = os.path.join(result, ep)
    return result
