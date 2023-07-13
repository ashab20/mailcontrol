import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ashabu',
    'database': 'pymail'
}

def connect_db():
    return mysql.connector.connect(**db_config)

def execute_query(query, params=None):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()
