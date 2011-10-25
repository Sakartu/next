from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Show, TVRShow

class DB(object):
    def __init__(self, database):
        self.engine = create_engine(database, echo=False)
        self.metadata = Base.metadata
        self.session = sessionmaker(bind=self.engine)()
        self.create()

    def create(self):
        self.metadata.create_all(self.engine)

    def find_show(self, name):
        '''
        This method tries to find a show in the shows database using a wildcard
        search
        '''
        shows = self.session.query(Show).\
                filter(Show.name.like('%' + name + '%')).all()

        if not shows:
            print u'No shows found with that name, try again!'
            return None

        if len(shows) > 2:
            print u'''Found multiple shows with the same name, picking first\
            ({0})'''.format(show)

        return shows[0]

    def add_show(self, sid, name, season, ep, status):
        '''
        This method adds a show with a given sid, name, season and ep to the
        database
        '''
        show = Show(sid=sid, name=name, season=season, episode=ep, status=status)
        self.session.add(show)
        self.session.commit()

    def change_show(self, sid, season, ep):
        '''
        This method changes the season and ep of a given show in the database
        '''
        show = self.session.query(Show).filter(Show.sid == sid).one()
        show.season = season
        show.episode = episode
        self.session.add(show)
        self.session.commit()

    def all_shows(self):
        '''
        This method returns a list of Show objects for all the shows in the
        database
        '''
        return self.session.query(Show).all()

    def store_tvr_eps(eps):
        '''
        This method stores all the eps in the given eps list in the database
        '''
        for ep in eps:
            self.session.add(ep)
        self.session.commit()

    def find_seasons(self, sid):
        '''
        This method finds all the season numbers belonging to a given show
        '''
        return list(set(self.session.query(TVRShow.season).filter(TVRShow.sid == sid)))

    def find_all_eps(self, sid, season):
        '''
        This method returns all the eps, wrapped in Episode objects for a given
        show and season
        '''
        return self.session.query(TVRShow).filter(TVRShow.sid == sid,
                TVRShow.season == season)

    def find_ep(self, sid, season, ep):
        '''
        This method returns a single Episode object for the given show, season
        and epnumber
        '''
        return self.session.query(TVRShow).filter(TVRShow.sid == sid,
                TVRShow.season == season, TVRShow.episode == ep).one()

    def mark_maybe_finished(self, sid, value=True):
        '''
        This method marks the given show as maybe_finished
        '''
        show = self.session.query(Show).filter(Show.sid == sid).one()
        show.maybe_finished = 1 if value else 0
        self.session.add(show)
        self.session.commit()

    def mark_not_maybe_finished(self, sid):
        '''
        This method unmarks the show as maybe_finished
        '''
        self.mark_maybe_finished(sid, False)
