"""
### dbt_manifest_create
This DAG can be triggered as needed to re-create the manifest.json for the dbt models running in this environment

### Notes
This DAG uses the `dbt ls` command to generate a manifest.json file to be parsed. You can read more about the dbt
command [here](https://docs.getdbt.com/reference/commands/list)
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from include.utils.dbt_env import dbt_env_vars, dbt_cmd

DBT_PROJECT_DIR = "/usr/local/airflow/include/dbt"

with DAG(
    dag_id="dbt_manifest_create",
    start_date=datetime(2022, 7, 27),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    doc_md=__doc__,
    tags=["dbt"],
) as dag:

    BashOperator(
        task_id="dbt_ls_cmd",
        bash_command=(
            f"{dbt_cmd} ls --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}"
        ),
    )
