from show import player, fs
from db import db
from exceptions import UserCancelled
import random
import sys

def query_user(conf):
    print_help(conf)

    stop = False
    while not stop:
        try:
            choice = get_input(possibles=[x for (x, _, _) in options])
            command = filter(lambda x : x[0] == choice, options)[0][2]
            stop = command(conf) #call the appropriate function
        except UserCancelled:
            print "User cancelled!"
        except KeyboardInterrupt:
            print "\nUser pressed ^C, exitting..."
            sys.exit(0)

def play_ep(conf):
    all_shows = db.all_shows(conf)
    if not all_shows:
        print "There are no shows to play!"
        return
    print "Which show would you like to play the next ep from?"
    print_shows(all_shows)
    number = int(get_input("Show number: ", range(1, len(all_shows) + 1)))
    showname = all_shows[number - 1].name

    s = db.find_show(conf, showname)
    if s:
        player.play_next(conf, s)

def play_random_ep(conf):
    all_shows = db.all_shows(conf)
    if not all_shows:
        print "There are no shows to play!"
        return
    s = db.find_show(conf, random.choice(all_shows).name)
    player.play_next(conf, s)

def add_show(conf):
    #find the show
    unlisted = fs.find_unlisted(conf)
    if not unlisted:
        print "There are no shows to add!"
        return
    print "Which show would you like to add?"
    for (i, show) in enumerate(unlisted):
        print "{0:3d}. {1}".format(i + 1, show)
    number = int(get_input("Show number: ", range(1, len(unlisted) + 1)))
    showname = unlisted[number - 1]
    add_show_details(conf, showname)

def add_show_details(conf, showname):
    #then the season in the show
    seasons = fs.find_seasons(conf, showname)
    if not seasons:
        print "There are no seasons for this show!"
        return
    print "What season are you at for {0} ({1}-{2})?".format(showname, min(seasons), max(seasons))
    season = int(get_input("Season: ", seasons.keys()))

    #then the ep in the season
    eps = fs.find_eps(conf, showname, seasons, season)
    if not eps:
        print "This season has no eps!"
        return
    print "What ep are you in season {0}?".format(season)
    for (k, v) in eps.items():
        print "{0:3d}. {1}".format(k, v)
    ep = int(get_input("Episode: ", eps.keys()))  #a hundread eps max should be enough too

    #and finally put everything in the database
    db.add_show(conf, showname, season, ep)
    print "Successfully added {0} to the database!".format(showname)

def change_show(conf):
    all_shows = db.all_shows(conf)
    if not all_shows:
        print "There are no shows to change!"
        return
    print "Which show would you like to change?"
    print_shows(all_shows)
    number = int(get_input("Show number: ", range(1, len(all_shows) + 1)))
    showname = all_shows[number - 1]

    #then the season in the show
    seasons = fs.find_seasons(conf, showname)
    if not seasons:
        print "There are no seasons for this show!"
        return
    print "What season are you at for {0} ({1}-{2})?".format(showname, min(seasons), max(seasons))
    season = int(get_input("Season: ", seasons.keys()))

    #then the ep in the season
    eps = fs.find_eps(conf, showname, seasons, season)
    if not eps:
        print "This season has no eps!"
        return
    print "What ep are you in season {0}?".format(season)
    for (k, v) in eps.items():
        print "{0:3d}. {1}".format(k, v)
    ep = int(get_input("Episode: ", eps.keys()))  #a hundread eps max should be enough too

    #and finally put everything in the database
    db.change_show(conf, showname, season, ep)
    print "Successfully changed details for {0}!".format(showname)

def scan_series(conf):
    unlisted = fs.find_unlisted(conf)
    if not unlisted:
        print "There are no shows to add!"
        return
    for (i, show) in enumerate(unlisted):
        print "Would you like to add {0}?".format(show)
        answer = get_input("Add [yes]? ")
        if 'y' in answer.lower() or answer == "":
            add_show_details(conf, show)

def list_shows(conf):
    all_shows = db.all_shows(conf)
    if not all_shows:
        print "There are no shows!"
        return
    print_shows(all_shows)

def get_input(term="next$ ", possibles=None):
    if possibles != None and type(possibles) != type([]):
        possibles = None

    if possibles != None:
        possibles = map(str, possibles)

    a = None
    while a == None:
        try:
            inp = raw_input(term)
        except EOFError:
            print ""
            raise UserCancelled

        if possibles != None and inp in possibles:
            a = inp
        elif possibles == None:
            a = inp
        else:
            print "Invalid command!"
    return a

def print_help(_):
    print "What do you want to do? Press a number to select an option or press <enter> to play a random ep you haven't seen yet."
    for (k, o, _) in options:
        print k + ":", o

def print_shows(shows):
    max_len = max(map(len, map(lambda x : x.name, shows))) + 3
    print "{id:3s}  {name:{length}s} Episode".format(id="", name="Show Name", length=max_len)
    for (i, show) in enumerate(shows):
        print "{id:3d}. {name:{length}s} s{S:>02d}e{E:>02d}".format(id=i + 1, name=show.name, length=max_len, S=show.season, E=show.ep)

#all the possible options for the tui, including shortcut and explanation
options = [
        ('p', "Play an ep",play_ep),
        ('r', "Play a random ep",play_random_ep),
        ('a', "Add show",add_show),
        ('c', "Change show details",change_show),
        ('s', "Scan series folder", scan_series),
        ('l', "List all shows", list_shows),
        ('h', "Print this help", print_help),
        ('q', "Quit", lambda x : True),
        ]
