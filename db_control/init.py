import psycopg2
import os


def connect():
    connection = psycopg2.connect(
        host=os.environ['HOST'],
        port=os.environ['PORT'],
        user=os.environ['USER'],
        password=os.environ['PASSWORD'],
        database=os.environ['DATABASE'],
    )
    connection.autocommit = True
    return connection


def create():
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons
            (
                id serial NOT NULL PRIMARY KEY,
                chat_number varchar(15) NOT NULL UNIQUE,
                group varchar(12) NOT NULL
            );
        ''')
    connection.close()
