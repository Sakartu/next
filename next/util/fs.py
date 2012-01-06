from next.db import db
import constants
import util
import os
import re

def build_sub_path(path):
    '''
    A helper function to tell you whether subs are available for a given ep and
    if so, return the full path to the subtitle file
    '''
    if not path:
        return None
    (base, _) = os.path.splitext(path)
    for ext in constants.SUB_EXTS:
        sub_path = base + '.' + ext
        if os.path.exists(sub_path):
            return sub_path
    return None

def fix_subs(ep):
    pass

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

    unstructured = conf.get(constants.ConfKeys.UNSTRUCTURED, False)
    if constants.ConfKeys.SHOW_PATH not in conf:
        return None

    shows_base = os.path.expandvars(os.path.expanduser(conf[constants.ConfKeys.SHOW_PATH]))
    path = None
    
    if not unstructured:
        bases = []
        show_words = util.get_words(show.name)
        for name in os.listdir(shows_base):
            full = os.path.join(shows_base, name)
            if os.path.isdir(full) and all([x in util.get_words(name.lower()) for x in show_words]):
                bases.append(full)
    else:
        # if we're in unstructured mode, we just set the base as the show dir
        bases = [conf[constants.ConfKeys.SHOW_PATH]]
    bases.extend(db.find_all_locations(conf, show.sid))
    bases = map(os.path.expanduser, bases)
    bases = map(os.path.expandvars, bases)

    for base in bases: # search each base for the wanted ep
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
            show_words = util.get_words(show.name)
            rexes = [re.compile(x.format(show="".join([word + "\W" for word in
                show_words]), season=show.season, ep=show.ep) + ext, re.I) for x in
                constants.SHOW_REGEXES for ext in constants.VIDEO_EXTS] 
        for ep in os.listdir(path):
            for rex in rexes:
                m = rex.match(ep)
                if m:
                    path = os.path.join(path, ep)
                    return path

    return None # if no ep could be found in any of the bases
