import sqlite3
from sqlite3 import Error

class Database:
    def __init__(self, db_file):
        self.connection = None
        try:
            self.connection = sqlite3.connect(db_file)
            self.create_tables()
        except Error as e:
            print(e)

    def create_tables(self):
        sql_users = """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        is_organizer INTEGER DEFAULT 0
                    );"""
        
        sql_events = """CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        date TEXT,
                        time TEXT
                    );"""
        
        sql_registrations = """CREATE TABLE IF NOT EXISTS registrations (
                                user_id INTEGER,
                                event_id INTEGER,
                                FOREIGN KEY (user_id) REFERENCES users (id),
                                FOREIGN KEY (event_id) REFERENCES events (id),
                                PRIMARY KEY (user_id, event_id)
                            );"""
        
        sql_notifications = """CREATE TABLE IF NOT EXISTS notifications (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                message TEXT,
                                FOREIGN KEY (user_id) REFERENCES users (id)
                            );"""
        
        cursor = self.connection.cursor()
        cursor.execute(sql_users)
        cursor.execute(sql_events)
        cursor.execute(sql_registrations)
        cursor.execute(sql_notifications)
        self.connection.commit()

    def add_user(self, user_id, username):
        sql = """INSERT OR IGNORE INTO users(id, username) VALUES(?,?)"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id, username))
        self.connection.commit()

    def is_organizer(self, user_id):
        sql = """SELECT is_organizer FROM users WHERE id=?"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0] == 1 if result else False

    def add_event(self, name, date, time):
        sql = """INSERT INTO events(name, date, time) VALUES(?,?,?)"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (name, date, time))
        self.connection.commit()
        return cursor.lastrowid

    def remove_event(self, event_id):
        sql = """DELETE FROM events WHERE id=?"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (event_id,))
        self.connection.commit()

    def get_all_events(self):
        sql = """SELECT id, name, date, time FROM events"""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def get_event(self, event_id):
        sql = """SELECT id, name, date, time FROM events WHERE id=?"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (event_id,))
        return cursor.fetchone()

    def register_user_to_event(self, user_id, event_id):
        sql = """INSERT INTO registrations(user_id, event_id) VALUES(?,?)"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id, event_id))
        self.connection.commit()

    def is_user_registered(self, user_id, event_id):
        sql = """SELECT 1 FROM registrations WHERE user_id=? AND event_id=?"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id, event_id))
        return cursor.fetchone() is not None

    def get_user_events(self, user_id):
        sql = """SELECT e.id, e.name, e.date, e.time 
                 FROM events e
                 JOIN registrations r ON e.id = r.event_id
                 WHERE r.user_id=?"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchall()

    def get_event_participants(self, event_id):
        sql = """SELECT u.id, u.username
                 FROM users u
                 JOIN registrations r ON u.id = r.user_id
                 WHERE r.event_id=?"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (event_id,))
        return cursor.fetchall()

    def get_event_participants_count(self, event_id):
        sql = """SELECT COUNT(*) FROM registrations WHERE event_id=?"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (event_id,))
        return cursor.fetchone()[0]

    def get_events_stats(self):
        sql = """SELECT e.name, COUNT(r.user_id)
                 FROM events e
                 LEFT JOIN registrations r ON e.id = r.event_id
                 GROUP BY e.id"""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def add_notification(self, user_id, message):
        sql = """INSERT INTO notifications(user_id, message) VALUES(?,?)"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id, message))
        self.connection.commit()

    def get_user_notifications(self, user_id):
        sql = """SELECT id, message FROM notifications WHERE user_id=?"""
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchall()

    def send_notification_to_all(self, message):
        sql = """SELECT id FROM users WHERE is_organizer=0"""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        users = cursor.fetchall()
        for user in users:
            self.add_notification(user[0], message)

def get_all_participants(self):
    """Возвращает список ID всех обычных участников (не организаторов)"""
    sql = """SELECT id FROM users WHERE is_organizer = 0"""
    cursor = self.connection.cursor()
    cursor.execute(sql)
    return [row[0] for row in cursor.fetchall()]


# ОТМЕНА ЗАПИСИ


def unregister_user_from_event(self, user_id, event_id):
    sql = """DELETE FROM registrations WHERE user_id=? AND event_id=?"""
    cursor = self.connection.cursor()
    cursor.execute(sql, (user_id, event_id))
    self.connection.commit()
    return cursor.rowcount > 0

