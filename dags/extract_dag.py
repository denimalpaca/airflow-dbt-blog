"""
### Extract DAG
Removes need for seed steps from dbt core example projects. The same csv's are stored in GCS and this DAG copies them to
snowflake

"""

from pendulum import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.empty import EmptyOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.utils.task_group import TaskGroup
from include.utils.team_args import args

args["owner"] = "01-EXTRACT"

with DAG(
    dag_id="extract_dag",
    start_date=datetime(2022, 11, 27),
    schedule="@daily",
    template_searchpath="/usr/local/airflow/include/extract_dag",
    doc_md=__doc__,
    catchup=False,
    default_args=args
) as dag:

    with TaskGroup(group_id="extracts") as extracts:
        for blob in ["raw_customers", "ad_spend", "customer_conversions", "raw_orders", "sessions", "raw_payments",
                     "subscription_periods"]:
            SnowflakeOperator(
                task_id=f"extract_{blob}",
                sql=f"sql/extract_{blob}.sql",
                params={
                    "schema_name": "demo",
                    "table_name": blob,
                },
            )

    finish = EmptyOperator(task_id="finish", outlets=[Dataset("DAG://EXTRACT_DAG")])

    extracts >> finish
