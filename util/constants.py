CONF_PATH = '~/.next/next.conf'
VIDEO_EXTS = ['avi', 'mpg', 'mpeg', 'mkv']
SHOW_REGEXES = [r'.*S(\d{1,2)E(\d{1,2}).*']

USAGE = \
        """Usage: %prog [options] [show]

This program helps you in maintaining your episodes. It
will remember which eps you've already seen and start a
new named (or a new random) ep for you. The configuration
file for %prog can be found in ~/.%prog/
"""

class Keys:
    DB_PATH = 'database_path'
