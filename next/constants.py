# exts shouldn't have dots!
VIDEO_EXTS = [u'mkv', u'avi', u'mpg', u'mpeg', u'mp4', u'mov']
SUB_EXTS = [u'srt', u'sub', u'idx', u'ssa', u'ass']

SHOW_REGEXES = [
    # accounts for most S12E12 type of shows
    r'(?P<show>{show}).*S0*(?P<season>{season})E0*(?P<ep>{ep})\D.*',

    # accounts for most 12x12 type of shows
    r'(?P<show>{show}).*0*(?P<season>{season})x0*(?P<ep>{ep})\D.*',
    ]


USAGE = u"""Usage: next ([options] | [show])

This program helps you in maintaining your episodes. It will remember which eps
you've already seen and start a new named (or a new random) ep for you. The
configuration file for next can be found in ~/.config/next/. next uses the
TVRage database to search for information about shows but it can also be used
offline. Make sure you update your database regularly, or next will not be
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
    BASE_DIR = u'base_dir'
    SHOW_PATH = u'show_path'
    PLAYER_CMD = u'player_cmd'
    UNSTRUCTURED = u'unstructured_mode'
    POSTPROCESSING = u'post_hook'
    LENGTH_DETECTION = u'length_detecion'
    FUNC_ARGS = u'func_args'
    ASK_ANOTHER = u'ask_another'
    CHECK_NEW_VERSION = u'check_new_version'
    AUTO_UPDATE_NEXT = u'auto_update_next'
    GIT_PATH = u'git_path'
    UPDATE_MANAGER = u'update_manager'


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


class GitHub:
    GITHUB_USER = u'Sakartu'
    GITHUB_REPO = u'next'
