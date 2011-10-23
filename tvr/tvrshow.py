class Show:
    def __init__(self, db_row):
        self.sid = db_row[0]
        self.name = db_row[1]
        self.season = int(db_row[2])
        self.ep = int(db_row[3])
