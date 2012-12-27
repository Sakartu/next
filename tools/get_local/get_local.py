#!/usr/bin/python -u

import os
import sys
import shutil
from collections import defaultdict

# Make sure we can import next libraries
file_base = os.path.abspath(os.path.dirname(__file__))
next_base = os.path.abspath(os.path.join(file_base, '..', '..'))
sys.path.append(next_base)

from next import util, db, config, fs


def main():
    if not sys.argv[1:]:
        usage()
        sys.exit(1)
    copy_from = sys.argv[1]
    if not os.path.isdir(copy_from):
        print(u'The provided remote path does not exist or isn\'t a '
              'directory!')
    (options, conf, args) = config.parse_opts([])
    db.connect(conf)
    if sys.argv[2:]:
        show_names = ' '.join(sys.argv[2:]).split(',')
        shows = []
        for show_name in show_names:
            show_name = show_name.strip()
            candidates = db.find_shows(conf, show_name)
            shows.append(util.filter_shows(candidates, show_name))
    else:
        shows = db.all_shows(conf)
    copy_to = get_local_dir(conf)
    for s in shows:
        sync(conf, s, copy_from, copy_to)
    print(u'All done!')


def sync(conf, show, copy_from, copy_to):
    print(u'Processing {0}'.format(show))
    next_season = show.season
    next_ep = show.ep
    to_copy = defaultdict(dict)
    while True:
        path = fs.build_ep_path(conf, show, next_season, next_ep)
        if not path:
            next_season += 1
            next_ep = 1
            # Try next season
            path = fs.build_ep_path(conf, show, next_season, next_ep)
        if path:
            to_copy[next_season][next_ep] = path
            next_ep += 1
        else:
            break
    if not to_copy:
        print(u'Nothing to copy, proceding with next show!')
        return

    print(u'Episode tree built, proceeding with sync')
    new_show_path = os.path.join(copy_to, str(show))
    for season in to_copy:
        season_path = os.path.join(new_show_path, 'Season {0:02d}'.format(season))
        if not os.path.exists(season_path):
            os.makedirs(season_path)
        for epnum in to_copy[season]:
            copy_from = to_copy[season][epnum]
            print(u'Copying {0}... '.format(copy_from))
            shutil.copy2(copy_from, season_path)
            try:
                subfile = os.path.splitext(copy_from)[0] + '.srt'
                shutil.copy2(subfile, season_path)
            except IOError:
                print(u'Could not copy subtitle, maybe it doesn\'t exist?')
    print(u'Show done!')


def get_local_dir(conf):
    '''
    Utility function which will find out which local directory the user want's
    his new eps in
    '''
    local_dir = ''
    bases = fs.get_bases(conf)
    if not bases:
        print(u'No show directories are configured, have you setup next '
              'correctly?')
        sys.exit(1)
    if len(bases) > 1:
        print(u'Which of the local show directories do you want to put the eps'
              ' in?')
        for i, base in enumerate(bases):
            print(u'{0:2d}. {1}'.format(i + 1, base))
        answer = ''
        while not answer.isdigit():
            answer = raw_input(u'Please enter directory number: ')
        local_dir = bases[int(answer) - 1]
    else:
        local_dir = bases[0]
    print(u'Episodes will be put in {0}'.format(local_dir))
    return local_dir


def usage():
    print(u'Usage:')
    print(u'{0} <path where shows are> [showname]'.format(sys.argv[0]))
    print
    util.print_formatted(u'''\
          This program will copy all eps for a show from a remote mounted
          location to your local show directory. It will use the next database
          to find out which ep you are at and only copy eps that you haven\'t
          seen yet. It will copy the episodes in a directory structure as
          such:''')
    print(u'<local show dir>/<Show name>/Season <Show season>/<Episode>')
    util.print_formatted(u'''\
            For instance, season 1 episode 1 of Doctor Who (2005) will be
            copied as such:''')
    print(u'/show/path/Doctor Who (2005)/Season 01/Doctor.Who.2005.S01E01.avi')
    print
    print(u'It has two arguments:')
    print
    util.print_formatted(u'''\
          <path where shows are> which defines the path to the remote mounted
          location. This can be any locally mounted remote directory, such as
          sshfs, nfs or samba.''')
    print
    util.print_formatted(u'''\
          <shownames> which defines the names of the shows you want to copy to
          your local path. You can define multiple shows by separating them
          with commas. You can use spaces as all remaining arguments will be
          used together. If you don't fill this parameter, {0} will copy all
          your shows'''.format(sys.argv[0]))


if __name__ == '__main__':
    main()
