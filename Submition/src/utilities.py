"""
Movies Database Constants
"""

import mysql.connector

MYSQL_HOST = "localhost"
MYSQL_PORT = 3305

MYSQL_DATABASE_NAME = "ahmadk1"

MYSQL_USER = "ahmadk1"
MYSQL_PASSWORD = "ahma50949"

def connect_mysql_server():
    """
    Connects to the mysql server
    """
    print("Connecting to MySQL")
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE_NAME
    )
