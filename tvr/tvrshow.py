class Show:
    '''
    This is a wrapper around show information coming from the TVRage database
    '''
    def __init__(self, db_row):
        self.sid = db_row[0]
        self.name = db_row[1]
        self.season = int(db_row[2])
        self.ep = int(db_row[3])
        self.maybe_finished = int(db_row[4])
