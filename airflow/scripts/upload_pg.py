import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from logging import Logger

# Load environment variables from the correct path
AIRFLOW_HOME = "/opt/airflow"
load_dotenv(os.path.join(AIRFLOW_HOME, ".env"))

# PostgreSQL connection string using pg8000
pg_user = os.getenv("POSTGRES_USER")
pg_password = os.getenv("POSTGRES_PASSWORD")
pg_host = os.getenv("POSTGRES_HOST")
pg_port = os.getenv("POSTGRES_PORT")
pg_database = os.getenv("POSTGRES_DATABASE")

engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}")

def upload_to_postgres(df: pd.DataFrame, table_name: str, primary_keys: list[str], logger: Logger):
    """
    Upload a dataframe to a PostgreSQL table using SQLAlchemy with psycopg2.
    Deletes rows with matching composite primary keys before inserting.
    """
    if not all(pk in df.columns for pk in primary_keys):
        raise ValueError("Some primary keys are missing from the dataframe.")

    conn = engine.connect()
    trans = conn.begin()

    try:
        # Build the list of unique composite keys as strings
        pk_tuples = df[primary_keys].drop_duplicates().values.tolist()

        def format_tuple(t):
            return "(" + ",".join(f"'{v}'" for v in t) + ")"

        tuple_str = ",".join([format_tuple(t) for t in pk_tuples])
        pk_clause = ",".join(primary_keys)

        delete_query = f"DELETE FROM {table_name} WHERE ({pk_clause}) IN ({tuple_str})"

        conn.exec_driver_sql(delete_query)

        df.to_sql(table_name, con=conn, if_exists='append', index=False)
        logger.info(f"[UPLOAD] to {table_name} ({len(df)} rows)")
        trans.commit()

    except SQLAlchemyError as e:
        logger.error(f"[ERROR] Upload failed: {e}")
        trans.rollback()
    finally:
        conn.close()
        engine.dispose()