import constants
import logging
import os
import re

def play_next(conf, show):
    try:
        cmd_line = conf[constants.Keys.PLAYER_CMD]
        shows_base = conf[constants.Keys.SHOW_PATH]
        ep_path = build_ep_path(shows_base, show)
        #play the show
        logging.log("Starting show '{0}'!".format(ep_path))
        #update the db
        logging.log(cmd_line)
    except:
        logging.log('Could not start player, is your player_cmd line correct?')

def build_ep_path(base, show):
    result = base
    seasons = os.listdir(os.path.join(base, show.name))
    
    #see which seasons there are and pick the right one
    for season in seasons:
        if show.season in season:
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
