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
from include.utils.dbt_env import dbt_env_vars


DBT_PROJECT_DIR = "/usr/local/airflow/include/dbt"

with DAG(
    dag_id="dbt_manifest_create",
    start_date=datetime(2022, 7, 27),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    doc_md=__doc__,
    default_args={
        "owner": "00-PREP"
    }
) as dag:

    jaffle_shop_ls = BashOperator(
        task_id="jaffle_shop_manifest",
        bash_command=(
            f"dbt ls --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}/jaffle_shop"
        ),
        env=dbt_env_vars
    )

    mrr_playbook_ls = BashOperator(
        task_id="mrr_playbook_manifest",
        bash_command=(
            f"dbt deps --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}/mrr-playbook && \
             dbt ls --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}/mrr-playbook"
        ),
        env=dbt_env_vars
    )

    attribution_playbook = BashOperator(
        task_id="attribution_playbook_manifest",
        bash_command=(
            f"dbt ls --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}/attribution-playbook"
        ),
        env=dbt_env_vars
    )
