#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import sys

try:
    import tvrage
    import xdg
except ImportError:
    print "next needs the tvrage module and the xdg module to work. See the README for more information!"
    sys.exit(-1)

from next.util import config
from next.util.constants import ConfKeys
from next.db import db
from next.show import player
from next.tui.exceptions import UserCancelled
from next.tui.tui import TUI
import os
import codecs
import sqlite3

def main():
    (options, conf, args) = config.parse_opts()


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

    # create an unbuffered, unicode supporting output file descriptor
    out = codecs.getwriter('utf8')(os.fdopen(sys.stdout.fileno(), 'w', 0))
    if args:
        # if we don't have a Cmd instance, make sure stdout is unbuffered
        # and supports unicode printing
        sys.stdout = out
        # 1. user provided a showname, find it in the db, then play it.
        s = db.find_show(conf, u' '.join(args))
        if s:
            player.play_show(conf, s)
        else:
            print u'Show "{0}" could not be found!'.format(u' '.join(args))
    else:
        # 2. user provided nothing, popup a list of options
        # make sure stdout is unbuffered and has full utf8 support 
        # (see http://wiki.python.org/moin/PrintFails)
        ui = TUI(conf, stdin=sys.stdin, stdout=out)
        try:
            ui.cmdloop()
        except KeyboardInterrupt:
            print "\nUser pressed ^C, exitting!"

if __name__ == '__main__':
	main()

