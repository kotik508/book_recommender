from sqlalchemy import create_engine, text, inspect

DB_NAME = 'bookie'
DB_URL = 'postgresql://postgres:postgres@localhost/postgres'
TABLE_NAME = 'book'
books_populated = False
engine = create_engine(DB_URL)

check_database = text(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = :db_name")

count_rows_query = text(f"SELECT COUNT(*) FROM {TABLE_NAME}")

with engine.connect() as connection:
    result = connection.execute(check_database, {"db_name": DB_NAME})
    if result.fetchone():
        print(f"Database {DB_NAME} exists.")
    else:
        print(f"Database {DB_NAME} created.")

    inspector = inspect(engine)

    tables = inspector.get_table_names()


    if TABLE_NAME in tables:
        print('Table is in tables')
    else:
        print(tables)

    # if table_exists:
    #     row_count = connection.execute(count_rows_query).scalar()
    #     if row_count > 0:
    #         print(f"Table '{TABLE_NAME}' exists with {row_count} books present.")
    #         books_populated = True
    #     else:
    #         print(f"Table '{TABLE_NAME}' exists but is empty")
    # else:
    #     print(f"Table '{TABLE_NAME}' does not exist.")