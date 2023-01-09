# Fivetran - dbt - Snowflake Pipeline

This is a modified version of the airflow-dbt-blog repository created by Chris Hronek at Astronomer. The main modifications are the use of OpenLineage and the `dbt-ol` command, and the use of a (for now) custom version of the `FivetranOperator` and `FivetranOperatorAsync`. Together, this provides an example use case for generating lineage across Fivetran and dbt into a Snowflake warehouse.

## Usage

To use this repo, create a .env file with the following entries:

- SNOWFLAKE_ACCOUNT
- SNOWFLAKE_USER
- SNOWFLAKE_PASSWORD
- ENV
- DBT_DATABASE
- DBT_WAREHOUSE
- OPENLINEAGE_URL # if not running on the Astro platform
- OPENLINEAGE_API_KEY # if not running on the Astro platform
- OPENLINEAGE_NAMESPACE # if not running on the Astro platform
- AIRFLOW__SECRETS__BACKEND
- AIRFLOW__SECRETS__BACKEND_KWARGS

If you are not using an Airflow secrets backend, ensure you have credentials properly set up for whichever backend your Fivetran pipeline ingests data from.

Start the project locally with `astro dev start`, provided you have the [Astro CLI](https://docs.astronomer.io/astro/cli/overview) installed, and enable the DAGs.
Manually trigger the unscheduled manifest DAG, then manually trigger or wait for the scheduled run of the extract DAG. 
