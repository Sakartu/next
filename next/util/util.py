import textwrap
import re

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

