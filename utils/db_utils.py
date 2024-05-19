import psycopg2
import os

def get_db_connection():
    # Get database credentials from environment variables
    db_name = "postgres"
    db_user = "postgres.kksffaorrtffzbawcmpx"
    db_password = "d-07-basdat"
    db_host = "aws-0-ap-southeast-1.pooler.supabase.com"
    db_port = "5432"
    
    # Establish a connection to the database
    connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    return connection