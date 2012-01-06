from next.util.constants import ConfKeys
from next.show import admin
from next.db import db
import next.util.util as util
import next.util.fs as fs
import subprocess
import time
import sys

def play_show(conf, show):
    another = True
    while another:
        show = play_next(conf, show)
        # ask the user for another ep
        if not show or not fs.build_ep_path(conf, show):
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
    ep_path = fs.build_ep_path(conf, show)
    if not ep_path:
        print u'Could not find s{S:02d}e{E:02d} for {name}, ep not available or marked maybe_finished?'.format(S=show.season, E=show.ep, name=show.name)
        return
    command = cmd_line.split(' ') + [ep_path]
    if not play(command, show):
        return

    # update the db
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

def play(command, show):
    '''
    A helper method that executes the given command
    '''
    # play the show
    print u'Starting S{S:02}E{E:02} of {name}!'.format(S=show.season, E=show.ep, name=show.name)
    try:
        print " ".join(command)
        subprocess.call(command)
        return True
    except KeyboardInterrupt:
        sys.stdout.flush()
        time.sleep(1) # give the movie player some time to clean up
        return True
    except OSError:
        # maybe the player isn't installed or something?
        print u'An error occurred while starting the player, check your config!'
        return False

