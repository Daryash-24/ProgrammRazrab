import os
import psycopg2

# Настройка подключения
password_db = os.getenv('parol')
user_db = os.getenv('user')
database_db = os.getenv('database')
host_db = os.getenv('host')
conn = psycopg2.connect(
    host=host_db,
    database=database_db,
    user=user_db,
    password=password_db
)
cur = conn.cursor()

cur.execute("""
           CREATE TABLE IF NOT EXISTS operations (
               id SERIAL PRIMARY KEY,
               date DATE NOT NULL,
               sum NUMERIC NOT NULL,
               chat_id VARCHAR(50) NOT NULL,
               type_operation VARCHAR(50),
               comment TEXT
               
           )
       """)
cur.execute("""
           CREATE TABLE IF NOT EXISTS users (
               id SERIAL PRIMARY KEY,
               name VARCHAR(50) UNIQUE NOT NULL,
               chat_id VARCHAR(50) NOT NULL UNIQUE
           )
       """)
conn.commit()