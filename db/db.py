import sqlite3
import os
from tvr.tvrshow import Show
from tvr.tvrep import Episode
from util.constants import Keys

def initialize(path):
    conn = sqlite3.connect(os.path.expanduser(path))
    with conn:
        c = conn.cursor()
        #test to see if the shows table exists
        test = c.execute(u'''SELECT name FROM sqlite_master
                WHERE type="table"
                AND name="shows"''').fetchall()
        if not test:
            c.execute(u'''CREATE TABLE shows(sid integer, name text, season
                    integer, ep integer, maybe_finished integer)''')
            c.execute(u'''CREATE UNIQUE INDEX unique_shows ON shows(sid)''')

        #test to see if the tvr_shows table exists
        test = c.execute(u'''SELECT name FROM sqlite_master
                WHERE type="table"
                AND name="tvr_shows"''').fetchall()
        if not test:
            c.execute(u'''CREATE TABLE tvr_shows(sid integer, showname text,
                    season integer, ep integer, title text, airdate text)''')
            c.execute(u'''CREATE UNIQUE INDEX unique_tvr_shows ON tvr_shows(sid,
                    season, ep)''')

        #test to see if the locations table exists
        test = c.execute(u'''SELECT name FROM sqlite_master
                WHERE type="table"
                AND name="locations"''').fetchall()
        if not test:
            c.execute(u'''CREATE TABLE locations(sid integer, location text)''')
            c.execute(u'''CREATE UNIQUE INDEX unique_locations ON locations(sid,
                    location)''')
    return conn

def find_show(conf, show_name):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT * FROM shows 
                WHERE name like ?''', ("%" + show_name + "%",))
        shows = c.fetchall()

    if not shows:
        print u'No shows found with that name, try again!'
        return None

    if len(shows) > 2:
        print u'''Found multiple shows with the same name, picking first\
        ({0})'''.format(shows[0][0])
    return Show(shows[0])

def add_show(conf, sid, showname, season, ep):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''INSERT INTO shows VALUES (?, ?, ?, ?, 0)''', (sid, showname,
            season, ep,))

def change_show(conf, sid, season, ep):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''UPDATE shows SET season=?, ep=? where sid = ?''',
                (season, ep, sid))

def all_shows(conf):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT * FROM shows''')
        shows = c.fetchall()
        return map(Show, shows)

def store_tvr_eps(conf, eps):
    if not eps:
        return
    all_eps = find_all_eps(conf, eps[0].sid, eps[0].season)

    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        for ep in eps:
            c.execute(u'''INSERT OR IGNORE INTO tvr_shows VALUES (?, ?, ?, ?, ?, ?)''',
                    (ep.sid, ep.showname, ep.season, ep.epnum, ep.title,
                        ep.airdate))

def find_seasons(conf, sid):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT season FROM tvr_shows WHERE sid = ?''', (sid,))
        return list(set(map(lambda x : x[0], c.fetchall())))

def find_all_eps(conf, sid, season):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT * FROM tvr_shows WHERE sid = ? AND season = ?''',
                (sid, season,))
        return map(Episode.from_db_row, c.fetchall())

def find_ep(conf, sid, season, ep):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT * FROM tvr_shows WHERE sid = ? AND season = ? AND
                ep = ?''', (sid, season, ep,))
        try:
            return Episode.from_db_row(c.fetchone())
        except:
            return None

def add_location(conf, sid, location):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''INSERT OR IGNORE INTO locations VALUES (?, ?, ?, ?)''', (sid,
            location,))

def find_locations(conf, sid):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT location FROM locations WHERE sid = ?''', (sid,))
        return map(lambda x : x[0], c.fetchall())

def mark_maybe_finished(conf, sid):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''UPDATE TABLE shows SET maybe_finished = 1 WHERE sid = ?''', sid)

def mark_not_maybe_finished(conf, sid):
    with conf[Keys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''UPDATE TABLE shows SET maybe_finished = 0 WHERE sid = ?''', sid)
