class Episode:
    def __init__(self, sid, showname, season, epnum, airdate, title):
        self.sid = sid
        self.showname = showname
        self.season = int(season)
        self.epnum = int(epnum)
        self.airdate = airdate
        self.title = title

    def __str__(self):
        return "{n} (sid {id}) - s{s:02d}e{e:02d} - {t}".format(n=self.showname, id=self.sid,  s=self.season, e=self.epnum, t=self.title)

    def __repr__(self):
        return str(self)

    def __cmp__(self, other):
        if type(self) != type(other):
            return 1

        if self.season == other.season:
            return self.epnum - other.epnum
        else:
            return self.season - other.season
