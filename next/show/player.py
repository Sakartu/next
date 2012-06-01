from util.constants import ConfKeys
from show import admin
from db import db
import util.fs as fs
import subprocess
import threading
import datetime
import Queue
import shlex
import time
import sys
import os


def play_show(conf, show):
    another = True
    while another:
        show = play_next(conf, show)
        # ask the user for another ep
        if not show or not fs.build_ep_path(conf, show):
            break

        answer = 'no'
        if conf.get(ConfKeys.ASK_ANOTHER, True):
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
    show.path = ep_path
    if not ep_path:
        print u'Could not find s{S:02d}e{E:02d} for {name}, ep not available '
        'or marked maybe_finished?'.format(S=show.season, E=show.ep,
                name=show.name)
        return
    command = cmd_line.split(' ') + [ep_path]
    before = datetime.datetime.now()
    if not play(command, show, conf):
        return
    after = datetime.datetime.now()

    # update the db
    length_detection = conf.get(ConfKeys.LENGTH_DETECTION, 0)
    # can't use total_seconds() due to 2.6 compatibility :(
    delta = (after - before)
    if (delta.seconds + delta.days * 24 * 3600) <= length_detection * 60:
        next_ep = admin.find_next_ep(conf, show)
        if next_ep:
            return show
        else:
            return None

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
                show.maybe_finished = True
            # call post-processing script
            post_processing = conf.get(ConfKeys.POSTPROCESSING, '')
            if post_processing:
                for script in post_processing.split(','):
                    to_call = os.path.expandvars(os.path.expanduser(script))
                    to_call = shlex.split(to_call)
                    try:
                        # fill all the parameters with info from show
                        to_call = [x.format(**show.__dict__) for x in to_call]
                    except KeyError, e:
                        print u'You used a post-processing parameter that '
                        'doesn\'t exist: {0}, skipping hook "{1}"'.format(
                                str(e).strip(), str(script))
                        continue
                    subprocess.call(to_call)

            return show
    except:
        print ''
    print u'Database unmodified.'
    return


def play(command, show, conf):
    '''
    A helper method that executes the given command
    '''
    # play the show
    print u'Starting S{S:02}E{E:02} of {name}!'.format(S=show.season,
            E=show.ep, name=show.name)

    # This Timer will fire an episode cache update if the user is watching for
    # at least 5 minutes, otherwise nothing will happen
    update_timer = threading.Timer(60 * 5, admin.update_eps, args=(conf,
        False,))

    class PlayThread(threading.Thread):
        def __init__(self, result):
            threading.Thread.__init__(self)
            self.result = result

        def run(self):
            try:
                subprocess.call(command)
                self.result.put(True)
            except KeyboardInterrupt:
                # user killed the player himself
                self.result.put(True)
            except:
                # player probably doesn't exist or isn't properly configged
                print u'An error occurred while starting the player, check '
                'your config!'
                self.result.put(False)
            finally:
                update_timer.cancel()

    # This separate thread will start playing the ep and cancel the above Timer
    # to make sure the user doesn't have to wait for the database update
    result = Queue.Queue()
    play_thread = PlayThread(result)

    try:
        # Start the ep
        play_thread.start()
        # and at the same time try to update the database
        update_timer.start()
        play_thread.join()
        return result.get(block=False)
    except KeyboardInterrupt:
        sys.stdout.flush()
        time.sleep(1)  # give the movie player some time to clean up
        return True
