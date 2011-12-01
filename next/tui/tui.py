from next.show import player, admin
from next.db import db
from next.tvr import parser
from next.util.constants import ConfKeys, TVRage
from exceptions import UserCancelled, NoShowsException
import cmd
import random
import sqlite3
import sys

class TUI(cmd.Cmd, object):
    def __init__(self, conf={}):
        super(TUI, self).__init__()

        self.conf = conf
        self.prompt = u'next$ '
        self.intro = "Welcome to next!\n"
        self.intro += "This program helps you maintain your show watching habits\n"
        self.intro += "by logging which ep you have reached for a show. Please\n"
        self.intro += "enter a command to continue!\n"
        self.doc_header = "Commands (press help <command> to get help):"

    def cmdloop(self, intro=None):
        while True:
            try:
                cmd.Cmd.cmdloop(self)
            except UserCancelled:
                self.intro = ""
                continue

    def add_show_details(self, show):
        '''
        A helper function that is used (amongst others) by the add_show function to
        query the user as to what season and episode the user is
        '''
        #found out which season and ep the user is
        showname = show[0]
        sid = show[1]

        show_status = show[2].lower()
        if TVRage.STATUS_RETURNING in show_status:
            status = TVRage.STATUS_RETURNING
        elif TVRage.STATUS_CANCELLED in show_status:
            status = TVRage.STATUS_CANCELLED
        elif TVRage.STATUS_NEW in show_status:
            status = TVRage.STATUS_NEW
        else:
            status = TVRage.STATUS_UNKNOWN
        
        seasons = db.find_seasons(self.conf, sid)

        #then the season in the show
        if not seasons:
            print u'There are no seasons for this show!'
            return
        print u'What season are you at for {0} ({1}-{2})?'.format(showname, min(seasons), max(seasons))
        season = int(get_input(u'Season: ', range(1, len(seasons) + 1)))

        #then the ep in the season
        eps = db.find_all_eps(self.conf, sid, season)
        if not eps:
            print u'This season has no eps!'
            return
        print u'What ep are you at in season {0}?'.format(season)
        for (i, ep) in enumerate(eps):
            print u'{id:3d}. s{S:>02d}e{E:>02d} - {title}'.format(id=i + 1, S=ep.season, E=ep.epnum, title=ep.title)
        ep = int(get_input(u'Episode: ', range(1, len(eps) + 1)))

        #and finally put everything in the database
        try:
            db.add_show(self.conf, sid, showname, season, ep, status)
            print u'Successfully added {0} to the database!'.format(showname)
        except sqlite3.IntegrityError:
            print u'Show already exists, use change command to change season and ep!'

    def get_all_shows(self):
        shows = db.all_shows(self.conf)
        if not shows:
            raise NoShowsException
        return shows

    def do_play(self, line=None):
        '''
        A TUI function that plays a new episode from the user-specified show
        '''
        all_shows = db.all_shows(self.conf)
        if not all_shows:
            print u'There are no shows to play!'
            return
        if line:
            candidates = filter(lambda s : set(line.split()) <= set(s.name.lower().split()), all_shows)
            if not candidates:
                print u'No show found for "{0}"'.format(line)
                return
            #just assume the first show
            show = candidates[0]
        else:
            print u'Which show would you like to play the next ep from?'
            print_shows(self.conf, all_shows)
            number = int(get_input(u'Show number: ', range(1, len(all_shows) + 1)))
            show = all_shows[number - 1]

        if show:
            player.play_next(self.conf, show)

    def help_play(self):
        print u'Play an ep. If keywords are provided, a show with a corresponding name will be searched.'

    def do_random(self, line=None):
        '''
        A TUI function that plays a new ep from a random show
        '''
        all_shows = db.all_shows(self.conf)
        if not all_shows:
            print u'There are no shows to play!'
            return
        s = db.find_show(self.conf, random.choice(all_shows).name)
        player.play_next(self.conf, s)

    def help_random(self):
        print u'Play a random ep'

    def do_add_show(self, line=None):
        '''
        A TUI function that adds a user-specified show to the database. Uses TVRage
        to find out details about the show.
        '''
        #query the user for the show they want to add
        found_show = None
        while not found_show:
            print u'Please enter the name of the show you would like to add.'
            wanted = get_input(term=u'Showname: ')
            #find the show in tvrage
            print u'Searching for show in TVRage database... ',
            shows = parser.fuzzy_search(wanted)
            print u'done.'
            if not shows:
                print u'No shows could be found, please try other keywords!'
                return
            else:
                found_show = read_show(shows)

        print u'Getting all show eps from TVRage... ',
        episodes = parser.get_all_eps(found_show[1]) #find eps by sid
        print u'done.'
        
        print u'Storing eps in db... ',
        db.store_tvr_eps(self.conf, episodes)
        print u'done.'

        self.add_show_details(found_show)

    def help_add_show(self):
        print u'Add a show to the local database'

    def do_add_show_location(self, line=None):
        '''
        A TUI function that adds a custom location to a show. Can be used if shows
        are spread across the disk instead of centrally located.
        '''
        all_shows = db.all_shows(self.conf)
        if not all_shows:
            print u'There are no shows to add a location for!'
            return
        print u'Which show would you like to add a location for?'
        print_shows(self.conf, all_shows)
        number = int(get_input(u'Show number: ', range(1, len(all_shows) + 1)))
        show = all_shows[number - 1]
        print u'What location do you want to add?'
        location = get_input(u'Location: ')
        db.add_location(self.conf, show.sid, location)

    def help_add_show_location(self):
        print u'Add a location to a show. next will check each added location for eps to play'

    def do_change_show(self, line=None):
        '''
        A TUI function used to change the season and episode of a show where the
        user is
        '''
        try:
            all_shows = self.get_all_shows()
        except NoShowsException:
            print u'There are no shows to change!'
            return

        print u'Which show would you like to change?'
        print_shows(self.conf, all_shows)
        number = int(get_input(u'Show number: ', range(1, len(all_shows) + 1)))
        show = all_shows[number - 1]

        #then the season in the show
        seasons = db.find_seasons(self.conf, show.sid)
        if not seasons:
            print u'There are no seasons for this show!'
            return
        print u'What season are you at for {0} ({1}-{2})?'.format(show.name, min(seasons), max(seasons))
        season = int(get_input(u'Season: ', range(1, len(seasons) + 1)))

        #then the ep in the season
        eps = db.find_all_eps(self.conf, show.sid, season)
        if not eps:
            print u'This season has no eps!'
            return
        print u'What ep are you at in season {0}?'.format(season)
        for (i, ep) in enumerate(eps):
            print u'{id:3d}. s{S:>02d}e{E:>02d} - {title}'.format(id=i + 1, S=ep.season, E=ep.epnum, title=ep.title)
        ep = int(get_input(u'Episode: ', range(1, len(eps) + 1)))

        #and finally put everything in the database
        db.change_show(self.conf, show.sid, season, ep)
        print u'Successfully changed details for {0}!'.format(show.name)

    def help_change_show(self):
        print u'Change the current season and ep for a show'

    def do_scan(self, line=None):
        '''
        A TUI function that scans the user's series folder to find shows that aren't
        in the database yet, then ask the user show by show if he wants to add it
        '''
        if ConfKeys.UNSTRUCTURED in self.conf and self.conf[ConfKeys.UNSTRUCTURED]:
            print "Cannot scan disk in unstructured mode!"
            return
        unlisted = admin.find_unlisted(self.conf)
        if not unlisted:
            print u'There are no shows to add!'
            return
        for (i, path) in enumerate(unlisted):
            print u'Would you like to add {0}?'.format(path)
            answer = get_input(u'Add [yes]? ')
            if u'y' in answer.lower() or answer == '':
                print u'Searching for show in TVRage database... ',
                shows = parser.fuzzy_search(path.split(' ')[0])
                print u'done.'
                if not shows:
                    print u'No shows could be found, please try other keywords!'
                    return
                else:
                    found_show = read_show(shows)

                    print u'Getting all show eps from TVRage... ',
                    episodes = parser.get_all_eps(found_show[1]) #find eps by sid
                    print u'done.'
                    
                    print u'Storing eps in db... ',
                    db.store_tvr_eps(self.conf, episodes)
                    print u'done.'

                    self.add_show_details(found_show)

    def help_scan(self):
        print u'Scan the local shows directory for shows that aren\'t in the database yet'

    def do_list(self, line=None):
        '''
        A TUI function that lists all the shows in the database
        '''
        try:
            shows = self.get_all_shows()
        except NoShowsException:
            print u'There are no shows!'
        else:
            print_shows(self.conf, shows, extended=True)

    def help_list(self):
        print u'List all the shows in the database'

    def do_new(self, line=None):
        '''
        A TUI function that lists all the shows for which new eps are available
        '''
        try:
            all_shows = self.get_all_shows()
        except NoShowsException:
            print u'There are no shows!'
        shows = []
        for show in all_shows:
            p = player.build_ep_path(self.conf, show)
            if p:
                shows.append(show)
        if not shows:
            print u'No new eps are available for your shows!'
            return
        print "New eps are on your computer for these shows:"
        print_shows(self.conf, shows)

    def help_new(self):
        pass

    def do_update(self, line=None):
        '''
        A function that updates the internal TVRage database
        '''
        try:
            admin.update_eps(self.conf)
        except:
            print u'Update failed!'

    def help_update(self, line=None):
        print u'Update the internal TVRage database'

    def do_quit(self, line=None):
        '''
        Quits the program
        '''
        print "Exitting..."
        sys.exit(0)

    def help_quit(self):
        print u'Quit the application'

    def help_help(self):
        print u'Get help about a topic'

    def do_EOF(self, line=None):
        '''
        Quit the program
        '''
        self.do_quit()

    def preloop(self):
        self.do_help("")

    def emptyline(self):
        self.do_random()

    def postloop(self):
        print

def read_show(shows):
    print u'Which show would you like to add?'
    for (i, show) in enumerate(shows):
        print u'{0:3d}. {1}'.format(i + 1, show[0])
    number = int(get_input(u'Show number: ', range(1, len(shows) + 1)))
    return shows[number - 1]

def get_input(term=u'next$ ', possibles=None):
    '''
    A helper function that queries the user for input. Can be given a terminal
    line to show (term) and a list of possible answers the user can give. If
    possibles is None, we assume a plaintext answer.
    '''
    if possibles != None and type(possibles) != type([]):
        possibles = None

    if possibles != None:
        possibles = map(str, possibles)

    a = None
    while a == None:
        try:
            inp = raw_input(term)
        except EOFError:
            print u''
            raise UserCancelled

        if possibles != None and inp in possibles:
            a = inp
        elif possibles == None:
            a = inp
        else:
            print u'Invalid command!'
    return a

def print_shows(conf, shows, extended=False):
    '''
    A helper function that prints a list of shows, each with the reached season and ep.
    '''
    new_shows = []
    if extended:
        # find all shows that have a new ep waiting
        for show in shows:
            p = player.build_ep_path(conf, show)
            if p:
                new_shows.append(show)

    max_len = max(map(len, map(lambda x : x.name, shows))) + 3
    print u'{id:3s}  {name:{length}s}  Next ep   {status}'.format(id=u'', name=u'Show Name', length=max_len, status='Status' if extended else '')
    for (i, show) in enumerate(shows):
        print u'{id:3d}. {name:{length}s} {new}s{S:>02d}e{E:>02d} {finished}'.format(
                id=i + 1, name=show.name, length=max_len, new='*' if show in
                new_shows and not show.maybe_finished else ' ', S=show.season,
                E=show.ep, finished=show.finished if extended else "")
