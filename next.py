#!/usr/bin/python -u
# -*- coding: utf-8 -*-

from util import config
from util.constants import Keys
from db import db
from show import player, admin
from tui import tui
import sys
import os
import sqlite3

def main():
    (conf, args) = config.parse_opts()

    try: #the database_path is usually the show_path, but can be defined in conf
        if Keys.DB_PATH in conf:
            database_path = os.path.join(conf[Keys.DB_PATH], u'.next.db')
        else:
            database_path = os.path.join(conf[Keys.SHOW_PATH], u'.next.db')
    except KeyError:
        print(u'No show_path or database_path defined in configuration, aborting!')
        sys.exit(-1)

    #initialize the sqlite database
    try:
        if os.path.exists(os.path.expanduser(os.path.expandvars(database_path))):
            db_conn = db.initialize(database_path)
            conf[Keys.DB_CONN] = db_conn
        else:
            print(u'Could not access shows database, path "{0}" does not exist!'.format(database_path))
            sys.exit(-1)

    except sqlite3.OperationalError as e:
        print e
        print(u'Could not access shows database, are the permissions correct for "{0}"?'.format(database_path))
        sys.exit(-1)

    # let's see if there's any new information for the tvr shows.
    admin.update_eps(conf)

    #couple of usecases:
    # 1. there is an argument provided. this is probably a show that the user wants
    #    us to start, so let's start it.
    # 2. there are no arguments provided. provide the user with a query what he wants

    if len(args):
        #1. user provided a showname, find it in the db, then play it.
        s = db.find_show(conf, u' '.join(args))
        if s:
            player.play_next(conf, s)
        else:
            print u'Show "{0}" could not be found!'.format(u' '.join(args))
    else:
        #2. user provided nothing, popup a list of options
        tui.query_user(conf)

if __name__ == '__main__':
	main()

