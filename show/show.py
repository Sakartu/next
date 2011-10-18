def find_show(db_conn, show_name):
    c = db_conn.cursor()
    c.execute('SELECT * FROM shows WHERE name=?', show_name)
    pass

def play_next(show):
    pass
