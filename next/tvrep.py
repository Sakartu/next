class Episode(object):
    '''
    This is a wrapper class around the episode information available in the
    TVRage database for a given episode.
    '''
    def __init__(self, sid, showname, season, epnum, title, airdate):
        self.sid = sid
        self.showname = showname
        self.season = int(season)
        self.epnum = int(epnum)
        self.title = title
        self.airdate = airdate

    @staticmethod
    def from_db_row(row):
        '''
        This static method can be used to create an Episode object from a
        database row
        '''
        return Episode(row[0], row[1], row[2], row[3], row[4], row[5])

    def __str__(self):
        return '{n} - s{s:02d}e{e:02d} - {t}'.format(
                n=self.showname, id=self.sid,  s=self.season, e=self.epnum,
                t=self.title)

    def __repr__(self):
        return str(self)

    def __cmp__(self, other):
        if type(self) != type(other):
            return 1

        if self.showname != other.showname:
            return 1

        if self.season == other.season:
            return self.epnum - other.epnum
        else:
            return self.season - other.season
