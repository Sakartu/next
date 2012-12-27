#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
# check version
if sys.version_info < (2, 6):
    print u'next needs python version >= 2.6!'
    sys.exit(-1)

# check imports
try:
    import tvrage  # flake8 ignore: # NOQA
except ImportError:
    print(u'next needs the tvrage module to work. See the README for more '
          'information!')
    sys.exit(-1)

try:
    import pyreadline as readline  # flake8 ignore: # NOQA
except ImportError:
    pass  # No readline support under Windows, oh well.

from tui_exceptions import UserCancelled
from updater import UpdateManager
from constants import ConfKeys
from tui import TUI
import message_queue
import codecs
import config
import player
import util
import db
import os


def main():
    (options, conf, args) = config.parse_opts()
    # save the basepath for later reference
    conf[ConfKeys.BASE_DIR] = os.path.dirname(os.path.realpath(__file__))
    # and create an update manager
    conf[ConfKeys.UPDATE_MANAGER] = UpdateManager(conf,
                                                  message_queue.MessageQueue())
    # create an unbuffered, unicode supporting output file descriptor
    # (see http://wiki.python.org/moin/PrintFails)
    out = codecs.getwriter('utf8')(os.fdopen(sys.stdout.fileno(), 'w', 0))
    # save old stdout fd to restore later if necessary
    old_stdout = sys.stdout
    # and redirect the current stdout
    sys.stdout = out

    db.connect(conf)

    # first check for commandline options
    if options.func:
        try:
            options.func()
        except UserCancelled:
            print "User cancelled!"
        except KeyboardInterrupt:
            print "\nUser pressed ^C!"
        sys.exit(0)

    # couple of usecases:
    # 1. there is an argument provided. this is probably a show that the user
    # wants us to start, so let's start it.
    # 2. there are no arguments provided. provide the user with a query what he
    # wants
    if args:
        # 1. user provided a showname, find it in the db, then play it.
        shows = db.find_shows(conf, u' '.join(args))
        match = util.filter_shows(shows, u' '.join(args))
        if match:
            player.play_show(conf, match)
        else:
            print u'Show "{0}" could not be found!'.format(u' '.join(args))
    else:
        # 2. user provided nothing, popup a list of options
        # restore the old stdout and build the TUI with the new out
        sys.stdout = old_stdout
        ui = TUI(conf, stdin=sys.stdin, stdout=out)
        try:
            ui.cmdloop()
        except KeyboardInterrupt:
            print "\nUser pressed ^C, exiting!"

if __name__ == '__main__':
    main()
