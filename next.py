#!/usr/bin/env python

from util import config, constants, logging
from db import db
from show import player
from tui import tui
import sys
import sqlite3

def main():
    (conf, args) = config.parse_opts()

    try: #the database_path is usually the show_path, but can be defined in conf
        if constants.Keys.DB_PATH in conf:
            database_path = conf[constants.Keys.DB_PATH]
        else:
            database_path = conf[constants.Keys.SHOW_PATH]
    except KeyError:
        logging.log("No show_path or database_path defined in configuration, aborting!")
        sys.exit(-1)

    #initialize the sqlite database
    try:
        db_conn = db.initialize(database_path)
        conf['db_conn'] = db_conn
    except sqlite3.OperationalError:
        logging.log("Could not access shows database, are the permissions correct for '{0}?'".format(database_path))
        sys.exit(-1)

    #couple of usecases:
    # 1. there is an argument provided. this is probably a show that the user wants
    #    us to start, so let's start it.
    # 2. there are no arguments provided. provide the user with a query what he wants

    if len(args):   #1.
        #user provided a showname, find it in the db, then play it.
        s = db.find_show(conf, args)
        player.play_next(conf, s)
    else:           #2.
        #user provided nothing, popup a list of options
        tui.tui.query_user(conf, db_conn)

if __name__ == '__main__':
	main()

