from db import db
import constants
import util
import glob
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


def fix_subs(conf, show):
    '''
    A method that looks in the season folders for the given show to see if
    there are subtitles available and renames them to have the same name as the
    accompanying ep
    '''
    unstructured = conf.get(constants.ConfKeys.UNSTRUCTURED, False)
    if constants.ConfKeys.SHOW_PATH not in conf:
        return None
    bases = get_show_bases(unstructured, conf, show)
    to_rename = []
    for base in bases:
        for dirpath, dirnames, filenames in os.walk(base):
            vids = [f for f in filenames if os.path.splitext(f)[1] and
                    os.path.splitext(f)[1][1:] in constants.VIDEO_EXTS]
            subs = [f for f in filenames if os.path.splitext(f)[1] and
                    os.path.splitext(f)[1][1:] in constants.SUB_EXTS]
            no_subs = [vid for vid in vids if os.path.splitext(vid)[0] not in
                    [os.path.splitext(sub)[0] for sub in subs]]
            for vid in no_subs:
                _, s, e = util.get_ep_details(vid)
                # see if there's a scene group known for the avi
                scene_group = util.get_scene_group(vid)
                if s and e:
                    # found season and ep number, find sub
                    candidate_subs = filter(lambda name:
                            util.get_ep_details(name, season=s, ep=e)[0], subs)
                    for sub in candidate_subs:
                        if (scene_group and scene_group in sub or not
                                scene_group):
                            curname, newname = util.get_new_sub_name(sub, vid)
                            to_rename.append((dirpath, curname, newname))
    if not to_rename:
        print "Nothing to rename!"
        return
    for (path, cur, new) in to_rename:
        try:
            os.rename(os.path.join(path, cur), os.path.join(path, new))
            print "Renamed {cur} to {new} in {path}".format(cur=cur, new=new,
                    path=path)
        except OSError, e:
            print "Could not rename {cur} to {new} in {path}:".format(cur=cur,
                    new=new, path=path)
            print e


def build_ep_path(conf, show, season=None, ep=None):
    '''
    This is a helper function for the play_next method. It tries to build
    a path to the next episode. It checks all the locations in the database, as
    well as the default show location. It will return None if no path could be
    built, in case the show isn't available on the disk yet.
    '''
    if not season:
        season = show.season
    if not ep:
        ep = show.ep

    # we can never find eps for shows that are maybe_finished
    if show.maybe_finished:
        return None

    unstructured = conf.get(constants.ConfKeys.UNSTRUCTURED, False)
    if constants.ConfKeys.SHOW_PATH not in conf:
        return None
    bases = get_show_bases(unstructured, conf, show)

    for base in bases:  # search each base for the wanted ep
        if not os.path.exists(base):
            continue
        path = base[:]

        # only search for season folder if we're not running in unstructured
        # mode
        if not unstructured:
            # see which seasons there are and pick the right one
            for season_dir in os.listdir(base):
                if (str(season) in season_dir and
                os.path.isdir(os.path.join(path, season_dir))):
                    path = os.path.join(path, season_dir)

            if path == base:  # no season found
                continue

        if not unstructured:
            rexes = [re.compile("^" + x.format(show="", season=season,
                ep=ep) + "$", re.I | re.U) for x in
                constants.SHOW_REGEXES]
        else:
            show_words = util.get_words(show.name)
            rexes = [re.compile(x.format(show="".join([word + "[\W_]" for word
                in show_words]), season=season, ep=ep), re.I | re.U)
                for x in constants.SHOW_REGEXES]

        for ext in constants.VIDEO_EXTS:
            for ep_file in glob.glob(path + os.sep + '*.' + ext):
                for rex in rexes:
                    m = rex.match(os.path.split(ep_file)[1])
                    if m:
                        return ep_file

    return None  # if no ep could be found in any of the bases


def get_show_bases(unstructured, conf, show):
    '''
    A helper method that returns all the paths in which a given show may be
    found
    '''
    # we search for an ep in the default shows folder and in each folder named
    # in the locations db

    shows_base = unicode(os.path.expandvars(os.path.expanduser(
        conf[constants.ConfKeys.SHOW_PATH])))

    if not unstructured:
        bases = []
        show_words = util.normalize(util.get_words(show.name))
        for name in os.listdir(shows_base):
            full = os.path.join(shows_base, name)
            if os.path.isdir(full) and all([x in
                util.normalize(util.get_words(name.lower())) for x in
                show_words]):
                bases.append(full)
    else:
        # if we're in unstructured mode, we just set the base as the show dir
        bases = [conf[constants.ConfKeys.SHOW_PATH]]
    bases.extend(db.find_all_locations(conf, show.sid))
    bases = map(os.path.expanduser, bases)
    bases = map(os.path.expandvars, bases)
    return bases
