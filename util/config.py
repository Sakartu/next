from optparse import OptionParser
from util import constants
import ConfigParser
import os
import sys

def parse_opts():
    '''
    This method parses the commandline options to next, if any, and it parses
    the configuration file
    '''
    parser = OptionParser(usage=constants.USAGE)
    parser.add_option(u'-c', u'--conf', nargs=1, dest=u'new_path', help=u'NEW_PATH specifies a different configuration file')
    (options, args) = parser.parse_args()

    config = ConfigParser.SafeConfigParser()

    path = os.path.expanduser(constants.CONF_PATH)
    if options.new_path:
        path = options.new_path

    if os.path.exists(path) and os.access(path, os.F_OK) and os.access(path, os.W_OK):
        config.read(path)
    else:
        print u'No configfile found in "{0}", aborting!'.format(path)
        sys.exit(2)

    result = dict(config.items(u'general'))

    for (k, v) in result.items(): # make sure bools are parsed correct
        if 'false' == v.lower() or 'no' == v.lower() or '0' == v:
            result[k] = False
        if 'true' == v.lower() or 'yes' == v.lower() or '1' == v:
            result[k] = True
                

    return result, args
