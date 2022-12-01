"""
>Insert description here.

"""

from pendulum import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.empty import EmptyOperator


with DAG(
    dag_id="load_dag_a",
    start_date=datetime(2022, 11, 27),
    schedule=[
        Dataset("DBT://STG_ORDERS"),
        Dataset("DBT://CUSTOMER_CHURN_MONTH")
    ],
    doc_md=__doc__,
    catchup=False,
    default_args={
        "owner": "03-LOAD"
    }
) as dag:

    EmptyOperator(task_id="reverse_etl")



