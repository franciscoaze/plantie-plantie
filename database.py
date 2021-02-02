import datetime
import psycopg2
import urllib.parse as up
from configuration.vars import DATABASE_URL

def insert_log(new_log):
    try:
        up.uses_netloc.append("postgres")
        url = up.urlparse(DATABASE_URL)
        connection = psycopg2.connect(database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port)
        cursor = connection.cursor()
        create_new_query = "CREATE TABLE IF NOT EXISTS LOGS (id SERIAL PRIMARY KEY, time TIMESTAMPTZ, type text,msg text);"
        cursor.execute(create_new_query)
        postgres_insert_query = """ INSERT INTO LOGS (TIME, TYPE, MSG) VALUES (%s,%s,%s)"""
        time = datetime.datetime.now().__str__()
        record_to_insert = (time, new_log['type'], new_log['msg'])
        # print(postgres_insert_query)
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()
        count = cursor.rowcount
        # print(count, "Record inserted successfully into logs table")
        success = True
    except (Exception, psycopg2.Error) as error :
        # print("Error while connecting to PostgreSQL", error)
        success = False
    finally:
        #closing database connection.
        if(connection):
            connection.close()
            # print("PostgreSQL connection is closed")

        return success
