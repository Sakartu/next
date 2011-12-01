from next.util import constants
from next.util.constants import ConfKeys
from next.show import admin
from next.db import db
import os
import sys
import re
import time
import subprocess

def play_show(conf, show):
    another = True
    while another:
        show = play_next(conf, show)
        # ask the user for another ep
        if not show:
            break
        print u"Shall I play another ep?"
        answer = raw_input(u'Another [yes]? ')
        if u'y' not in answer.lower() and answer.strip() != '':
            another = False

def play_next(conf, show):
    '''
    This method plays the next episode for the given show.
    '''
    cmd_line = conf[ConfKeys.PLAYER_CMD]
    ep_path = build_ep_path(conf, show)
    if not ep_path:
        print u'Could not find s{S:02d}e{E:02d} for {name}, ep not available or marked maybe_finished?'.format(S=show.season, E=show.ep, name=show.name)
        return
    command = cmd_line.split(' ') + [ep_path]
    if not play(command, show):
        return

    #update the db
    print u'Should I update the database for you?'
    try:
        answer = raw_input(u'Update [yes]? ')
        if u'y' in answer.lower() or answer.strip() == '':
            next_ep = admin.find_next_ep(conf, show)
            if next_ep:
                db.change_show(conf, show.sid, next_ep.season, next_ep.epnum)
                show.season = next_ep.season
                show.ep = next_ep.epnum
            else:
                print u'No information about new eps yet, try updating later!'
                db.mark_maybe_finished(conf, show.sid)
            return show
    except:
        print ''
    print u'Database unmodified.'
    return

def build_ep_path(conf, show):
    '''
    This is a helper function for the play_next method. It tries to build a path
    to the next episode. It checks all the locations in the database, as well as
    the default show location. It will return None if no path could be built, in
    case the show isn't available on the disk yet.
    '''
    # we can never find eps for shows that are maybe_finished
    if show.maybe_finished:
        return None

    # we search for an ep in the default shows folder and in each folder named
    # in the locations db

    unstructured = conf.get(ConfKeys.UNSTRUCTURED, False)
    if ConfKeys.SHOW_PATH not in conf:
        return None

    shows_base = os.path.expandvars(os.path.expanduser(conf[ConfKeys.SHOW_PATH]))
    path = None
    
    if not unstructured:
        bases = []
        show_words = get_words(show.name)
        for name in os.listdir(shows_base):
            full = os.path.join(shows_base, name)
            if os.path.isdir(full) and all([x in get_words(name.lower()) for x in show_words]):
                bases.append(full)
    else:
        # if we're in unstructured mode, we just set the base as the show dir
        bases = [conf[ConfKeys.SHOW_PATH]]
    bases.extend(db.find_all_locations(conf, show.sid))
    bases = map(os.path.expanduser, bases)
    bases = map(os.path.expandvars, bases)

    for base in bases: #search each base for the wanted ep
        if not os.path.exists(base):
            continue
        path = base[:]

        # only search for season folder if we're not running in unstructured mode
        if not unstructured:
            # see which seasons there are and pick the right one
            for season in os.listdir(base):
                if str(show.season) in season and os.path.isdir(os.path.join(path,
                    season)):
                    path = os.path.join(path, season)

            if path == base: # no season found
                continue

        if not unstructured:
            rexes = [re.compile("^" + x.format(show="", season=show.season, ep=show.ep) + ext + "$", re.I) for
                    x in constants.SHOW_REGEXES for ext in constants.VIDEO_EXTS] 
        else:
            show_words = get_words(show.name)
            rexes = [re.compile(x.format(show="".join([word + ".*" for word in
                show_words]), season=show.season, ep=show.ep) + ext, re.I) for x in
                constants.SHOW_REGEXES for ext in constants.VIDEO_EXTS] 
        for ep in os.listdir(path):
            for rex in rexes:
                m = rex.match(ep)
                if m:
                    path = os.path.join(path, ep)
                    return path

    return None #if no ep could be found in any of the bases

def get_words(text):
    '''
    Utility function that splits a given text on spaces, dots and _'s, then
    returns only those parts which contain only word characters
    '''
    # filter out dots, underscores and multiple spaces
    text = re.sub('\s+', ' ', text.lower())
    text = re.sub('[\._]', ' ', text)
    # split on spaces
    words = text.split()
    # filter for only normal words (handy in case of "Doctor Who (2005)"
    return filter(lambda x : re.compile(r'^\w*$').match(x), words)

def play(command, show):
    '''
    A helper method that executes the given command
    '''
    #play the show
    print u'Starting S{S:02}E{E:02} of {name}!'.format(S=show.season, E=show.ep, name=show.name)
    try:
        print " ".join(command)
        subprocess.call(command)
        return True
    except KeyboardInterrupt:
        sys.stdout.flush()
        time.sleep(1) #give the movie player some time to clean up
        return True
    except OSError:
        # maybe the player isn't installed or something?
        print u'An error occurred while starting the player, check your config!'
        return False
