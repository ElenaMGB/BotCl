import sqlite3
from datetime import datetime

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  teacher TEXT,
                  date_time TEXT,
                  created_at TEXT)''')
    conn.commit()
    conn.close()

# Добавление записи
def add_appointment(user_id, teacher, date_time):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO appointments (user_id, teacher, date_time, created_at) VALUES (?, ?, ?, ?)",
              (user_id, teacher, date_time, created_at))
    conn.commit()
    conn.close()

# Получение записей пользователя
def get_user_appointments(user_id):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute("SELECT teacher, date_time FROM appointments WHERE user_id = ?", (user_id,))
    appointments = c.fetchall()
    conn.close()
    return appointments

# Получение всех записей (для админа)
def get_all_appointments():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute("SELECT user_id, teacher, date_time FROM appointments")
    appointments = c.fetchall()
    conn.close()
    return appointments
