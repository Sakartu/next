class Show:
    def __init__(self, db_row):
        self.name = db_row[0]
        self.season = int(db_row[1])
        self.ep = int(db_row[2])
