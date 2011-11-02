from optparse import OptionParser
from next.util import constants
from next.tui.tui import TUI
from next.show import admin
import ConfigParser
import os
import sys

def parse_opts():
    '''
    This method parses the commandline options to next, if any, and it parses
    the configuration file
    '''
    t = TUI()

    parser = OptionParser(usage=constants.USAGE)
    parser.add_option(u'-c', u'--conf', nargs=1, dest=u'new_path', 
            help=u'NEW_PATH specifies a different configuration file')
    parser.add_option(u'-r', u'--random', action="store_const", dest="func", const=t.do_random, help=u'Start an ep for a random show')
    parser.add_option(u'-l', u'--list', action="store_const", dest="func", const=t.do_list, help=u'List all your shows')
    parser.add_option(u'-n', u'--new', action="store_const", dest="func", const=t.do_new, help=u'List shows for which there are new eps on your system')
    parser.add_option(u'-u', u'--update', action="store_const", dest="func", const=t.do_update, help=u'Connect to the TVRage database and update your show information')
    parser.add_option(u'-a', u'--add', action="store_const", dest="func", const=t.do_add_show, help=u'Add a show to the database')
    parser.add_option(u'--add_location', action="store_const", dest="func", const=t.do_add_show_location, help=u'Add a location for a show to the database')
    parser.add_option(u'--change', action="store_const", dest="func", const=t.do_change_show, help=u'Change the current season and ep for a show')
    parser.add_option(u'--scan', action="store_const", dest="func", const=t.do_scan, help=u'Scan your series path for shows')
    (options, args) = parser.parse_args()

    path = os.path.expanduser(constants.CONF_PATH)
    if options.new_path:
        path = options.new_path

    config = ConfigParser.SafeConfigParser()
    if os.path.exists(path) and os.access(path, os.F_OK) and os.access(path, os.W_OK):
        config.read(path)
    else:
        print u'No configfile found in "{0}", generating default configfile. Please modify, then start next again!'.format(path)
        gen_example(path)
        sys.exit(-1)

    result = dict(config.items(u'general'))

    for (k, v) in result.items(): # make sure bools are parsed correct
        if 'false' == v.lower() or 'no' == v.lower() or '0' == v:
            result[k] = False
        if 'true' == v.lower() or 'yes' == v.lower() or '1' == v:
            result[k] = True

    t.conf = result

    return options, result, args

def gen_example(path):
    try:
        with open(path, 'w+') as conf:
            conf.write(constants.EXAMPLE_CONF)
    except:
        print 'Couldn\'t generate default configfile, path "{0}" is inaccessible!'.format(path)

