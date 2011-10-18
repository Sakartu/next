from show import player
import db

def query_user(conf):
    options = [
            ("Play an ep",play_ep),
            ("Add show",add_show),
            ("Change show details",change_show),
            ("Scan series folder", scan_series),
            ("Quit", lambda x : True),
            ]
    print "What do you want to do? Press a number to select an option or press <enter> to play a random ep you haven't seen yet."
    for (i, k, _) in enumerate(options):
        print str(i + 1) + ".", k

    choice = get_input(possibles=range(1, len(options)+1))
    stop = options[choice][1](conf) #call the appropriate function
    if not stop:
        query_user(conf)

def play_ep(conf):
    print "An ep from which show?"
    name = get_input()
    s = db.find_show(conf['db_conn'], name)
    if s:
        player.play_next(conf, s)

def add_show(conf):
    try:
        print "Which show would you like to add?"
        showname = get_input()
        print "What season are you at for {0}?".format(showname)
        season = int(get_input(range(1, 100)))  #a hundread seasons max should be enough
        print "What ep are you in season {0}?".format(season)
        ep = int(get_input(range(1, 100)))  #a hundread eps max should be enough too
        db.add_show(conf, showname, season, ep)
    except:
        print "Something went wrong while adding the show, try again!"

def change_show(conf):
    try:
        print "Which show would you like to change?"
        showname = get_input()
        print "What season are you at for {0}?".format(showname)
        season = int(get_input(range(1, 100)))  #a hundread seasons max should be enough
        print "What ep are you in season {0}?".format(season)
        ep = int(get_input(range(1, 100)))  #a hundread eps max should be enough too
        db.change_show(conf, showname, season, ep)
    except:
        print "Something went wrong while changing the show, try again!"

def scan_series(conf):
    print "not implemented yet :)"
    
def get_input(possibles=None):
    if possibles != None and type(possibles) != type([]):
        possibles = None

    possibles = map(str, possibles)

    a = None
    while not a:
        inp = raw_input("next:$ ")
        if possibles != None and inp in possibles:
            a = inp
        elif possibles == None:
            a = inp
        else:
            print "Invalid command!"
    return a
