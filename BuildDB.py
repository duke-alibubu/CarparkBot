import sqlite3

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2}, {c3} {t3}, {c4} {t4})'.\
    format(tn='carparks', c1='carpark_id', t1='VARCHAR', c2='address', t2='VARCHAR',
    c3='x_coord', t3='FLOAT', c4='y_coord', t4='FLOAT'))

file = open('hdb-carpark-information.csv', 'r')
data = file.readlines()

for i in range(1, len(data)):
    data[i] = data[i].strip('"')
    data[i] = data[i].split('","')
    c.execute('INSERT INTO {tn} VALUES ("{carpark_id}", "{address}", {x_coord}, {y_coord})'.
        format(tn='carparks', carpark_id=data[i][0], address=data[i][1],
                x_coord=data[i][2], y_coord=data[i][3]))

conn.commit()
conn.close() 