import psycopg2

def open_connection():
    conn = psycopg2.connect(database = "exambot", 
                        user = "postgres", 
                        host= 'localhost',
                        password = 'Muhammad_0010',
                        port = 5432)
    return conn


def close_connection(conn, cur):
    cur.close()
    conn.close()


def create_database_tables():
    conn = open_connection()
    cur = conn.cursor()
    cur.execute(
            """ CREATE TABLE IF NOT EXISTS Users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
    cur.execute("""
            CREATE TABLE IF NOT EXISTS JobListing (
                id SERIAL PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                company VARCHAR(100) NOT NULL,
                salary DECIMAL(10, 2),
                location VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT REFERENCES Users(id) ON DELETE CASCADE
            )"""
        )
    cur.execute("""
            CREATE TABLE IF NOT EXISTS Resume (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                skills TEXT,
                experience TEXT,
                desired_salary DECIMAL(10, 2),
                location VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT REFERENCES Users(id) ON DELETE CASCADE
            )
        """)
    conn.commit()
    close_connection(conn, cur)

create_database_tables()