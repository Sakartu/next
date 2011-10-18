class Show:
    def __init__(self, db_row):
        self.name = db_row[0]
        self.season = db_row[1]
        self.ep = db_row[2]
