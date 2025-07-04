import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="navi-bot",
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print("Tables:", tables)

cursor.execute("SELECT * FROM menu_item LIMIT 5")
print("Sample rows:", cursor.fetchall())

cursor.close()
conn.close()
