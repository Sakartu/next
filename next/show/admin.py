from db import db
from tvr import parser
from urllib2 import URLError
import util.util as util
import os


def find_unlisted(conf):
    '''
    This method searches in your shows folder for shows that aren't in the
    database yet
    '''
    listed = map(lambda x: x.name, db.all_shows(conf))
    basedir = os.path.expanduser(conf['show_path'])
    try:
        all_shows = [d for d in os.listdir(basedir) if os.path.isdir(
            os.path.join(basedir, d))]
    except OSError:
        print "Could not list directory {0}".format(basedir)
        all_shows = []

    has_match = lambda s: any(x for x in listed if util.shows_match(s, x))
    return [s for s in all_shows if not has_match(s)]


def find_next_ep(conf, show):
    '''
    This method tries to determine which ep is next for the given show.
    '''
    next_season = show.season
    next_ep = show.ep + 1
    ep = db.find_ep(conf, show.sid, next_season, next_ep)
    if ep == None:  # maybe forward to next season?
        next_season = show.season + 1
        next_ep = 1
        ep = db.find_ep(conf, show.sid, next_season, next_ep)
    return ep


def update_eps(conf, messages=None):
    '''
    This method updates the eplist for a given show using the TVRage database
    '''
    # Below method is necessary since update_eps may be called in parallel with
    # the ep player, and if so messages should be printed after the output of
    # the player
    def msg(m):
        if messages:
            messages.push(str(m))
        else:
            print str(m)

    # first we check tvr to see if there are any updates for our shows
    msg("Updating TVRage episode cache...")
    all_shows = db.all_shows(conf)
    try:
        for show in all_shows:
            if messages:
                print '.',

            all_eps = []
            for i in range(4):  # try updating 4 times, tvrdb is a bit flakey
                try:
                    status = parser.get_status(show.sid)
                    all_eps = parser.get_all_eps(show.sid)
                    break
                except URLError:
                    continue

            if not all_eps:
                raise URLError

            db.change_status(conf, show.sid, status)
            db.store_tvr_eps(conf, all_eps)
    except URLError, e:  # probably no internet connection
        msg('\nCould not connect to TVRage, will not update tvrage episode'
        ' cache:')
        msg(e.reason)
        return
    except Exception, e:  # probably no internet connection
        msg('\nCould not connect to TVRage, will not update tvrage episode'
        ' cache.')
        if hasattr(e, 'code'):
            msg('Received status code:')
            msg(e.code)
        return

    try:
        process_maybe_finished(conf, all_shows)
    except:
        msg(u'maybe_finished processing failed for tvrage episode cache '
        'update, database may be in an inconsistant state!')
        raise Exception
    msg("Done!")


def process_maybe_finished(conf, all_shows):
    '''
    This method walks over all the shows that are marked maybe_finished, to
    find out if they're really finished or if the database was just outdated.
    If a new ep can be found for the given show, this is set as the current ep
    and the maybe_finished mark is removed
    '''
    for show in all_shows:
        if show.maybe_finished:
            next_ep = find_next_ep(conf, show)
            if next_ep:
                db.change_show(conf, show.sid, next_ep.season, next_ep.epnum)
                db.mark_not_maybe_finished(conf, show.sid)


def clean_db(conf):
    '''
    This method cleans the database of shows that have leftover information in
    the tvrage cache, but are no longer present in the rest of the database
    '''
    show_ids = db.find_show_ids(conf)
    tvr_ids = db.find_tvr_ids(conf)
    to_clean = [i for i in tvr_ids if i not in show_ids]
    db.clear_cache(conf, ((x,) for x in to_clean))
    print u'Cleared out shows with ids {0}'.format(
            ' and '.join(map(str, to_clean)))
