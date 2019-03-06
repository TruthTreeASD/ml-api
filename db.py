from sqlalchemy import create_engine
import os
import io
import pandas as pd


# psycopg2
print("Creating PSQL engine")
db_engine = create_engine(os.environ['DATABASE_URL'])
csv="database/state.csv"
table_name = "state"


def init_db():
    df = pd.read_csv(csv)
    df = df.dropna(axis=1)
    df.head(0).to_sql(table_name, db_engine, if_exists='replace',
                      index=False)  # truncates the table
    conn = db_engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    cur.copy_from(output, table_name, null="")  # null values become ''
    conn.commit()

if __name__ == '__main__':
    init_db()
