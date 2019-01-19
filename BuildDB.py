import sqlite3

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2})'.\
    format(tn='carparks', c1='carpark_id', t1='VARCHAR', c2='address', t2='VARCHAR'))

file = open('hdb-carpark-information.csv', 'r')
data = file.readlines()

for i in range(1, len(data)):
    data[i] = data[i].split(',')
    print(data[i][0])
    print(data[i][1])
    c.execute('INSERT INTO {tn} VALUES ("{carpark_id}", "{address}")'.
        format(tn='carparks', carpark_id=data[i][0].strip('"'), address=data[i][1].strip('"')))

conn.commit()
conn.close() 