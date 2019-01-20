import sqlite3

class DBManager():

    def __init__(self, SQL_SERVER):

        # DATABASE (db.sqlite3)
        self.SQL_SERVER = SQL_SERVER
        # 'users' table
        self.SQL_USERS = 'users'
        self.USER_ID = 'user_id'
        self.RECENT_SEARCHES = 'recent_searches'
        # 'carparks' table
        self.SQL_CARPARKS = 'carparks'
        self.CARPARK_ID = 'carpark_id'
        self.ADDRESS = 'address'
        self.X_COORD = 'x_coord'
        self.Y_COORD = 'y_coord'

        # Try creating tables if not existed
        try:
            conn = sqlite3.connect(self.SQL_SERVER)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2})'.\
                format(tn=self.SQL_USERS, c1=self.USER_ID, t1='INTEGER', c2=self.RECENT_SEARCHES, t2='VARCHAR'))
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2}, {c3} {t3}, {c4} {t4})'.\
                format(tn=self.SQL_CARPARKS, c1=self.CARPARK_ID, t1='VARCHAR', c2=self.ADDRESS, t2='VARCHAR',
                c3=self.X_COORD, t3='FLOAT', c4=self.Y_COORD, t4='FLOAT'))
            conn.commit()
            conn.close()
        except FileNotFoundError:
            f = open(self.SQL_SERVER,'w+')
            f.close()
            conn = sqlite3.connect(self.SQL_SERVER)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2})'.\
                format(tn=self.SQL_USERS, c1=self.USER_ID, t1='INTEGER', c2=self.RECENT_SEARCHES, t2='VARCHAR'))
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2}, {c3} {t3}, {c4} {t4})'.\
                format(tn=self.SQL_CARPARKS, c1=self.CARPARK_ID, t1='VARCHAR', c2=self.ADDRESS, t2='VARCHAR',
                c3=self.X_COORD, t3='FLOAT', c4=self.Y_COORD, t4='FLOAT'))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error in opening: "+str(e))

    def recent_search(self, user_id):

        # First try of connecting sqlite database
        try:
            conn = sqlite3.connect(self.SQL_SERVER)
            c = conn.cursor()
        except Exception as e:
            print('Error DB:'+ str(e))
            return None
        # Get recent search input for a specific user from the database
        try:
            c.execute('SELECT {c2} FROM {tn} WHERE {c1}={user_id}'\
                .format(tn=self.SQL_USERS, c1=self.USER_ID, c2=self.RECENT_SEARCHES, user_id=user_id))
            all_rows = c.fetchone()[0]
            conn.close()
            return all_rows
        except sqlite3.DatabaseError as e:
            print('Error SELECT:'+str(e))
            return None
        except Exception as e:
            print("Error in getting data: "+str(e))
            return None
        return None


    def add(self, user_id, search_input):

        # First try of connecting sqlite database
        try:
            conn = sqlite3.connect(self.SQL_SERVER)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2})'.\
                format(tn=self.SQL_USERS, c1=self.USER_ID, t1='INTEGER', c2=self.RECENT_SEARCHES, t2='VARCHAR'))
        except FileNotFoundError:
            f = open(self.SQL_SERVER,'w+')
            f.close()
            conn = sqlite3.connect(self.SQL_SERVER)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2})'.\
                format(tn=self.SQL_USERS, c1=self.USER_ID, t1='INTEGER', c2=self.RECENT_SEARCHES, t2='VARCHAR'))
        except Exception as e:
            print("Error in opening: "+str(e))
            return False
        # Add the search input of a specific user to the database
        try:
            c.execute('SELECT EXISTS (SELECT {c1} from {tn} WHERE {c1} = {user_id})'\
                .format(tn=self.SQL_USERS, c1=self.USER_ID, user_id=user_id))
            is_existed = c.fetchone()[0]
            if is_existed:
                c.execute('SELECT {c2} FROM {tn} WHERE {c1}={user_id}'\
                    .format(tn=self.SQL_USERS, c1=self.USER_ID, c2=self.RECENT_SEARCHES, user_id=user_id))
                old_searches = c.fetchone()[0] # carpark_id
                old_searches = old_searches.split(',')
                if (search_input not in old_searches):
                    if (len(old_searches) >= 3):
                        old_searches.remove(old_searches[0])
                    old_searches.append(search_input)
                recent_searches = ','.join(old_searches)

                c.execute('UPDATE {tn} SET {c2} = "{recent_searches}" WHERE {c1} = {user_id}'\
                    .format(tn=self.SQL_USERS, c1=self.USER_ID, c2=self.RECENT_SEARCHES, user_id=user_id, recent_searches=recent_searches))
            else:
                c.execute('INSERT INTO {tn} VALUES ({user_id}, "{search_input}")'.\
                    format(tn=self.SQL_USERS, user_id=user_id, search_input=search_input))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print("Error in adding, ignoring: "+str(e))
            return False
        return False

    def is_existed(self, user_id):

        # First try of connecting sqlite database
        try:
            conn = sqlite3.connect(self.SQL_SERVER)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2})'.\
                format(tn=self.SQL_USERS, c1=self.USER_ID, t1='INTEGER', c2=self.RECENT_SEARCHES, t2='VARCHAR'))
        except FileNotFoundError:
            f = open(self.SQL_SERVER,'w+')
            f.close()
            conn = sqlite3.connect(self.SQL_SERVER)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({c1} {t1} PRIMARY KEY, {c2} {t2})'.\
                format(tn=self.SQL_USERS, c1=self.USER_ID, t1='INTEGER', c2=self.RECENT_SEARCHES, t2='VARCHAR'))
        except Exception as e:
            print("Error in opening: "+str(e))
            return False
        # Check if the specific user exists
        try:
            c.execute('SELECT EXISTS (SELECT {c1} from {tn} WHERE {c1} = {user_id})'\
                .format(tn=self.SQL_USERS, c1=self.USER_ID, user_id=user_id))
            is_existed = c.fetchone()[0]
            conn.commit()
            conn.close()
            return is_existed
        except Exception as e:
            print(e)
            return False

    def search_carpark(self,address):

        # First try of connecting sqlite database
        try:
            conn = sqlite3.connect(self.SQL_SERVER)
            c = conn.cursor()
            # Search for carparks that are matched with the user's input
            c.execute('SELECT * FROM {tn}'.format(tn=self.SQL_CARPARKS))
            allrows = c.fetchall()
            car_parks = []
            for row in allrows:
                if set(address.split()).union(set(row[1].split())) == set(row[1].split()):
                    car_parks.append(row)
            conn.commit()
            conn.close()
            return car_parks
        except Exception as e:
            print("Error in opening: "+str(e))
            return False
        return False