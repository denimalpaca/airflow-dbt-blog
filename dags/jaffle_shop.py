"""
>Insert description here.
https://github.com/dbt-labs/jaffle_shop
"""

import os

from pendulum import datetime

from airflow import DAG
from airflow.datasets import Dataset
from cosmos.providers.dbt.task_group import DbtTaskGroup

from include.utils.team_args import args


args["owner"] = "02-TRANSFORM"

with DAG(
    dag_id="jaffle_shop",
    start_date=datetime(2022, 11, 27),
    schedule=[Dataset("DAG://EXTRACT_DAG")],
    doc_md=__doc__,
    catchup=False,
    default_args=args
) as dag:

    DbtTaskGroup(
        group_id="jaffle_shop_group",
        dbt_project_name="jaffle_shop",
        dbt_root_path=os.environ.get("DBT_DIR"),
        dbt_args={
            #"dbt_executable_path": "/usr/local/airflow/dbt_venv/bin/dbt-ol",
            "schema": "demo"
        },
        #conn_id="postgres_default",
        conn_id="snowflake_default",
        dag=dag,
    )
