VIDEO_EXTS = [u'.avi', u'.mpg', u'.mpeg', u'.mkv'] #need to have .'s in front!

SHOW_REGEXES = [
    r'(?P<show>{show}).*S0*(?P<season>{season})E0*(?P<ep>{ep})\D.*',  #accounts for most S12E12 type of shows
    r'(?P<show>{show}).*0*(?P<season>{season})x0*(?P<ep>{ep})\D.*'    #accounts for most 12x12 type of shows
    ] 

USAGE = u"""Usage: next ([options] | [show])

This program helps you in maintaining your episodes. It will remember which eps
you've already seen and start a new named (or a new random) ep for you. The
configuration file for next can be found in ~/.config/next/. next uses the
TVRage database to search for information about shows but it can also be used
offline.  Make sure you update your database regularly, or next will not be
aware of new episodes!

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
    PLAYER_CMD = u'player_cmd'
    LOCATIONS = u'locations'
    UNSTRUCTURED = u'unstructured'

class TVRage:
    '''
    This enumeration class contains constants for all the xpath-like paths for
    tvrage results
    '''
    SEARCH_NAME = u'show/name'
    SEARCH_ID = u'show/showid'
    SEARCH_STATUS = u'show/status'

    STATUS_RETURNING = 'returning'
    STATUS_CANCELLED = 'cancelled'
    STATUS_UNKNOWN = 'unknown'

    EPLIST_NAME = u'name'
    EPLIST_SEASON = u'Episodelist/Season'
    EPLIST_SEASONNUM = u'no'
    EPLIST_EPISODE = u'episode'
    EPLIST_EPNUM = u'seasonnum'
    EPLIST_AIRDATE = u'airdate'
    EPLIST_TITLE = u'title'


EXAMLE_CONF = '''[general]

# set this option if you want your database to reside somewhere else
#database_path=~/downloads/series/

# this command is called by next when a show is to be played.
# the full path to the desired episode is placed at the end before calling
player_cmd=totem

[locations]
~/downloads/series=structured
'''
