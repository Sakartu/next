#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    import tvrage
except ImportError:
    print u'next needs the tvrage module to work. See the README for more information!'
    sys.exit(-1)

from next.util import config
from next.util.constants import ConfKeys
from next.db import db
from next.show import player
from next.tui.exceptions import UserCancelled
from next.tui.tui import TUI
from next.util import util
import os
import codecs
import sqlite3

def main():
    (options, conf, args) = config.parse_opts()
    # create an unbuffered, unicode supporting output file descriptor
    # (see http://wiki.python.org/moin/PrintFails)
    out = codecs.getwriter('utf8')(os.fdopen(sys.stdout.fileno(), 'w', 0))
    # save old stdout fd to restore later if necessary
    old_stdout = sys.stdout
    # and redirect the current stdout
    sys.stdout = out

    try: # the database_path is usually the show_path, but can be defined in conf
        if ConfKeys.DB_PATH in conf:
            database_path = os.path.join(conf[ConfKeys.DB_PATH], u'next.db')
        else:
            database_path = os.path.join(conf[ConfKeys.SHOW_PATH], u'next.db')
        database_path = os.path.expanduser(os.path.expandvars(database_path))
    except KeyError:
        print(u'No show_path or database_path defined in configuration, aborting!')
        sys.exit(-1)

    # initialize the sqlite database
    try:
        if os.path.exists(database_path) or os.access(os.path.dirname(database_path), os.W_OK | os.R_OK):
            conf[ConfKeys.DB_CONN] = db.initialize(database_path)
        else:
            print(u'Could not access shows database, path "{0}" does not exist or we don\'t have write access!'.format(database_path))
            sys.exit(-1)

    except sqlite3.OperationalError:
        print(u'Could not access shows database, are the permissions correct for "{0}"?'.format(database_path))
        sys.exit(-1)

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
    # 1. there is an argument provided. this is probably a show that the user wants
    #    us to start, so let's start it.
    # 2. there are no arguments provided. provide the user with a query what he wants
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

