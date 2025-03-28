import mysql.connector
import dotenv

config = dotenv.dotenv_values(".env")

conn = mysql.connector.connect(
    host='localhost',
    user=config.get("DB_USER"),
    password=config.get("DB_PASS"),
    database="flask_db"
)

print("MySQL connection successful!")
conn.close()