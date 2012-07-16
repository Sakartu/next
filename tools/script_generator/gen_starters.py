#!/usr/bin/env python
from templates import LINUX, WINDOWS
import subprocess
import sys
import os


def main():
    args = sys.argv[1:]

    flavor = 'L'
    if '-w' in args:
        flavor = 'W'

    shows = subprocess.check_output(['../next.py', '-s'])

    try:
        os.makedirs('./scripts/')
    except:
        pass

    for s in shows.strip('\n \t').split('\n'):
        # pick a single, representing word for the show
        defining_name = max(s.lower().split(), key=len)
        if flavor == 'L':
            p = gen_linux(defining_name)
        else:
            p = gen_windows(defining_name)
        set_perms(p)


def gen_linux(name):
    path = os.path.join('./scripts/', name + '.sh')
    with open(path, 'w+') as f:
        f.write(LINUX.format(name=name))
    return path


def gen_windows(name):
    path = os.path.join('./scripts/', name + '.bat')
    with open(path, 'w+') as f:
        f.write(WINDOWS.format(name=name))
    return path


def set_perms(path):
    os.chmod(path, 0744)

if __name__ == '__main__':
    main()
