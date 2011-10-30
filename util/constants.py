CONF_PATH = u'~/.next/next.conf'
VIDEO_EXTS = [u'.avi', u'.mpg', u'.mpeg', u'.mkv'] #need to have .'s in front!

SHOW_REGEXES = [
    r'.*S0*(?P<season>{season})E0*(?P<ep>{ep}).*',  #accounts for most S12E12 type of shows
    r'.*0*(?P<season>{season})x0*(?P<ep>{ep}).*'    #accounts for most 12x12 type of shows
    ] 

USAGE = u"""Usage: next ([options] | [show])

This program helps you in maintaining your episodes. It will remember which eps
you've already seen and start a new named (or a new random) ep for you. The
configuration file for next can be found in ~/.next/. next uses the TVRage
database to search for information about shows but it can also be used offline.
Make sure you update your database regularly, or next will not be aware of new
episodes!

next can be called either with an option or with words identifying a certain
show. Only one option can be used at a time, the last option counts, previous
options will be ignored
"""



class ConfKeys:
    '''
    This enumeration class contains constants for all the configuration keys
    '''
    DB_PATH = u'database_path'
    DB_CONN = u'db_conn'
    SHOW_PATH = u'show_path'
    PLAYER_CMD = u'player_cmd'
    UNSTRUCTURED = u'unstructured_mode'

class TVRage:
    '''
    This enumeration class contains constants for all the xpath-like paths for
    tvrage results
    '''
    SEARCH_NAME = u'show/name'
    SEARCH_ID = u'show/showid'

    EPLIST_NAME = u'name'
    EPLIST_SEASON = u'Episodelist/Season'
    EPLIST_SEASONNUM = u'no'
    EPLIST_EPISODE = u'episode'
    EPLIST_EPNUM = u'seasonnum'
    EPLIST_AIRDATE = u'airdate'
    EPLIST_TITLE = u'title'

EXAMLE_CONF = '''[general]

# this option defines the path to your shows
show_path=~/downloads/series/

# set this option if you want your database to reside somewhere else
#database_path=~/downloads/series/

# this command is called by next when a show is to be played.
# the full path to the desired episode is placed at the end before calling
player_cmd=totem

# set this command to True if you have an unstructured series folder
# this is useful for people who just put all their new eps in 
# ~/downloads/ or something.
# unstructured_mode=False
'''
