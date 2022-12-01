"""
>Insert description here.

"""

from pendulum import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.bash_operator import BashOperator
from airflow.utils.task_group import TaskGroup
from include.utils.dbt_dag_parser import DbtDagParser
from include.utils.dbt_env import dbt_env_vars


DBT_PROJECT_DIR = "/usr/local/airflow/include/dbt"

with DAG(
    dag_id="mrr-playbook",
    start_date=datetime(2022, 11, 27),
    schedule=[Dataset("DAG://EXTRACT_DAG")],
    doc_md=__doc__,
    catchup=False,
    default_args={
        "owner": "02-TRANSFORM"
    }
) as dag:

    seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"source /usr/local/airflow/dbt_venv/bin/activate && \
        dbt seed --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}/mrr-playbook",
        env=dbt_env_vars
    )

    with TaskGroup(group_id="dbt") as dbt:
        dag_parser = DbtDagParser(
            model_name="mrr-playbook",
            dbt_global_cli_flags="--no-write-json"
        )

        dag_parser.dbt_run_group >> dag_parser.dbt_test_group


    seed >> dbt

