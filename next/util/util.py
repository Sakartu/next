import subprocess
import constants
import textwrap
import time
import sys
import re
import os

def print_formatted(msg):
    '''
    Helper method to print indented strings
    '''
    print textwrap.fill(textwrap.dedent(msg), 80)

def get_words(text):
    '''
    Utility function that splits a given text on spaces, dots and _'s, then
    returns only those parts which contain only word characters
    '''
    # filter out dots, underscores and multiple spaces
    text = re.sub('\s+', ' ', text.lower())
    text = re.sub('[\._]', ' ', text)
    # split on spaces
    words = text.split()
    # filter for only normal words (handy in case of "Doctor Who (2005)"
    return filter(lambda x : re.compile(r'^\w*$').match(x), words)

def play(command, show):
    '''
    A helper method that executes the given command
    '''
    # play the show
    print u'Starting S{S:02}E{E:02} of {name}!'.format(S=show.season, E=show.ep, name=show.name)
    try:
        print " ".join(command)
        subprocess.call(command)
        return True
    except KeyboardInterrupt:
        sys.stdout.flush()
        time.sleep(1) # give the movie player some time to clean up
        return True
    except OSError:
        # maybe the player isn't installed or something?
        print u'An error occurred while starting the player, check your config!'
        return False

def build_sub_path(path):
    '''
    A helper function to tell you whether subs are available for a given ep and
    if so, return the full path to the subtitle file
    '''
    if not path:
        return None
    (base, _) = os.path.splitext(path)
    for ext in constants.SUB_EXTS:
        sub_path = base + '.' + ext
        if os.path.exists(sub_path):
            return sub_path
    return None
