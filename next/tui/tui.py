from next.show import player, admin
from next.db import db
from next.tvr import parser
from next.util.constants import ConfKeys
import next.util.util as util
import next.util.fs as fs
from next.tui.exceptions import UserCancelled, NoShowsException
import sys
import cmd
import random
import sqlite3
from datetime import datetime

class TUI(cmd.Cmd, object):
    def __init__(self, conf={}, stdin=sys.stdin, stdout=sys.stdout):
        cmd.Cmd.__init__(self, stdin=stdin, stdout=stdout)

        self.conf = conf
        self.prompt = u'next$ '
        self.intro = u'Welcome to next!\n'
        self.intro += u'This program helps you maintain your show watching habits\n'
        self.intro += u'by logging which ep you have reached for a show. Please\n'
        self.intro += u'enter a command to continue!\n'
        self.doc_header = u'Commands (press help <command> to get help):'

    def cmdloop(self):
        while True:
            try:
                cmd.Cmd.cmdloop(self)
            except UserCancelled:
                self.intro = u''
                continue

    def preloop(self):
        self.do_help("")

    def postloop(self):
        print

    def precmd(self, line):
        if line == "EOF":
            raise UserCancelled
        else:
            return line

    def do_play(self, line=None):
        '''
        A TUI function that plays a new episode from the user-specified show. If
        keywords are provided, a show with a corresponding name will be searched
        '''
        show = self.ask_show(line, u'Which show would you like to play the next ep from?')

        player.play_show(self.conf, show)

    def help_play(self):
        util.print_formatted(u'''\
        Play an ep. If keywords are provided, a show with a corresponding
        name will be searched.''')

    def do_random(self, line=None):
        '''
        A TUI function that plays a new ep from a random show
        '''
        try:
            all_shows = self.get_all_shows()
        except NoShowsException:
            print u'There are no shows to play!'
            return
        choice = random.choice(all_shows)
        shows = db.find_shows(self.conf, choice.name)
        s = util.filter_shows(shows, choice.name)
        player.play_next(self.conf, s)

    def help_random(self):
        print u'Play a random ep'

    def do_add_show(self, line=None):
        '''
        A TUI function that adds a user-specified show to the database. Uses TVRage
        to find out details about the show. If keywords are provided, a show with
        a corresponding name will be searched
        '''

        wanted = ''
        if ConfKeys.FUNC_ARGS in self.conf and self.conf[ConfKeys.FUNC_ARGS]:
            wanted = u' '.join(self.conf[ConfKeys.FUNC_ARGS])
        elif line:
            wanted = line

        # query the user for the show they want to add
        found_show = None
        while not found_show:
            if not wanted:
                print u'Please enter the name of the show you would like to add.'
                wanted = self.get_input(term=u'Showname: ')
            # find the show in tvrage
            print u'Searching for show in TVRage database... ',
            try:
                shows = parser.fuzzy_search(wanted)
            except:
                # possibly no internet or no conn to tvr
                print u'\nCould not connect to tvr, try again later!'
                return
            print u'done.'
            if not shows:
                print u'No shows could be found, please try other keywords!'
                return
            else:
                found_show = self.read_show(shows)
            wanted = ''

        print u'Getting all show eps from TVRage... ',
        episodes = parser.get_all_eps(found_show[1]) # find eps by sid
        print u'done.'
        
        print u'Storing eps in db... ',
        db.store_tvr_eps(self.conf, episodes)
        print u'done.'

        self.add_show_details(found_show)

    def help_add_show(self):
        print u'Add a show to the local database'
    
    def do_del_show(self, line=None):
        '''
        A TUI function used to delete a show from the database. If keywords are
        provided, a show with a corresponding name will be searched
        '''
        show = self.ask_show(line, u'Which show would you like to delete?')
        
        print u'Are you ABSOLUTELY sure you want to delete the show?'
        answer = self.get_input(u'Delete [no]? ')
        if 'y' in answer.lower():
            try:
                db.delete_show(self.conf, show.sid)
            except:
                print u'Something went wrong while deleting, database reverted'
            print u'Successfully removed {name} from the database!'.format(
                    name=show.name)
        else:
            print u'Database unmodified.'

    def help_del_show(self, line=None):
        print u'Remove a show from the local database'

    def do_add_show_location(self, line=None):
        '''
        A TUI function that adds a custom location to a show. Can be used if shows
        are spread across the disk instead of centrally located. If keywords are
        provided, a show with a corresponding name will be searched
        '''
        show = self.ask_show(line, u'Which show would you like to add a location for?')
            
        print u'What location do you want to add?'
        location = self.get_input(u'Location: ')
        db.add_location(self.conf, show.sid, location)

    def help_add_show_location(self):
        util.print_formatted(u'''\
        Add a location to a show. next will check each added location for eps to
        play''')

    def do_change_show(self, line=None):
        '''
        A TUI function used to change the season and episode of a show where the
        user is. If keywords are provided, a show with a corresponding name will
        be searched
        '''
        show = self.ask_show(line, u'Which show would you like to change?')

        season = self.ask_show_season(show.name, show.sid)
        ep = self.ask_show_ep(show.sid, season)

        # and finally put everything in the database

        db.change_show(self.conf, show.sid, season, ep)
        print u'Successfully changed details for {0}!'.format(show.name)

    def help_change_show(self):
        print u'Change the current season and ep for a show'

    def do_further_show(self, line=None):
        '''
        A TUI function used to further the season and episode of a show where
        the user is. If keywords are provided, a show with a corresponding name
        will be searched
        '''
        show = self.ask_show(line, u'Which show would you like to further?')

        next_ep = admin.find_next_ep(self.conf, show)
        if not next_ep:
            print u'No information about new eps yet, try updating later!'
            db.mark_maybe_finished(self.conf, show.sid)
            show.maybe_finished = True
            return

        db.change_show(self.conf, show.sid, next_ep.season, next_ep.epnum)
        print u'Successfully furthered {0}!'.format(show.name)

    def help_further_show(self):
        print u'Set a show to the next episode without playing the ep'

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
        for path in unlisted:
            print u'Would you like to add {0}?'.format(path)
            answer = self.get_input(u'Add [yes]? ')
            if u'y' in answer.lower() or answer == '':
                print u'Searching for show in TVRage database... ',

                shows = parser.fuzzy_search(" ".join(util.get_words(path)))
                print u'done.'
                if not shows:
                    print u'No shows could be found, please try other keywords!'
                    return
                else:
                    found_show = self.read_show(shows)

                    print u'Getting all show eps from TVRage... ',
                    episodes = parser.get_all_eps(found_show[1]) # find eps by sid
                    print u'done.'
                    
                    print u'Storing eps in db... ',
                    db.store_tvr_eps(self.conf, episodes)
                    print u'done.'

                    self.add_show_details(found_show)

    def help_scan(self):
        util.print_formatted(u'''\
        Scan the local shows directory for shows that aren\'t in the database
        yet''')

    def do_list(self, line=None):
        '''
        A TUI function that lists all the shows in the database
        '''
        try:
            shows = self.get_all_shows()
        except NoShowsException:
            print u'There are no shows!'
            return
        else:
            self.print_shows_detailed(shows, display_new=True, display_subs=True, display_status=True)

    def help_list(self):
        util.print_formatted(u'''\
        List all the shows in the database. A single * in front of an ep means
        there\'s a new ep available on the drive. A double * in front of an ep
        means there\'s a new ep available and it also has subtitles.''')

    def do_new(self, line=None):
        '''
        A TUI function that lists all the shows for which new eps are available
        '''
        try:
            all_shows = self.get_all_shows()
        except NoShowsException:
            print u'There are no shows!'
            return
        shows = []
        for show in all_shows:
            p = fs.build_ep_path(self.conf, show)
            if p:
                shows.append(show)
        if not shows:
            print u'No new eps are available for your shows!'
            return
        print "New eps are on your computer for these shows (* = has subs):"
        self.print_shows_detailed(shows, display_subs=True)

    def help_new(self):
        util.print_formatted(u'''\
        Prints a list of all shows for which there are new eps available.
        A * in front of an ep means that there are subtitles available for the
        new ep''')

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

    def do_fix_subs(self, line=None):
        '''
        A function that fixes the names of subtitle files for a given show. If
        keywords are provided, a show with a corresponding name will be searched
        '''
        show = self.ask_show(line, 
                    u'For which show do you want to fix the subtitles?')

        fs.fix_subs(self.conf, show)

    def help_fix_subs(self):
        util.print_formatted(u'''\
        Recursively check subtitle names and rename to name of
        corresponding ep file if necessary''')

    def do_quit(self, line=None):
        '''
        Quits the program
        '''
        print "Exiting..."
        sys.exit(0)

    def help_quit(self):
        print u'Quit the application'

    def help_help(self):
        print u'Get help about a topic'

    def add_show_details(self, show):
        '''
        A helper function that is used (amongst others) by the add_show function to
        query the user as to what season and episode the user is
        '''
        name = show[0]
        sid = show[1]
        status = show[2]
        
        # found out which season and ep the user is
        season = self.ask_show_season(name, sid)
        ep = self.ask_show_ep(sid, season)

        # and finally put everything in the database
        try:
            db.add_show(self.conf, sid, name, season, ep, status)
            print u'Successfully added {0} to the database!'.format(name)
        except sqlite3.IntegrityError:
            print u'Show already exists, use change command to change season and ep!'

    def ask_show_season(self, name, sid):
        '''
        Convenience function to ask the user which season he is given the name
        and sid
        '''
        # then the season in the show
        seasons = db.find_seasons(self.conf, sid)
        if not seasons:
            print u'There are no seasons for this show!'
            return
        print u'What season are you at for {0} ({1}-{2})?'.format(name, min(seasons), max(seasons))
        return int(self.get_input(u'Season: ', range(1, len(seasons) + 1)))

    def ask_show_ep(self, sid, season):
        '''
        Convenience function to ask the user which ep he is given the sid and
        season
        '''
        # then the ep in the season
        eps = db.find_all_eps(self.conf, sid, season)
        if not eps:
            print u'This season has no eps!'
            return
        print u'What ep are you at in season {0} (* = unaired)?'.format(season)
		
		# get the current day 
        today = datetime.today().date()
        for (i, ep) in enumerate(eps):
            print u'{id:3d}. {unaired}s{S:>02d}e{E:>02d} - {title}'.format(id=i + 1, S=ep.season, E=ep.epnum, title=ep.title, 
                unaired=u'*' if datetime.strptime(ep.airdate, '%Y-%m-%d').date() > today else ' ')

        # and ask the ep
        ep = int(self.get_input(u'Episode: ', range(1, len(eps) + 1)))
        return ep

    def get_all_shows(self):
        '''
        Helper method that returns all shows from database, or NoShowsException
        if there are none
        '''
        shows = db.all_shows(self.conf)
        if not shows:
            raise NoShowsException
        return shows

    def ask_show(self, line, header):
        '''
        A method that tries to find out which show a user means, using
        various methods. It checks the line to see if the user filled in
        anything there. If not, it checks to see whether the conf contains a
        hint to which show the user means in case of a CLI call. Finally, if
        none of these work, it'll list all the shows and ask the user which one
        it wants.

        This method guarantees to produce a show, or keep asking the user. Only
        a ^C can let the user exit.
        '''
        show = None
        if line:
            while not show:
                candidates = db.find_shows(self.conf, line)
                show = util.filter_shows(candidates, line)
        elif ConfKeys.FUNC_ARGS in self.conf and self.conf[ConfKeys.FUNC_ARGS]:
            while not show:
                name = u' '.join(self.conf[ConfKeys.FUNC_ARGS])
                shows = db.find_shows(self.conf, name)
                show = util.filter_shows(shows, name)
        else:
            try:
                all_shows = self.get_all_shows()
            except NoShowsException:
                util.print_formatted(u'There are no shows!')
                return

            util.print_formatted(header)
            self.print_shows_detailed(all_shows)
            number = int(self.get_input(u'Show number: ', range(1, len(all_shows) + 1)))
            show = all_shows[number - 1]
        return show

    def read_show(self, shows):
        print u'Which show would you like to add?'
        for (i, show) in enumerate(shows):
            print u'{0:3d}. {1}'.format(i + 1, show[0])
        number = int(self.get_input(u'Show number: ', range(1, len(shows) + 1)))
        return shows[number - 1]

    def get_input(self, term=u'next$ ', possibles=None):
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

    def print_shows_detailed(self, shows, display_new=False, display_subs=False, display_status=False):
        '''
        A helper function that prints a list of shows, each with the reached season and ep.
        '''
        new_shows = {}
        if display_new or display_subs:
            # find all shows that have a new ep waiting
            for show in shows:
                p = fs.build_ep_path(self.conf, show)
                subp = fs.build_sub_path(p)
                if p:
                    new_shows[show.name] = subp

        max_len = max(map(len, map(lambda x : x.name, shows))) + 3
        print u'{id:3s}  {name:{length}s}   Next ep   {status}'.format(id=u'', 
            name=u'Show Name', length=max_len, status='Status' if 
            display_status else '')
        for (i, show) in enumerate(shows):
            newline = '  '
            if show.name in new_shows and not show.maybe_finished:
                newline = '*' if display_new else ' '
                if display_subs and new_shows[show.name]:
                    newline += '*'
                else:
                    newline += ' '
            print u'{id:3d}. {name:{length}s} {new}s{S:>02d}e{E:>02d}    {status}'.format(
                id=i + 1, name=show.name, length=max_len, 
                new=newline, S=show.season, E=show.ep, 
                status=show.status if display_status else "")

    def print_shows_simple(self):
        try:
            print '\n'.join(map(str, self.get_all_shows()))
        except NoShowsException:
            print u'There are no shows!'
            return


