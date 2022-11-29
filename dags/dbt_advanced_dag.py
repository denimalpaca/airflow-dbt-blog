"""
Insert description here.

"""

from pendulum import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from include.utils.dbt_env import dbt_env_vars, dbt_cmd
from include.utils.dbt_dag_parser import DbtDagParser
from airflow.utils.task_group import TaskGroup


DBT_PROJECT_DIR = "/usr/local/airflow/include/dbt"

with DAG(
    dag_id="dbt_advanced_dag",
    start_date=datetime(2022, 11, 27),
    schedule_interval="@daily",
    doc_md=__doc__,
    catchup=False
) as dag:

    seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"{dbt_cmd} seed --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}",
        env=dbt_env_vars
    )

    with TaskGroup(group_id="dbt") as dbt:
        dag_parser = DbtDagParser(model_name="jaffle_shop", dbt_global_cli_flags="--no-write-json")

        dag_parser.dbt_run_group >> dag_parser.dbt_test_group


    seed >> dbt

