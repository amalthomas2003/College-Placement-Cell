import pymysql
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "careerconnect",
    "database": "maindb"
}
connection = pymysql.connect(**db_config)
cursor = connection.cursor()
cursor.execute("DROP DATABASE IF EXISTS maindb")
connection.commit()
cursor.close()
connection.close()
print("Database successfully Deleted")