"""
>Insert description here.
https://github.com/dbt-labs/jaffle_shop
"""

from pendulum import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.bash import BashOperator
from cosmos.providers.dbt.task_group import DbtTaskGroup

#from include.utils.dbt_dag_parser import DbtDagParser
from include.utils.dbt_env import dbt_env_vars
#from airflow.utils.task_group import TaskGroup
from include.utils.team_args import args


DBT_PROJECT_DIR = "/usr/local/airflow/include/dbt"

args["owner"] = "02-TRANSFORM"

with DAG(
    dag_id="jaffle_shop",
    start_date=datetime(2022, 11, 27),
    schedule=[Dataset("DAG://EXTRACT_DAG")],
    doc_md=__doc__,
    catchup=False,
    default_args=args
) as dag:

    jaffle_shop_group = DbtTaskGroup(
        group_id="jaffle_shop_group",
        dbt_project_name="jaffle_shop",
        dbt_root_path=f"{DBT_PROJECT_DIR}",
        dbt_args={
            "dbt_executable_path": "/usr/local/airflow/dbt_venv/bin/dbt-ol",
            "schema": "demo"
        },
        conn_id="snowflake_default",
        dag=dag
    )

    jaffle_shop_group

    """
    docs = BashOperator(
        task_id="dbt_docs",
        bash_command=f"dbt docs generate --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}/jaffle_shop",
        env=dbt_env_vars
    )
    
    run = BashOperator(
        task_id="dbt_run",
        bash_command=f"dbt-ol run --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}/jaffle_shop",
        env=dbt_env_vars,
        outlets=[Dataset("DBT://JAFFLE_SHOP")]
    )

    test = BashOperator(
        task_id="dbt_test",
        bash_command=f"dbt-ol test --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}/jaffle_shop",
        env=dbt_env_vars,
        outlets=[Dataset("DBT://JAFFLE_SHOP")]
    )
    """

    # with TaskGroup(group_id="dbt") as dbt:
    #     dag_parser = DbtDagParser(
    #         model_name="attribution-playbook",
    #         dbt_global_cli_flags="--no-write-json"
    #     )

    #docs >> run

