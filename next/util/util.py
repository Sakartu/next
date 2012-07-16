import constants
import unicodedata
import textwrap
import os
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
    text = re.sub('\s+', ' ', text.lower(), re.U)
    text = re.sub('[\._]', ' ', text, re.U)
    # split on spaces
    words = text.split()
    # filter for only normal words (handy in case of "Doctor Who (2005)"
    filtered = map(lambda x: re.compile(r'\w*', re.U).search(x).group(0),
            words)
    return filtered


def normalize(wordlist):
    '''
    Utility function that goes over each word in the list and tries to
    normalize the words by 'un-unicoding' them
    '''
    return [unicodedata.normalize('NFKD', x).encode('ascii', 'ignore') for x in
            wordlist]


def shows_match(one, two, fuzzy=False):
    '''
    This method returns True if the names of the two shows provided as
    parameters look very much alike

    That is, if all the words that are in one are also in two when words that
    contain only of strange characters aren't counted
    '''
    if type(one) != type("") and type(one) != type(u""):  # assume type Show
        one = one.name.lower()
    if type(two) != type("") and type(two) != type(u""):  # assume type Show
        two = two.name.lower()
    one = one.lower()
    two = two.lower()
    ones = one.split()
    twos = two.split()
    for word in [x for x in ones if re.compile('^\w*$', re.U).match(x)]:
        if not fuzzy and word not in twos:  # use list of words
            return False
        elif fuzzy and word not in two:  # use whole string
            return False
    return True


def get_ep_details(filename, show='.*', season='\d{1,2}', ep='\d{1,2}',
        postfix=''):
    '''
    Helper method to get the epname, season and episode from a filename.
    Will use the provided show, season and ep as a filter, or not if not
    provided. A postfix can be added if necessary.
    '''
    rexes = []
    for rex in constants.SHOW_REGEXES:
        rexes.append(re.compile(rex.format(show=show, season=season, ep=ep) +
            postfix, re.U | re.I))
    for rex in rexes:  # try to find season and ep number
        m = rex.match(filename)
        if m:
            show, s, e = (m.group('show'), int(m.group('season')), 
                    int(m.group('ep')))
            return show, s, e
    return None, None, None


def get_scene_group(name):
    '''
    Helper method to retrieve the scene group name from a file
    Returns "" if no group can be found
    '''
    grp = ""
    if '-' in name:
        grp, _ = os.path.splitext(name[name.rfind('-'):])
    return grp


def get_new_sub_name(sub, vid):
    '''
    Helper method to return a tuple containing the current name and
    the new name of a sub file, given provided video file name.
    Returns a tuple containing (oldname, newname). Can handle paths
    as well as loose filenames
    '''
    vidname, _ = os.path.splitext(vid)
    subname, subext = os.path.splitext(sub)
    return (sub, vidname + subext)


def filter_shows(showlist, name):
    '''
    This method filters a given list of shows to provide the show which looks
    most like the given name.
    '''
    if not showlist or not name:
        return None

    matching = [x for x in showlist if shows_match(name, x, False)]
    if not matching:  # loosen matching rules a bit if no results are found
        matching = [x for x in showlist if shows_match(name, x, True)]

    return matching[0] if matching else None
