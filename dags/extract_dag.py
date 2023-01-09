"""
### Extract DAG
Removes need for seed steps from dbt core example projects. The same csv's are stored in GCS and this DAG copies them to
snowflake

"""

from pendulum import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.empty import EmptyOperator
from fivetran_provider_async.operators import FivetranOperatorAsync
from airflow.utils.task_group import TaskGroup
from include.utils.team_args import args

args["owner"] = "01-EXTRACT"
blobs = ["raw_customers", "ad_spend", "customer_conversions", "raw_orders", "sessions", "raw_payments", "subscription_periods"]
fivetran_connector_ids = [
    "pointy_reprise", "report_hopeful", "cropping_limitation",
    "efficacy_dearest", "cater_aristocratic", "smith_administrative",
    "nozzle_distension"
]

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
        for fivetran_connector_id in fivetran_connector_ids:
            FivetranOperatorAsync(
                task_id=f"extract_{fivetran_connector_id}",
                fivetran_conn_id="fivetran_default",
                connector_id=fivetran_connector_id,
                schedule_type="manual"
            )

    finish = EmptyOperator(task_id="finish", outlets=[Dataset("DAG://EXTRACT_DAG")])

    extracts >> finish
