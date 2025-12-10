from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
from pendulum import timezone

default_args = {
    "owner": "hunganh1310",
    "start_date": datetime(2024, 4, 1, tzinfo=timezone("Asia/Ho_Chi_Minh")),
    "depends_on_past": False,
}

with DAG(
    dag_id="song_pipeline_workflow",
    default_args=default_args,
    schedule_interval="30 3 * * *",  # Runs at 03:30 AM daily (local time)
    catchup=False,
    tags=["fetch", "download", "song"],
) as dag:

    fetch_song = BashOperator(
        task_id="fetch_song",
        bash_command="cd /opt/airflow && python data_enrich.py"
    )

    download_song = BashOperator(
        task_id="download_song",
        bash_command="cd /opt/airflow && python upload_mp3.py"
    )

    fetch_song >> download_song