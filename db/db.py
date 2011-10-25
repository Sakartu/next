import sqlite3
import os
from tvr.tvrshow import Show
from tvr.tvrep import Episode
from util.constants import ConfKeys

def initialize(path):
    '''
    This method initializes the next database at the given path. It also sets up
    the tables and returns the created db connection.
    '''
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
    '''
    This method tries to find a show in the shows database using a wildcard search
    '''
    with conf[ConfKeys.DB_CONN] as conn:
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
    '''
    This method adds a show with a given sid, name, season and ep to the
    database
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''INSERT INTO shows VALUES (?, ?, ?, ?, 0)''', (sid,
        showname, season, ep,))

def change_show(conf, sid, season, ep):
    '''
    This method changes the season and ep of a given show in the database
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''UPDATE shows SET season=?, ep=? where sid = ?''',
                (season, ep, sid))

def all_shows(conf):
    '''
    This method returns a list of Show objects for all the shows in the database
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT * FROM shows''')
        shows = c.fetchall()
        return map(Show, shows)

def store_tvr_eps(conf, eps):
    '''
    This method stores all the eps in the given eps list in the database
    '''
    if not eps:
        return

    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        for ep in eps:
            c.execute(u'''INSERT OR IGNORE INTO tvr_shows VALUES (?, ?, ?, ?, ?, ?)''',
                    (ep.sid, ep.showname, ep.season, ep.epnum, ep.title,
                        ep.airdate))

def find_seasons(conf, sid):
    '''
    This method finds all the season numbers belonging to a given show
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT season FROM tvr_shows WHERE sid = ?''', (sid,))
        return list(set(map(lambda x : x[0], c.fetchall())))

def find_all_eps(conf, sid, season):
    '''
    This method returns all the eps, wrapped in Episode objects for a given show
    and season
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT * FROM tvr_shows WHERE sid = ? AND season = ?''',
                (sid, season,))
        return map(Episode.from_db_row, c.fetchall())

def find_ep(conf, sid, season, ep):
    '''
    This method returns a single Episode object for the given show, season and
    epnumber
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT * FROM tvr_shows WHERE sid = ? AND season = ? AND
                ep = ?''', (sid, season, ep,))
        try:
            return Episode.from_db_row(c.fetchone())
        except:
            return None

def add_location(conf, sid, location):
    '''
    This method adds the given location to the show in the locations database
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''INSERT OR IGNORE INTO locations VALUES (?, ?, ?, ?)''', (sid,
            location,))

def find_all_locations(conf, sid):
    '''
    This method returns all the stored locations for the given show
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''SELECT location FROM locations WHERE sid = ?''', (sid,))
        return map(lambda x : x[0], c.fetchall())

def mark_maybe_finished(conf, sid):
    '''
    This method marks the given show as maybe_finished
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''UPDATE shows SET maybe_finished = 1 WHERE sid = ?''',
                (sid,))

def mark_not_maybe_finished(conf, sid):
    '''
    This method unmarks the show as maybe_finished
    '''
    with conf[ConfKeys.DB_CONN] as conn:
        c = conn.cursor()
        c.execute(u'''UPDATE TABLE shows SET maybe_finished = 0 WHERE sid =
        ?''', (sid,))
