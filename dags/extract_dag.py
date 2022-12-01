"""
>Insert description here.

"""

from pendulum import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.empty import EmptyOperator


with DAG(
    dag_id="extract_dag",
    start_date=datetime(2022, 11, 27),
    schedule="@daily",
    doc_md=__doc__,
    catchup=False,
    default_args={
        "owner": "01-EXTRACT"
    }
) as dag:

    EmptyOperator(task_id="ingestion_workflow", outlets=[Dataset("DAG://EXTRACT_DAG")])

