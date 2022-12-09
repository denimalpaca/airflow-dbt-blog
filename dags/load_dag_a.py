"""
>Insert description here.

"""

from pendulum import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.empty import EmptyOperator
from include.utils.team_args import args

args["owner"] = "03-LOAD"

with DAG(
    dag_id="load_dag_a",
    start_date=datetime(2022, 11, 27),
    schedule=[
        Dataset("DBT://JAFFLE_SHOP"),
        Dataset("DBT://MRR-PLAYBOOK")
    ],
    doc_md=__doc__,
    catchup=False,
    default_args=args
) as dag:

    EmptyOperator(task_id="reverse_etl")



