import constants
import textwrap
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

def fix_subs(ep):
    pass
