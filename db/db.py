import sqlite3
import logging
from show import Show

def initialize(path):
    conn = sqlite3.connect(path)
    with conn:
        c = conn.cursor()
        #test to see if the shows table exists
        test = c.execute("""SELECT name FROM sqlite_master
                WHERE type='table'
                AND name='shows'""").fetchall()
        if not test:
            c.execute("""CREATE TABLE shows(name text, season integer, ep integer)""")
        
    return conn

def find_show(conf, show_name):
    conn = conf['db_conn']
    with conn:
        c = conn.cursor()
        c.execute("""SELECT * FROM shows 
                WHERE name like '%?%'""", (show_name,))
        shows = c.fetchall()

    if not shows:
        logging.log("No shows found with that name, try again!")
        return None

    if len(shows) > 2:
        logging.log("Found multiple shows with the same name, picking first ({0})".format(shows[0][0]))
    return Show(shows[0])

def add_show(conf, showname, season, ep):
    conn = conf['db_conn']
    with conn:
        c = conn.cursor()
        c.execute('INSERT INTO shows VALUES (?, ?, ?)', (showname, season, ep,))

def change_show(conf, showname, season, ep):
    conn = conf['db_conn']
    with conn:
        c = conn.cursor()
        c.execute("""UPDATE shows SET season=?, ep=? where showname like '%?%')""", (season, ep,showname,))
