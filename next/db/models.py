from sqlalchemy import create_engine, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import UniqueConstraint, Column
from sqlalchemy.types import Integer, Enum
from next.util.constants import TVRage

Base = declarative_base()

class Show(Base):
    __tablename__ = 'shows'

    sid = Column(Integer, primary_key=True)
    name = Column(Text)
    season = Column(Integer)
    episode = Column('ep', Integer)
    maybe_finished = Column(Integer, default=0)
    status = Column(Enum(TVRage.STATUS_RETURNING, TVRage.STATUS_CANCELLED, TVRage.STATUS_UNKNOWN))

    def __str__(self):
        return self.name

class TVRShow(Base):
    __tablename__ = 'tvr_shows'
    __table_args__  = (
            UniqueConstraint('sid', 'season', 'ep'),
            {},
            )

    sid = Column(Integer, primary_key=True)
    showname = Column(Text)
    season = Column(Integer)
    episode = Column('ep', Integer)
    title = Column(Text)
    airdate = Column(Text)

    def __str__(self):
        return '{n} (sid {id}) - s{s:02d}e{e:02d} - {t}'.format(n=self.showname, id=self.sid,  s=self.season, e=self.epnum, t=self.title)

    def __repr__(self):
        return str(self)

    def __cmp__(self, other):
        if type(self) != type(other):
            return 1

        if self.season == other.season:
            return self.epnum - other.epnum
        else:
            return self.season - other.season
