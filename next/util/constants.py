# exts shouldn't have dots!
VIDEO_EXTS = [u'mkv', u'avi', u'mpg', u'mpeg'] 
SUB_EXTS = [u'srt', u'sub', u'idx', u'ssa', u'ass']

SHOW_REGEXES = [
    r'(?P<show>{show}).*S0*(?P<season>{season})E0*(?P<ep>{ep})\D.*',  # accounts for most S12E12 type of shows
    r'(?P<show>{show}).*0*(?P<season>{season})x0*(?P<ep>{ep})\D.*'    # accounts for most 12x12 type of shows
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
    SHOW_PATH = u'show_path'
    PLAYER_CMD = u'player_cmd'
    UNSTRUCTURED = u'unstructured_mode'
    POSTPROCESSING = u'post_hook'
    LENGTH_DETECTION = u'length_detecion'
    FUNC_ARGS = u'func_args'
    ASK_ANOTHER = u'ask_another'

class TVRage:
    '''
    This enumeration class contains constants for all the xpath-like paths for
    tvrage results
    '''
    SEARCH_NAME = u'show/name'
    SEARCH_ID = u'show/showid'
    SEARCH_STATUS = u'show/status'

    STATUS_STATUS = u'status'

    EPLIST_NAME = u'name'
    EPLIST_SEASON = u'Episodelist/Season'
    EPLIST_SEASONNUM = u'no'
    EPLIST_EPISODE = u'episode'
    EPLIST_EPNUM = u'seasonnum'
    EPLIST_AIRDATE = u'airdate'
    EPLIST_TITLE = u'title'


EXAMPLE_CONF = '''[general]

# this option defines the path to your shows
show_path=~/downloads/series/

# set this option if you want your database to reside somewhere else
# database_path=~/downloads/series/

# this command is called by next when a show is to be played.
# the full path to the desired episode is placed at the end before calling
player_cmd=totem

# set this command to True if you have an unstructured series folder
# this is useful for people who just put all their new eps in 
# ~/downloads/ or something.
#unstructured_mode=False

# a comma-separated list of scripts to call after an ep is watched and the
# database is updated. The script will be called always when the database is
# updated. The arguments for the script can be the following:
# 'status'          The status of the show (Returning, Cancelled, etc) 
# 'name'            The name of the show
# 'season'          The season of the watched ep
# 'ep'              The episode number of the watched ep
# 'sid'             The TVRage show id
# 'path'            The absolute path to the watched ep
#
# They should be placed in curly braces. For example:
# post_hook=~/bin/test.py {path} {season} {ep}
# multiple scripts can be called by separating them with comma's:
# post_hook=~/bin/test.py {path},~/bin/test2.py {season} {ep}
# 
# The example below will delete the watched ep after a succesful watch.
#post_hook=/bin/rm {path}
'''
