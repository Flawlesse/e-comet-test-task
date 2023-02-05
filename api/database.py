from api.config import ENV
import psycopg2


def get_db_connection():
    connection = psycopg2.connect(
        database=ENV.get("POSTGRES_NAME"), 
        user=ENV.get("POSTGRES_USER"),
        password=ENV.get("POSTGRES_PASSWORD"), 
        host=ENV.get("HOST"), 
        port=ENV.get("PORT")
    )
    return connection
