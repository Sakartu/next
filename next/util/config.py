from optparse import OptionParser
from constants import USAGE, EXAMPLE_CONF, ConfKeys
from tui.tui import TUI
import ConfigParser
import os
import sys

try:
    from xdg import BaseDirectory
    have_xdg = True
except ImportError:
    have_xdg = False


def parse_opts():
    '''
    This method parses the commandline options to next, if any, and it parses
    the configuration file
    '''
    t, parser = build_parser()

    (options, args) = parser.parse_args()

    # Load a default config
    config = ConfigParser.SafeConfigParser()
    config.add_section(u'general')

    # Load the config override
    path = None
    if options.new_path:
        path = options.new_path
    elif have_xdg:
        path = BaseDirectory.load_first_config('next', 'next.conf')
        if not path:
            path = os.path.join(BaseDirectory.save_config_path('next'),
                    'next.conf')
    else:
        path = os.path.expanduser(u'~/.next/next.conf')

    # Generate a default configuration if required
    if not path or not os.path.exists(path):
        try:
            print((u'No configfile found in "{0}", generating default '
            'configfile. Please modify, then retart next!').format(path))
            gen_example(path)
        except:
            print(('Couldn\'t generate default configfile, path "{0}" is '
            'inaccessible!').format(path))
        sys.exit(-1)

    if path:
        config.read(path)

    # Set the database path
    if not config.has_option(u'general', ConfKeys.DB_PATH):
        # No override
        if have_xdg:
            db_path = BaseDirectory.save_data_path('next')
        else:
            db_path = config.get(u'general', ConfKeys.SHOW_PATH)
        config.set(u'general', ConfKeys.DB_PATH, db_path)

    # Check if DB_PATH is a dir or a file
    database_path = config.get(u'general', ConfKeys.DB_PATH)
    if not database_path.endswith('.db'):
        config.set(u'general', ConfKeys.DB_PATH,
        os.path.join(database_path, u'next.db'))

    result = dict(config.items(u'general'))

    for (k, v) in result.items():  # make sure bools are parsed correct
        if 'false' == v.lower() or 'no' == v.lower() or '0' == v:
            result[k] = False
        if 'true' == v.lower() or 'yes' == v.lower() or '1' == v:
            result[k] = True

    # put the remaining args in the conf
    result['func_args'] = args

    t.conf = result

    return options, result, args


def build_parser():
    '''
    Convenience method that builds an OptionParser based on a TUI object
    and returns both the TUI object and the OptionParser, in that order
    '''
    t = TUI()

    parser = OptionParser(usage=USAGE)

    # -c, --conf
    parser.add_option(u'-c',
    u'--conf',
    nargs=1,
    dest=u'new_path',
    help=u'NEW_PATH specifies a different configuration file')

    # -r, --random
    parser.add_option(u'-r',
    u'--random',
    action="store_const",
    dest="func",
    const=t.do_random,
    help=u'Start an ep for a random show')

    # -l, --list
    parser.add_option(u'-l',
    u'--list',
    action="store_const",
    dest="func",
    const=t.do_list,
    help=u'List all your shows with detailed information')

    # -n, --new
    parser.add_option(u'-n',
    u'--new',
    action="store_const",
    dest="func",
    const=t.do_new,
    help=u'List shows for which there are new eps on your system')

    # -u, --update
    parser.add_option(u'-u',
    u'--update',
    action="store_const",
    dest="func",
    const=t.do_update,
    help=u'Connect to the TVRage database and update your show information')

    # -a, --add
    parser.add_option(u'-a',
    u'--add',
    action="store_const",
    dest="func",
    const=t.do_add_show,
    help=u'Add a show to the database. If arguments are provided they will be '
    'used for a search, otherwise the user will be prompted.')

    # -d, --del, --rm
    parser.add_option(u'-d',
    u'--del',
    u'--rm',
    u'--remove',
    action="store_const",
    dest="func",
    const=t.do_del_show,
    help=u'Remove a show from the database. If arguments are provided they '
    'will be used as a show name, otherwise the user will be prompted.')

    # -f, --fix_subs
    parser.add_option(u'-f',
    u'--fix_subs',
    action="store_const",
    dest="func",
    const=t.do_fix_subs,
    help=u'Fix the subtitles for a given show. If arguments are provided they '
    'will be used as a show name, otherwise the user will be prompted.')

    # -s, --shows
    parser.add_option(u'-s',
    u'--shows',
    action="store_const",
    dest="func",
    const=t.print_shows_simple,
    help=u'Print a plain list of your shows')

    # --update_next
    parser.add_option(u'--update_next',
    action="store_const",
    dest="func",
    const=t.do_update_next,
    help=u'Update next to the latest version')

    # --add_location
    parser.add_option(u'--add_location',
    action="store_const",
    dest="func",
    const=t.do_add_show_location,
    help=u'Add a location for a show to the database. If arguments are '
    'provided they will be used as a show name, otherwise the user will be '
    'prompted.')

    # --change
    parser.add_option(u'--change',
    action="store_const",
    dest="func",
    const=t.do_change_show,
    help=u'Change the current season and ep for a show. If arguments are '
    'provided they will be used as a show name, otherwise the user will be '
    'prompted.')

    # --further
    parser.add_option(u'--further',
    action="store_const",
    dest="func",
    const=t.do_further_show,
    help=u'Further the current season and ep for a show. If arguments are '
    'provided they will be used as a show name, otherwise the user will be '
    'prompted.')

    # --scan
    parser.add_option(u'--scan',
    action="store_const",
    dest="func",
    const=t.do_scan,
    help=u'Scan your series path for shows')

    # --scan
    parser.add_option(u'--clean_db',
    action="store_const",
    dest="func",
    const=t.do_clean_db,
    help=u'Clean the tvrage cache of deleted shows')

    return t, parser


def gen_example(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w+') as conf:
        conf.write(EXAMPLE_CONF)
