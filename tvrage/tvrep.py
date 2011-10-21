class Episode:
    def __init__(self, showname, season, epnum, airdate, title):
        self.showname = showname
        self.season = int(season)
        self.epnum = int(epnum)
        self.airdate = airdate
        self.title = title

    def __str__(self):
        return "{n} - s{s:02d}e{e:02d} - {t}".format(n=self.showname, s=self.season, e=self.epnum, t=self.title)

    def __repr__(self):
        return str(self)
