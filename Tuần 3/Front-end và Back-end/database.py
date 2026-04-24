import mysql.connector


def ket_noi():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="quanlykham"
    )
